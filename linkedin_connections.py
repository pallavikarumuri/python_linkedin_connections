from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fpdf import FPDF, HTMLMixin
import time
import chromedriver_autoinstaller
import os
import re

# Automatically install chromedriver
chromedriver_autoinstaller.install(True)

# Create a new instance of the Chrome driver
options = webdriver.ChromeOptions()
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--start-maximized")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--enable-unsafe-swiftshader")
options.add_argument("--ignore-certificate-errors")

driver = webdriver.Chrome(options=options)

# Set page load timeout and implicit wait
driver.set_page_load_timeout(120)
driver.implicitly_wait(20)

# Open LinkedIn login page
try:
    driver.get("https://www.linkedin.com/login")
except Exception as e:
    print(f"Page load timed out: {e}")
    driver.quit()
    exit(1)

# Allow time for the page to load
time.sleep(2)

# Set environment variables (for testing purposes only)
os.environ["LINKEDIN_USERNAME"] = "user mail id@gmail.com"
os.environ["LINKEDIN_PASSWORD"] = "user password"

# Get username and password from environment variables
username = os.getenv("LINKEDIN_USERNAME")
password = os.getenv("LINKEDIN_PASSWORD")

# Enter your username and password
try:
    username_field = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username_field.send_keys(username)
    password_field = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
except Exception as e:
    print(f"Error entering credentials: {e}")
    driver.quit()
    exit(1)

# Allow time for login to complete
time.sleep(5)

# Open LinkedIn search page with query
search_query = "data science"
try:
    driver.get(f"https://www.linkedin.com/search/results/people/?keywords={search_query}")
except Exception as e:
    print(f"Page load timed out: {e}")
    driver.quit()
    exit(1)

time.sleep(2)

# Function to click all 'Connect' buttons while scrolling
def click_connect_buttons_and_scroll():
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        try:
            connect_buttons = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//button[contains(@aria-label, 'Connect')]"))
            )
            print(f"Found {len(connect_buttons)} 'Connect' buttons.")
            for button in connect_buttons:
                try:
                    driver.execute_script("arguments[0].scrollIntoView();", button)
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button))
                    driver.execute_script("arguments[0].click();", button)
                    print("Clicked 'Connect' button.")
                    time.sleep(1)  # Reduced delay
                except Exception as click_error:
                    print(f"Error clicking 'Connect' button: {click_error}")

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # Reduced delay
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        except Exception as find_error:
            print(f"Error finding 'Connect' buttons: {find_error}")
            break

# Initial scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

# Start the process
click_connect_buttons_and_scroll()

# Go to My Network and send connection requests
def send_connection_requests(driver, num_requests):
    driver.get("https://www.linkedin.com/mynetwork/")
    time.sleep(1)  # Reduced delay
    connect_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Connect')]")
    print(f"Found {len(connect_buttons)} 'Connect' buttons in My Network.")
    
    for i in range(min(num_requests, len(connect_buttons))): 
        connect_buttons[i].click()  # Click the "Connect" button
        time.sleep(1)  # Reduced delay
        print(f"[{i + 1}] Connection request sent")
    
    print("Done sending connection requests")

# Send connection requests
send_connection_requests(driver, 10)

# # Quit the driver
# driver.quit()

#Navigate to the "My Network" page
driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")

# Allow time for the page to load
time.sleep(5)

# Scroll to load all connections
SCROLL_PAUSE_TIME = 2
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Retrieve all connections
connections = driver.find_elements(By.XPATH, "//div[@class='mn-connection-card__details']")
connections_list = []
for conn in connections:
    try:
        name = conn.find_element(By.XPATH, ".//span[@class='mn-connection-card__name t-16 t-black t-bold']").text
        details = conn.find_element(By.XPATH, ".//span[@class='mn-connection-card__occupation t-14 t-black--light t-normal']").text
        connections_list.append({'name': name, 'details': details})
    except Exception as e:
        print(f"Error retrieving connection details: {e}")

# Close the driver
driver.quit()

# Define a class for PDF generation with HTML support
class PDF(FPDF, HTMLMixin):
    pass

# Function to remove unsupported characters
def remove_unsupported_characters(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

# Create PDF with filtered text
pdf = PDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

pdf.cell(200, 10, txt="LinkedIn Connections", ln=True, align="C")
pdf.ln(10)

for conn in connections_list:
    name = remove_unsupported_characters(conn['name'])
    details = remove_unsupported_characters(conn['details'])
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Details: {details}", ln=True)
    pdf.ln(5)

pdf.output("LinkedIn_Connections.pdf")

print("PDF created successfully.")









