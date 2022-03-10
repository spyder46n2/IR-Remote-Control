from machine import UART, Pin
from time import sleep_us, time_ns
import select

# UART Init for reading IR sensor.
# Uses Pin GP 17 for UART RX
# Also GP 1, 7, 12, or 22 can be used
ir_rx = 17
uartZero = UART(0, baudrate=2400, rx=Pin(ir_rx))

# IR defs
up_bytes         = b'\xcbK{{\xcfOK\xcb{\xcf\xcf\xff'
down_bytes       = b'\xcbK{{\xcf\xcfOK\xcb\xcf\xcf\xcf'
cont_1_bytes     = b'\x00\xff'
cont_2_bytes     = b'\xff\x00'
cont_3_bytes     = b'\xff'
cont_4_bytes     = b'\x00'
power_bytes      = b'\xcbK{{\xcfO{K\xcf{\xcf\xff'
hdmi_power_bytes = b'KK\xcf\xcf\xcfOOO{\xcf{\xcf'
hdmi_arc_bytes   = b'KK\xcf\xcf\xcfO\xcf\xcfKK\xcf\xcf'
hdmi_1_bytes     = b'KK\xcf\xcf\xcfOKK\xcf\xcf\xcf\xcf'
hdmi_2_bytes     = b'KK\xcf\xcf\xcfOOK\xcb\xcf\xcf\xcf'
hdmi_3_bytes     = b'KK\xcf\xcf\xcfO{K\xcf{\xcf\xcf'
hdmi_4_bytes     = b'KK\xcf\xcf\xcfO\xcfK{{\xcf\xcf'
one_dot          = b'\xcbK{{\xcfO\xcb\xcf{\xcfK\xff'
two_dot          = b'\xcbK{{\xcf\xcfK\xcf\xcb\xcfK\xff'
three_dot        = b'\xcbK{{\xcf\xcfO{K\xcf\xcb\xff'
four_dot         = b'\xcbK{{\xcf\xcfK\xcf\xcb\xcfO\xcf'

# Flashy Flashy - onboard LED
flashy = Pin(25, Pin.OUT)

# Power Relay
power_relay = Pin(5, Pin.OUT)

# Stepper Pins
in1 = 6
in2 = 7
in3 = 8
in4 = 9

# Stepper pins IN1-IN4 of stepper
# Any 4 GPIO pins will work
stepper_pins = [
    Pin(in1, Pin.OUT),
    Pin(in2, Pin.OUT),
    Pin(in3, Pin.OUT),
    Pin(in4, Pin.OUT)]

# Time between stepper pulses
step_time_us = 600

# Number of steps per volume call
default_steps = 5

# One Clockwise Step (512 steps = 360°)
full_step_up = [
    [1,0,0,0],
    [0,1,0,0],
    [0,0,1,0],
    [0,0,0,1],
    [0,0,0,0]]

# One Clockwise Step (512 steps = 360°)
full_step_down = [
    [0,0,0,1],
    [0,0,1,0],
    [0,1,0,0],
    [1,0,0,0],
    [0,0,0,0]]

# Turns volume up default_steps times
def volume_up(count = default_steps):
    # print("volume up")
    for _ in range(count):
        flashy.toggle()
        for step in full_step_up:
            for i in range(len(stepper_pins)):
                stepper_pins[i].value(step[i])
                sleep_us(step_time_us)
    flashy.off()
   
# Turns volume down default_steps times
def volume_down(count = default_steps):
    # print("volume down")
    for _ in range(count):
        flashy.toggle()
        for step in full_step_down:
            for i in range(len(stepper_pins)):
                stepper_pins[i].value(step[i])
                sleep_us(step_time_us)
    flashy.off()


# Switch Functions
def up(cont, last_call, call_time):
    print("up")
    cont = True
    last_call = "up"
    volume_up()
    return cont, last_call

def down(cont, last_call, call_time):
    print("down")
    cont = True
    last_call = "down"
    volume_down()
    return cont, last_call

def vol_cont(cont, last_call, call_time):
    # print("continue", cont, last_call, call_time)
    if (time_ns() - call_time)  > 0:
        print("Continue timeout")
        return False, None
    if cont:
        if last_call == "up":
            print("up")
            volume_up()
        if last_call == "down":
            print("down")
            volume_down()
    return cont, last_call

def power(cont, last_call, call_time):
    print("power")
    cont = False
    last_call = "power"
    power_relay.toggle()
    return cont, last_call

def hdmi_power(cont, last_call, call_time):
    print("hdmi power")
    cont = False
    last_call = "hdmi_power"
    return cont, last_call

def arc(cont, last_call, call_time):
    print("arc")
    cont = False
    last_call = "arc"
    return cont, last_call

def hdmi_1(cont, last_call, call_time):
    print("hdmi 1")
    cont = False
    last_call = "hdmi_one"
    return cont, last_call

def hdmi_2(cont, last_call, call_time):
    print("hdmi 2")
    cont = False
    last_call = "hdmi_two"
    return cont, last_call

def hdmi_3(cont, last_call, call_time):
    print("hdmi 3")
    cont = False
    last_call = "hdmi_three"
    return cont, last_call

def hdmi_4(cont, last_call, call_time):
    print("hdmi 4")
    cont = False
    last_call = "hdmi_four"
    return cont, last_call

def one(cont, last_call, call_time):
    print("one")
    cont = False
    last_call = "one"
    return cont, last_call

def two(cont, last_call, call_time):
    print("two")
    cont = False
    last_call = "two"
    return cont, last_call

def three(cont, last_call, call_time):
    print("three")
    cont = False
    last_call = "three"
    return cont, last_call

def four(cont, last_call, call_time):
    print("four")
    cont = False
    last_call = "four"
    return cont, last_call

def default(cont, last_call, call_time):
    cont = False
    last_call = None
    print("Nothing to see here?")
    print(buf)
    return cont, last_call

# Switch Function Dict
switcher = {
    up_bytes:         up,
    down_bytes:       down,
    cont_1_bytes:     vol_cont,
    cont_2_bytes:     vol_cont,
    cont_3_bytes:     vol_cont,
    cont_4_bytes:     vol_cont,
    power_bytes:      power,
    hdmi_power_bytes: hdmi_power,
    hdmi_arc_bytes:   arc,
    hdmi_1_bytes:     hdmi_1,
    hdmi_2_bytes:     hdmi_2,
    hdmi_3_bytes:     hdmi_3,
    hdmi_4_bytes:     hdmi_4,
    one_dot:          one,
    two_dot:          two,
    three_dot:        three,
    four_dot:         four
    }
    

def switch(ir_signal, cont, last_call, call_time):
    # print("switcher: ", ir_signal)
    return switcher.get(ir_signal, default)(cont, last_call, call_time)
    
# UART Read Buffer
buf = None

# Continue Volume Up
cont = False

# Last Volume Call
last_call = None

# Setup Polling on UART data
poll = select.poll()
poll.register(uartZero, select.POLLIN)

# Run Forever or until True is False
while True:
    
    # Timer for continue volume
    before_time = time_ns()
    
    # Trigger on data received
    events = poll.poll()
    buf = uartZero.read(12)
    # print(buf)
    
    cont, last_call = switch(buf, cont, last_call, before_time)

    
