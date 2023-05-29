from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from time import sleep

def initialize_the_artwork_upload():
	# Replace these with your DeviantArt username and password
	USERNAME = "DrMorphGTS3"
	PASSWORD = "passphrase"
	ART_PATH = "E:/1.png"

	# Initialize the Chrome driver
	driver = webdriver.Chrome()

	# Navigate to DeviantArt's login page
	driver.get("https://www.deviantart.com/users/login")

	# Enter username
	username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
	username_field.send_keys(USERNAME)

	# Enter password
	password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
	password_field.send_keys(PASSWORD)

	# Submit the form
	password_field.send_keys(Keys.RETURN)

	# Navigate to upload page - replace this URL if it changes
	driver.get("https://www.deviantart.com/submit/deviation")

	# Upload the art - this part will change based on how the site accepts file uploads
	upload_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "upload_button")))
	upload_button.send_keys(ART_PATH)

	# Fill out any additional fields required for upload, similar to the username/password process

	# Submit the art
	submit_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "submit_button")))
	submit_button.click()

	# Close the browser
	driver.quit()

now = datetime.now()

# Example : Current Time = 20:53:32
current_time = now.strftime("%H:%M")
print("Current Time =", current_time)

def Time_Checker():
	now = datetime.now()
	current_time = now.strftime("%H:%M")
	print(current_time)
	if(current_time == "21:21"):
		print("Time reached! Run DA Upload procedure!")
		initialize_the_artwork_upload()
	else:
		print("Waiting...")
		sleep(1)
		Time_Checker()
Time_Checker()

