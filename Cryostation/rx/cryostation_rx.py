import rx
import numpy
import time

from .commands_bunched import *
from .bunch import *

def observe_periodic_value(cryostation_socket, action, sample_rate_ms = 1000):
    """
    Returns an observer that periodically samples a float yielding Cryostation command
    :param cryostation_socket: TCP socket to the Cryostation. This should not be closed
        while this observer is hot
    :param action: a function that takes a socket to the Cryostation as an
        argument and returns a Bunch with the values of interest in a named attribute.
        Will accept a list of functions rather than a single function. The functions
        will be executed in the sequence they appear in the list.
    :param sample_rate_ms: The sample rate in milliseconds, defaults to 1000ms
    :return: rx.Observable that yields a Bunch with attributes start_time and delta_time
    in seconds. The timing bunch is joined with the Bunch returned by action
    """

    if isinstance(action, list):
        action = join_list([a() for a in action])

    def update_value(previous, n):
        timing = Bunch(start_time=previous.start_time,
                     delta_time=time.clock() - previous.start_time)
        return timing.join(action(cryostation_socket))

    init_timing = Bunch(start_time=time.clock(),
                        delta_time=0)
    return rx.Observable.timer(0, sample_rate_ms)\
        .scan(update_value, init_timing.join(action(cryostation_socket)))

def observe_periodic_user_temperature(cryostation_socket, sample_rate_ms = 1000):
    return observe_periodic_value(cryostation_socket, get_user_temperature, sample_rate_ms)

def observe_periodic_platform_temperature(cryostation_socket, sample_rate_ms = 1000):
    return observe_periodic_value(cryostation_socket, get_platform_temperature, sample_rate_ms)

def observe_periodic_sliding_buffer(cryostation_socket, action, sample_rate_ms = 1000, buffer_length = 100):
    return observe_periodic_value(cryostation_socket, action, sample_rate_ms)\
        .buffer_with_count(buffer_length, 1)

def concat_temperature_and_stability_slopes(buffer_window,
                                     temperature_source=Temperature_Source.platform,
                                     stability_source=Stability_Source.platform):
    times = [x.delta_time for x in buffer_window]
    temps = [getattr(x, temperature_source) for x in buffer_window]
    stabs = [getattr(x, stability_source) for x in buffer_window]
    stab_slope = numpy.polyfit(time, stabs, 1)[0]
    temp_slope = numpy.polyfit(time, temps, 1)[0]
    stability = numpy.mean(stabs)
    temperature = getattr(buffer_window[-1], temperature_source)
    return Bunch(temperature_slope=temp_slope/temperature,
                 stability_slope=stab_slope/stability,
                 stability_mean=stability)

def concat_is_stable(value, temperature_slope_threshold=5e-3,
              stability_slope_threshold=5e-3,
              max_stability=0.1):
    return value.join(Bunch(is_stable=(value.temperature_slope > temperature_slope_threshold)\
           and (value.stability_slope > stability_slope_threshold)\
           and value.stability_mean < max_stability))

def observe_periodic_is_temperature_stable(cryostation_socket, set_point, action,
                                           temperature_source=Temperature_Source.platform,
                                           stability_source=Stability_Source.platform,
                                           window=100):
    def concat_stability(buffer):
        concat_is_stable(
            concat_temperature_and_stability_slopes(buffer,
                                                    temperature_source,
                                                    stability_source)
        )
    return observe_periodic_sliding_buffer(cryostation_socket, action,1000, window)\
        .select(concat_stability)

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
    return observe_periodic_is_temperature_stable(cs, set_point,
                                                  [get_user_temperature_b(cs),
                                                   get_user_stability_b(cs)],
                                                  Temperature_Source.user,
                                                  Stability_Source.user, 30)\
        .take_while(lambda x: not x.is_stable)