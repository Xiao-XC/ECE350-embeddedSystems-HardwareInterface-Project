# Written by Dr. Tolga Soyata      
#
# This program demonstrates simple Open CV functionality
# It opens two separate Open CV windows. 
# First windows displays a static image (dog) for 40 seconds and closes
# The second window displays an image, captured from Logitech C270
# The second window also displays a count-down timer and the frames-per-second
#

import cv2
import time

DOGimg = cv2.imread('dog.bmp')
cv2.imshow("WOOF",DOGimg)
WOOFduration=40
WOOFopen=True
t1=time.time()
#cv2.waitKey(0)

FPS=1.0

LogiC270 = cv2.VideoCapture(0)

try:
    while True:
        t2=time.time()
        WOOFtimer=int(t2-t1)
        WOOFstr=str(WOOFduration-WOOFtimer)
        if (WOOFtimer>WOOFduration) and WOOFopen:
                WOOFopen=False
                cv2.destroyWindow("WOOF")
        sucess, C270img = LogiC270.read()
        FPSstr=f"{FPS:3.1f} fps";
        cv2.putText(C270img,FPSstr,(10,30),cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,255), 2)
        if WOOFopen:
            cv2.putText(C270img,WOOFstr,(10,70),cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 3)
        cv2.imshow("CAPTURE",C270img)
        print(f"Frame Rate = {FPS:4.1f} fps",22*'\b',end='',flush=True)
        cv2.waitKey(1)
        t3=time.time()
        FPS=1.0/(t3-t2)
except KeyboardInterrupt:
    print("\n\nCapture is done!!!")

cv2.destroyAllWindows()

