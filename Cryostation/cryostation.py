import socket

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

"""
Get commands, retrieve parameters and return them. Functions with a _b
suffix return bundles (named tuples) that can be joined in reactive programming
stream transformers.
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
    
def get_platform_heater_power(cryostation_socket):
    response = query(cryostation_socket, "GPHP")
    return float(response)
    
def get_pid_fi(cryostation_socket):
    response = query(cryostation_socket, "GPIDF")
    return float(response)
    
def get_pid_ki(cryostation_socket):
    response = query(cryostation_socket, "GPIDK")
    return float(response)
    
def get_pid_td(cryostation_socket):
    response = query(cryostation_socket, "GPIDT")
    return float(response)

def get_platform_temperature(cryostation_socket):
    response = query(cryostation_socket, "GPT")
    return float(response)

def get_platform_stability(cryostation_socket):
    response = query(cryostation_socket, "GPS")
    return float(response)

def get_stage_1_heater_power(cryostation_socket):
    response = query(cryostation_socket, "GS1HP")
    return float(response)
    
def get_stage_1_temperature(cryostation_socket):
    response = query(cryostation_socket, "GS1T")
    return float(response)
    
def get_stage_2_temperature(cryostation_socket):
    response = query(cryostation_socket, "GS2T")
    return float(response)
    
def get_sample_stability(cryostation_socket):
    response = query(cryostation_socket, "GSS")
    return float(response)
    
def get_sample_temperature(cryostation_socket):
    response = query(cryostation_socket, "GST")
    return float(response)
    
def get_platform_temperature_setpoint(cryostation_socket):
    response = query(cryostation_socket, "GTSP")
    return float(response)
    
def get_user_temperature(cryostation_socket):
    response = query(cryostation_socket, "GUT")
    return float(response)

def get_user_stability(cryostation_socket):
    response = query(cryostation_socket, "GUS")
    return float(response)
    
"""
Set commands, perform some action on the cryostat state or behavior
"""

def reset_pid_parameters(cryostation_socket):
    query(cryostation_socket, "RPID")
    
def start_cooldown(cryostation_socket):
    query(cryostation_socket, "SCD")

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