# Written by Dr. Tolga Soyata       4/23/2023
#
# This program does edge detection on an image captured from video0
# It splits the screen into four sub-windows, which display the following into:
#    TOP LEFT) original image           TOP RIGHT) Gray scale
# BOTTOM LEFT) blurred image         BOTTOM RIGHT) Detected edges

import cv2
import numpy as np
import time

TX=10
TY1=30
TY2=55
COL1=(0,0,255)       # Text 1 color
COL2=(255,255,0)     # Text 2 color
COL3=(255,0,0)     # Line color
FONT1=cv2.FONT_HERSHEY_SIMPLEX    # Text 1 font
FONT2=cv2.FONT_HERSHEY_PLAIN      # Text 2 font


t1=time.time()
FPS=0.00
LogiC270 = cv2.VideoCapture(0)

try:
    while True:
        sucess, C270img = LogiC270.read()
        ImgH2,ImgW2 = C270img.shape[0], C270img.shape[1]
        ImgH, ImgW = int(ImgH2/2), int(ImgW2/2)
        ImgDim=(ImgW, ImgH)
        
        # shrink the original image to half in both dimensions
        HalfImg=cv2.resize(C270img,ImgDim, interpolation=cv2.INTER_AREA)
        # This is what we will see. Start with a blank image
        EntireImg=np.zeros((ImgH2, ImgW2,3), dtype = np.uint8)
        # bury the original inside the entire image (top left quarter)
        EntireImg[0:ImgH, 0:ImgW] = HalfImg

        # Gray scale version of the captured image
        GrayImg=cv2.cvtColor(HalfImg,cv2.COLOR_BGR2GRAY)
        EntireImg[0:ImgH:, ImgW:] = cv2.cvtColor(GrayImg, cv2.COLOR_GRAY2BGR)
        
        # Blurred version of the captured image
        BlurImg=cv2.GaussianBlur(GrayImg,(101,201),0)
        EntireImg[ImgH:, 0:ImgW] = cv2.cvtColor(BlurImg, cv2.COLOR_GRAY2BGR)

        # Edge detected image
        EdgeImg=cv2.Canny(image= GrayImg, threshold1=100, threshold2=200)
        EntireImg[ImgH:, ImgW:] = cv2.cvtColor(EdgeImg, cv2.COLOR_GRAY2BGR)
        
        # add text to each sub-image
        cv2.putText(EntireImg,"Original",(TX,TY1),FONT1, 1, COL1, 2)
        ImgDimStr=str(ImgW) + 'x' + str(ImgH)
        cv2.putText(EntireImg,ImgDimStr,(TX,TY2),FONT2, 1, COL2, 1)
        cv2.putText(EntireImg,"Gray Scale",(TX+ImgW,TY1),FONT1, 1, COL1, 2)
        cv2.putText(EntireImg,"Blur",(TX,TY1+ImgH),FONT1, 1, COL1, 2)
        cv2.putText(EntireImg,"Edges",(TX+ImgW,TY1+ImgH),FONT1, 1, COL1, 2)
        
        # seperating lines between images
        #cv2.line(EntireImg,(ImgW-1,0),(ImgW-1,ImgH2-1),COL3,3)
        cv2.line(EntireImg,(ImgW-1,0),(ImgW-1, 2*ImgH-1),COL3,3)
        cv2.line(EntireImg,(0,ImgH-1),(2*ImgW-1, ImgH-1),COL3,3)
        
        # Calculate and print FPS
        t2=time.time()
        FPS=f"{(1/(t2-t1)):4.1f} fps"
        t1=t2
        cv2.putText(EntireImg,FPS,(TX+ImgW,TY2+ImgH),FONT2, 1, COL2, 1)
        # show the entire image
        cv2.imshow("EDGE DETECTION",EntireImg)
        cv2.waitKey(1)
except KeyboardInterrupt:
    print("\n\nEdge detection program is done!!!")

cv2.destroyAllWindows()

