from enum import Enum

from cryostation.rx.bunch import Bunch
from cryostation import *

class Stability_Source(Enum):
    sample = 'sample_stability'
    platform = 'platform_stability'
    user = 'user_stability'
class Temperature_Source(Enum):
    sample = 'sample_temperature'
    platform = 'platform_stability'
    user = 'user_stability'

def get_alarm_state_b(cryostation_socket):
    return Bunch(alarm_state=get_alarm_state(cryostation_socket))

def get_chamber_pressure_b(cryostation_socket):
    return Bunch(chamber_pressure=get_chamber_pressure(cryostation_socket))

def get_user_stage_temperature_setpoint_b(cryostation_socket):
    return Bunch(user_stage_temperature_setpoint=get_user_stage_temperature_setpoint(cryostation_socket))

def get_platform_heater_power_b(cryostation_socket):
    return Bunch(platform_heater_power=get_platform_heater_power(cryostation_socket))

def get_pid_fi_b(cryostation_socket):
    return Bunch(pid_fi=get_pid_fi(cryostation_socket))

def get_pid_ki_b(cryostation_socket):
    return Bunch(pid_ki=get_pid_ki(cryostation_socket))

def get_pid_td_b(cryostation_socket):
    return Bunch(pid_td=get_pid_td(cryostation_socket))

def get_platform_temperature_b(cryostation_socket):
    return Bunch(platform_temperature=get_platform_temperature(cryostation_socket))

def get_platform_stability_b(cryostation_socket):
    return Bunch(platform_stability=get_platform_stability(cryostation_socket))

def get_stage_1_heater_power_b(cryostation_socket):
    return Bunch(stage_1_heater_power=get_stage_1_heater_power(cryostation_socket))

def get_stage_1_temperature_b(cryostation_socket):
    return Bunch(stage_1_temperature=get_stage_1_temperature(cryostation_socket))

def get_stage_2_temperature_b(cryostation_socket):
    return Bunch(stage_2_temperature=get_stage_2_temperature(cryostation_socket))

def get_sample_stability_b(cryostation_socket):
    return Bunch(sample_stability=get_sample_stability(cryostation_socket))

def get_sample_temperature_b(cryostation_socket):
    return Bunch(sample_temperature=get_sample_temperature(cryostation_socket))

def get_platform_temperature_setpoint_b(cryostation_socket):
    return Bunch(platform_temperature_setpoint=get_platform_temperature_setpoint(cryostation_socket))

def get_user_temperature_b(cryostation_socket):
    return Bunch(user_temperature=get_user_temperature(cryostation_socket))

def get_user_stability_b(cryostation_socket):
    return Bunch(user_stability=get_user_stability(cryostation_socket))

