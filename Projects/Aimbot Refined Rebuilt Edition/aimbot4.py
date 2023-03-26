import cv2
import numpy as np
import math
import pyautogui
from PIL import Image
from time import sleep
import time
import sys
import win32gui, win32api, win32con, ctypes

# Define the color range for the player (blue)
lower_player = np.array([100, 50, 50])
upper_player = np.array([130, 255, 255])

# Define the color range for the enemy players (red)
lower_enemy = np.array([0, 50, 50])
upper_enemy = np.array([20, 255, 255])


print ("""
  _____         ___         _      _____ _       _       _     
 |  _  |___ ___|  _|___ ___| |_   |  _  |_|_____| |_ ___| |_   
 |   __| -_|  _|  _| -_|  _|  _|  |     | |     | . | . |  _|  
 |__|  |___|_| |_| |___|___|_|    |__|__|_|_|_|_|___|___|_|                                                             
 Coded by LogicPy (Wayne Kenney) - 3/24/2023 - [Private Edition]
           -= Universal Game Aimbot (Undetectable) =-
""")

Box = 640, 360, 640, 360

# Capture the screenshot using PyAutoGUI
screenshot = pyautogui.screenshot(region=Box)

# Convert the screenshot to a NumPy array
screenshot = np.array(screenshot)

# Convert the color from BGR to RGB
screenshot = screenshot[:, :, ::-1]

# Load the image
img = screenshot.copy()

# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply a threshold to the image to make it black and white
ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# Find the contours in the image
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Initialize variables for player and enemy positions
player_x, player_y = 0, 0
enemy_x, enemy_y = 0, 0
enemy_height = 1.8 # meters
# Replace with the height of the player provided by the game or detected using computer vision
player_height = 1.7 # meters

# Loop through the contours
for cnt in contours:
    # Get the area of the contour
    area = cv2.contourArea(cnt)
    
    # If the area is too small, skip it
    if area < 100:
        continue
    
    # Get the bounding box for the contour
    x, y, w, h = cv2.boundingRect(cnt)
    
    # If the rectangle is in the top third of the image, it's the game screen
    if y < img.shape[0] / 3:
        continue
    # If the rectangle is in the bottom third of the image, it's an enemy player
    elif y > img.shape[0] * 2 / 3:
        # Calculate the center of the enemy player
        enemy_center_x = x + w / 2
        enemy_center_y = y + h / 2
        
        # Draw a circle at the center of the enemy player
        cv2.circle(img, (int(enemy_center_x), int(enemy_center_y)), 5, (0, 0, 255), -1)
        
        # Set the enemy position variables to the center of the enemy player
        enemy_x, enemy_y = enemy_center_x, enemy_center_y
    # Otherwise, it's the player
    else:
        # Calculate the center of the player
        player_center_x = x + w / 2
        player_center_y = y + h / 2
        
        # Draw a circle at the center of the player
        cv2.circle(img, (int(player_center_x), int(player_center_y)), 5, (255, 0, 0), -1)
        
        # Set the player position variables to the center of the player
        player_x, player_y = player_center_x, player_center_y
        
# Calculate the distance between the player and enemy
dx = enemy_x - player_x
dy = enemy_y - player_y
distance = math.sqrt(dx ** 2 + dy ** 2)

# Calculate the angle between the player and enemy
angle = math.atan2(dy, dx) * 180 / math.pi
# Replace with the x-coordinates of the player and enemy provided by the game or detected using computer vision
player_x = 100
enemy_x = 200

# Calculate the horizontal distance between the player and the enemy
horizontal_distance = abs(enemy_x - player_x)


# Calculate the velocity required to hit the enemy player
velocity = 50.0 # Replace with your own value
gravity = 9.81 # Replace with your own value
theta = math.atan2(enemy_y - player_y, enemy_x - player_x) # Angle between player and enemy
distance = math.sqrt((enemy_x - player_x)**2 + (enemy_y - player_y)**2) # Distance between player and enemy
height_difference = enemy_height - player_height # Height difference between player and enemy
horizontal_distance = distance * math.cos(theta) # Horizontal distance between player and enemy
vertical_distance = distance * math.sin(theta) # Vertical distance between player and enemy

# Calculate the angle to hit the enemy player
if horizontal_distance == 0:
    if enemy_y > player_y:
        angle_to_hit = 90
    else:
        angle_to_hit = -90
else:
    angle_to_hit = math.atan((velocity**2 + math.sqrt(velocity**4 - gravity*(gravity*horizontal_distance**2 + 2*height_difference*velocity**2))) / (gravity*horizontal_distance))


# Calculate the angle required to hit the enemy player
angle_to_hit = math.atan((velocity**2 + math.sqrt(velocity**4 - gravity*(gravity*horizontal_distance**2 + 2*height_difference*velocity**2))) / (gravity*horizontal_distance))

# Convert the angle to degrees
angle_to_hit = math.degrees(angle_to_hit)

# Debugging (2)
print("Distance: ", distance)
print("Height difference: ", height_difference)
print("Horizontal distance: ", horizontal_distance)
print("Vertical distance: ", vertical_distance)
print("Angle to hit: ", angle_to_hit)

# Move the mouse pointer to the calculated angle
screen_width, screen_height = pyautogui.size()
mouse_x = screen_width / 2 + distance * math.cos(angle_to_hit * math.pi / 180)
mouse_y = screen_height / 2 + distance * math.sin(angle_to_hit * math.pi / 180)

# Move the mouse pointer to the calculated position
pyautogui.moveTo(mouse_x, mouse_y)
