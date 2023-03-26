import cv2
import numpy as np
import math
import pyautogui
from PIL import Image
from time import sleep
import time
import sys
import win32gui, win32api, win32con, ctypes
import mouse

print ("""
  _____         ___         _      _____ _       _       _     
 |  _  |___ ___|  _|___ ___| |_   |  _  |_|_____| |_ ___| |_   
 |   __| -_|  _|  _| -_|  _|  _|  |     | |     | . | . |  _|  
 |__|  |___|_| |_| |___|___|_|    |__|__|_|_|_|_|___|___|_|                                                             
 Coded by Pythogen (Wayne Kenney) - 4/27/2018 - [Private Edition]
           -= GunZ 2 (Undetectable) =-
""")

def mouseMovementTest():
    while(True):
        print (mouse.get_position())
        mouse.move(100, 100, absolute=False, duration=0.2)
        
#mouseMovementTest()

def find_center(image):
    # Convert image to grayscale and apply threshold
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Check if any contours were found
    if len(contours) == 0:
        return None

    # Find the largest contour
    contour = max(contours, key=cv2.contourArea)

    # Get the moments of the largest contour
    M = cv2.moments(contour)

    # Calculate the center of mass of the contour
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        return (cx, cy)
    else:
        return None


player_lower = np.array([0, 0, 255])
player_upper = np.array([0, 0, 255])
color = np.array([0, 0, 255])
enemy_lower = np.array([100, 100, 200])
enemy_upper = np.array([140, 140, 255])

# Define the region of interest (ROI) where the game screen is located
roi = (0, 0, 1920, 1080)

# Define the velocity and gravity values for the projectile motion calculation
velocity = 50.0
gravity = 9.81

while True:
    # Capture the screen and convert it to the RGB color space
    screen = np.array(pyautogui.screenshot(region=roi))
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
    
    # Threshold the image to extract the player and enemy players
    player_mask = cv2.inRange(screen, player_lower, player_upper)
    enemy_mask = cv2.inRange(screen, enemy_lower, enemy_upper)
    
    # Combine the player and enemy masks
    combined_mask = cv2.bitwise_or(player_mask, enemy_mask)
    # Apply a binary threshold to the combined mask
    _, threshold = cv2.threshold(combined_mask, 127, 255, cv2.THRESH_BINARY)
    
    # Find the center of the thresholded image
    center = find_center(screen)

    if center is not None:
        # Move the mouse to the center
        pyautogui.moveTo(center[0] + roi[0], center[1] + roi[1])

    # Find the contours of the player and enemy players
    player_contours, _ = cv2.findContours(player_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    enemy_contours, _  = cv2.findContours(enemy_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    
    # Get the center coordinates of the player and enemy players
    player_center = None
    enemy_centers = []
    for contour in player_contours:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            player_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    for contour in enemy_contours:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            enemy_center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            enemy_centers.append(enemy_center)
    
    # Calculate the horizontal distance and height difference between the player and enemy players
    if player_center and enemy_centers:
        enemy_center = enemy_centers[0]
        horizontal_distance = enemy_center[0] - player_center[0]
        height_difference = player_center[1] - enemy_center[1]
        
        # Calculate the required angle to hit the enemy player
        theta = math.atan2(height_difference, horizontal_distance)
        distance = horizontal_distance / math.cos(theta)
        angle_to_hit = math.atan((velocity**2 + math.sqrt(velocity**4 - gravity*(gravity*horizontal_distance**2 + 2*height_difference*velocity**2))) / (gravity*horizontal_distance))
        
        # Move the mouse pointer to the calculated angle
        screen_width, screen_height = pyautogui.size()
        mouse_x = screen_width / 2 + distance * math.cos(angle_to_hit)
        mouse_y = screen_height / 2 + distance * math.sin(angle_to_hit)
        pyautogui.moveTo(mouse_x + center[0], mouse_y + center[1], duration=0)
        mouse.move(mouse_x + center[0], mouse_y + center[1], duration=0)
        #pyautogui.moveTo(region_x + center[0], region_y + center[1])

        print("Distance: ", distance)
        print("Height difference: ", height_difference)
        print("Horizontal distance: ", horizontal_distance)
        print("Vertical distance: ", vertical_distance)
        print("Angle to hit: ", angle_to_hit)


    # Wait for a short duration before capturing the next screen
    time.sleep(0.1)
