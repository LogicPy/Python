import mss
import numpy as np
import cv2
import keyboard
import torch 
import pyautogui
import torchvision
import time

# SETUP. Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='C:/Users/Admin/Desktop/best5.pt')
#model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True) 

# Set the screen size
ScreenSizeX = 1920
ScreenSizeY = 1080
with mss.mss() as sct: 
    monitor = {'top': 0, 'left': 0, 'width': ScreenSizeX, 'height': ScreenSizeY}

while True:
    img = np.array(sct.grab(monitor))

    # Perform object detection
    results = model(img)

    rl = results.xyxy[0].tolist()
    print(rl)
    
    #time.sleep(4000)
    # If any objects are detected
    if len(rl) > 0:
        # If the confidence is above 30%
        if rl[0][4] > .35:
            # Class prediction
            if rl[0][5]  == 15 or rl[0][5] == 17 or rl[0][5] == 18:
                x = int(rl[0][2])
                y = int(rl[0][3])

                print(rl[0])

                # X Info
                xmax = int(rl[0][2])
                width = int(rl[0][2] - rl[0][0])
                screenCenterX = ScreenSizeX / 2
                centerX = int((xmax - (width/2)) - screenCenterX)
                
                # Y INFO
                ymax = int(rl[0][1])
                height = int(rl[0][3] - rl[0][1])

                xpos = int(.37 * ((x - (width/2)) - pyautogui.position()[0]))
                ypos = int(.30 * ((x - (height/2)) - pyautogui.position()[1]))
                screenCenterY = ScreenSizeY / 2
                centerY = int((ymax - (height/4)) - screenCenterY)

                # Change decimal as needed
                moveX = int(centerX * .1)
                moveY = int(centerY * .1)

                if centerY < screenCenterY:
                    moveY *= -1

                # Simulate mouse movements based on the detected object
                pyautogui.moveRel(xpos, ypos)
                pyautogui.click()
                pyautogui.moveRel(-xpos, -ypos)

    cv2.imshow('s', np.squeeze(results.render()))
    cv2.waitKey(1)

    if keyboard.is_pressed('q'):
        force_reload=True
        break

cv2.destroyAllWindows()
