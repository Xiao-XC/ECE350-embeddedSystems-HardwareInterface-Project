import time
from gpiozero import LED, MotionSensor

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
