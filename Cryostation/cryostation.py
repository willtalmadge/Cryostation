import socket
import rx
import numpy
import time


from multiprocessing import Process, freeze_support

"""
Utility functions for communicating with the Cryostation over TCP/IP.
A socket should be opened with open_cryostation before using any of the
communication functions
"""

def open_cryostation(hostname, port=7773):
    cryostation_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cryostation_socket.connect((hostname, port))
    return cryostation_socket

def send_cmd(cryostation_socket, cmd):
    l = len(cmd)
    cryostation_socket.send(("%.2d%s" % (l, cmd)).encode('ascii'))

def send_cmd_with_float(cryostation_socket, cmd, arg):
    send_cmd(cryostation_socket, cmd + " " + ("%.6e" % arg))

def recv_response(cryostation_socket):
    response = cryostation_socket.recv(1024)
    l = int(response[0:2])
    return response[2:2+l]

def query(cryostation_socket, cmd):
    send_cmd(cryostation_socket, cmd)
    return recv_response(cryostation_socket)

def query_with_float(cryostation_socket, cmd, arg):
    send_cmd_with_float(cryostation_socket, cmd, arg)
    return recv_response(cryostation_socket)

"""
Cryostation commands. Call open_cryostation and pass in the returned
socket before calling these functions. See the Cryostation command
documentation for detailed descriptions of what these commands do.
"""

def get_alarm_state(cryostation_socket):
    response = query(cryostation_socket, "GAS")
    return True if response == "T" else False

def get_chamber_pressure(cryostation_socket):
    response = query(cryostation_socket, "GCP")
    return float(response)

def get_user_stage_temperature_setpoint(cryostation_socket):
    response = query(cryostation_socket, "GHTSP")
    return float(response)

def get_platform_temperature(cryostation_socket):
    response = query(cryostation_socket, "GPT")
    return float(response)

def get_platform_stability(cryostation_socket):
    response = query(cryostation_socket, "GPS")
    return float(response)

def get_user_temperature(cryostation_socket):
    response = query(cryostation_socket, "GUT")
    return float(response)

def get_user_stability(cryostation_socket):
    response = query(cryostation_socket, "GUS")
    return float(response)

def set_temperature_setpoint(cryostation_socket, temperature_setpoint):
    query_with_float(cryostation_socket, "STSP", temperature_setpoint)

def set_user_stage_setpoint(cryostation_socket, temperature_setpoint):
    query_with_float(cryostation_socket, "SHTSP", temperature_setpoint)

def start_cool_down(cryostation_socket):
    query(cryostation_socket, "SCD")

def start_warm_up(cryostation_socket):
    query(cryostation_socket, "SWU")

def start_standby(cryostation_socket):
    query(cryostation_socket, "SSB")

"""
Reactive Cryostation functions
"""

def observe_periodic_value(cryostation_socket, action, sample_rate_ms = 1000):
    """
    Returns an observer that periodically samples a float yielding Cryostation command
    :param cryostation_socket: TCP socket to the Cryostation. This should not be closed
        while this observer is hot
    :param action: an action that takes a socket to the Cryostation as an
        argument and returns a float
    :param sample_rate_ms: The sample rate in milliseconds, defaults to 1000ms
    :return: rx.Observable that yields a (start time(sec), delta time(sec), value) tuple
    """
    def update_value(accum, n):
        return (accum[0], time.clock() - accum[0], action(cryostation_socket))
    return rx.Observable.timer(0, sample_rate_ms)\
        .scan(update_value, (time.clock(), 0, action(cryostation_socket)))

def observe_periodic_user_temperature(cryostation_socket, sample_rate_ms = 1000):
    return observe_periodic_value(cryostation_socket, get_user_temperature, sample_rate_ms)

def observe_periodic_platform_temperature(cryostation_socket, sample_rate_ms = 1000):
    return observe_periodic_value(cryostation_socket, get_platform_temperature, sample_rate_ms)

def observe_periodic_sliding_buffer(cryostation_socket, action, sample_rate_ms = 1000, buffer_length = 100):
    return observe_periodic_value(cryostation_socket, action, sample_rate_ms)\
        .buffer_with_count(buffer_length, 1)

def observe_periodic_is_user_temperature_stable(cryostation_socket, set_point, window=100):
    def is_stable(values):
        time = [values[i][1] for i in range(window)]
        temps = [values[i][2][0] for i in range(window)]
        stabs = [values[i][2][1] for i in range(window)]
        slope = numpy.polyfit(time, stabs, 1)[0]
        stability = numpy.mean(stabs)
        last_temp_err = abs(set_point - values[-1][2][0])
        print("Temp, Stability (K): %f, %f" % (values[-1][2][0], stability))
        print("Slope: %f" % (slope/stability))
        return (last_temp_err <= stability) \
               and (abs(slope/stability) < 5e-3) \
               and (stability < 0.1)

    def temp_and_stability(x):
        return (get_user_temperature(cryostation_socket),
                get_user_stability(cryostation_socket))
    return observe_periodic_sliding_buffer(cryostation_socket,
                                    temp_and_stability,
                                    1000, window)\
        .select(is_stable)

def set_user_temperature_and_observe_stability(cs, set_point):
    print("Temperature set to %f" % set_point)
    if set_point < 40.0:
        ts =  set_point
        us = 3.0
    else:
        ts = 0.967*set_point
        us = set_point
    set_temperature_setpoint(cs,ts)
    set_user_stage_setpoint(cs, us)
    return observe_periodic_is_user_temperature_stable(cs, set_point, 30)\
        .take_while(lambda x: not x)\

def main():
    cs = open_cryostation("Cryostation-127")
    observe_periodic_user_temperature(cs)\
        .take(4)\
        .finally_action(lambda:cs.close())\
        .subscribe(lambda T: print("%f" % T))

if __name__ == '__main__':
    cs = open_cryostation("Cryostation-127")
    set_user_temperature_and_observe_stability(cs, 5)\
        .last()\
        .do_action(lambda x: print("action"))\
        .subscribe(lambda x: print("stable"))