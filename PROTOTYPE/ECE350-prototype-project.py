import time
from gpiozero import LED, MotionSensor, AngularServo


red = LED()
yellow = LED()
green = LED()

MIN_PULSE = 0.0005
MAX_PULSE = 0.0025
servo = AngularServo(
pin = GPIO_PIN,
    min_angle = 0,
    max_angle = 180,
    min_pulse_width =MIN_PULSE,
    max_pulse_width = MAX_PULSE
)


Motion = MotionSensor(23)
try:
    while True:
        Motion.wait_for_motion()
        if Motion.motion_detected:
            red.on()
            time.sleep(0.05)
            red.off()
            time.sleep(0.05)
            red.on()
            time.sleep(0.05)
            red.off()
            time.sleep(0.05)
            print("MOTION DETECTED!")


except KeyboardInterrupt:
    red.off()
    print("Program stopped.")


