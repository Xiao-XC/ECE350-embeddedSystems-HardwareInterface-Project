import time
from gpiozero import LED, MotionSensor, AngularServo, Buzzer

red = LED()
yellow = LED()
green = LED()
buzzer = Buzzer()

MIN_PULSE = 0.0005
MAX_PULSE = 0.0025
servo = AngularServo(
pin = GPIO_PIN,
    min_angle = 0,
    max_angle = 180,
    min_pulse_width =MIN_PULSE,
    max_pulse_width = MAX_PULSE
)

Blink = 0



Motion = MotionSensor(23)
try:
    while True:
        Motion.wait_for_motion()
        if not Motion.motion_detected:
            green.on()
            red.off()
            yellow.off()
            buzzer.off()
            servo.angle = 0
        if Motion.motion_detected:
            green.off()
            time.sleep(1)
            yellow.on()
            time.sleep(1)
            yellow.off()
            red.off()
            buzzer.off()
            servo.angle = 180
            Blink +=1
            print("MOTION DETECTED!")
        if Blink == 3: 
            red.on()
            buzzer.on()
            yellow.off()
            green.off()
            time.sleep(1)
            Blink = 0

except KeyboardInterrupt:
    red.off()
    print("Program stopped.")


