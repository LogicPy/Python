from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from random_username.generate import generate_username
import random

def register_on_deviantart():
    # Set up the chromedriver service
    service = Service('path/to/chromedriver')
    options = webdriver.ChromeOptions()
    options.add_argument('--log-level=3')
    # configure other options if needed

    # Create the webdriver instance with the service object
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.deviantart.com/join")

    email_generator = ['A', 'B', 'C', 'D', 'E'] 
    random.shuffle(email_generator) # shuffle the list in place
    email_generator = ''.join(email_generator) + str(random.randrange(150000))  + "@gmail.com" # join shuffled characters and concatenate with random number
    print ("Email: " + email_generator)


    email_input = driver.find_element(By.ID, "email")
    email_input.send_keys(email_generator)
    passwordshufflepart1=['A', 'B', 'C', 'D', 'E'] 
    random.shuffle(passwordshufflepart1)
    passwordstringint=''.join(passwordshufflepart1) + str(random.randrange(100000, 99999999) )
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(passwordstringint)
    print ("Password: " + str(passwordstringint)) # Used to be statically, 'asdfasdgf43434' now randomly generated too...
    continue_with_email_button = driver.find_element(By.XPATH, '//button[contains(@class, "_2PLlr") and contains(., "Continue with Email")]')
    continue_with_email_button.click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
    usernamevar = generate_username(1)
    username_input = driver.find_element(By.ID, "username")
    username_input.send_keys(usernamevar)
    print ("Username: " + str(usernamevar))

    # Wait for the username to be processed
    inputget = input("press enter to continue.... (After you've set your birthdate)")

    # Wait for the month element to appear

       # Add code for selecting day and year here

    join_button = driver.find_element(By.XPATH, '//button[contains(@class, "_2PLlr") and contains(., "Join")]')
    join_button.click()

    time.sleep(5)  # Wait for 5 seconds to observe the result

    # Navigate to the user's profile page
    user_profile_url = "https://www.deviantart.com/username"
    driver.get(user_profile_url)
    
    # Time to manually select the watch button before Selenium tries to do it itself
    time.sleep(50)
    
    # Temporarily removed for ease of application 
    # Click the "Watch" button to follow the user
    #watch_button = driver.find_element_by_css_selector("button[data-hook='deviation_watch_button']")
    #watch_button.click()

    driver.quit()

try:
    register_on_deviantart()
except Exception as e:
    import traceback
    print("An error occurred during registration:")
    traceback.print_exc()
