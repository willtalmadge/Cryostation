import cryostation.rx as c

def print_progress(x):
    print("Temp, stability: %f, %f" % (x.user_temperature, x.user_stability))
    print("Slopes: %f, %f" % (x.temperature_slope, x.stability_slope))
cs = c.open_cryostation("Cryostation-127")
c.set_user_temperature_and_observe_stability(cs, 5.0).subscribe(on_next=print_progress, on_completed=lambda:cs.close())