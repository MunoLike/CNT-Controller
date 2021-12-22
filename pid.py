from datetime import datetime

MAX_OUT = 4095  # 12bit d/a converter
Kp = 0
Ki = 0
Kd = 0
pp = 0
pi = 0
pd = 0
prev_time = None
prev_error = 0


def init():
    global prev_time
    prev_time = datetime.Now()


# pid controller
def PID(current_flowrate, target_flowrate):
    global Kp, Ki, Kd, pp, pi, pd, prev_time, prev_error

    dt = (datetime.Now() - prev_time).total_seconds() * 1000  # [ms]

    error = target_flowrate - current_flowrate
    pp = Kp * error
    pi += Ki * error * dt
    pd = Kd * (error - prev_time) / dt

    prev_error = error

    u = pp + pi + pd
    if u > MAX_OUT:
        u = MAX_OUT
    if u < 0:
        u = 0
    
    print("control val: ", u)
