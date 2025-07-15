from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import asyncio
import time
import smtplib
import dotenv
import os
from email.message import EmailMessage

dotenv.load_dotenv()

chrome_options = Options()
chrome_options.add_argument("--headless") 
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL = os.getenv("EMAIL")

class TusTusListener():
    def __init__(self, website):
        self.website = website
        self.existing_flights_location = []

    def get_flight_locations(self):
        driver.get(self.website)
        search_button = driver.find_element(By.CSS_SELECTOR, ".filter_category.search")
        search_button.click()

        search_results = driver.find_element(By.ID, "dropList_serach")
        flights_locations = search_results.find_elements(By.TAG_NAME, "li")
        flight_locations_text = [flight.text for flight in flights_locations]

        #Check for new flights
        for flight in flight_locations_text:
            if flight not in self.existing_flights_location:
                self.existing_flights_location.append(flight)
                self.send_new_flight_update(location=flight)

        # Check for removed flights
        self.existing_flights_location = [
            flight for flight in self.existing_flights_location if flight in flight_locations_text
        ]

        driver.quit()
    
    def send_new_flight_update(self, location):
        msg = EmailMessage()
        msg["Subject"] = f"יעד חדש הופיע בטוסטוס: {location}"
        msg["From"] = EMAIL
        msg["To"] = EMAIL
        #Sending and receiving to me becuase i just want to view it, can be changed later

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL, EMAIL_APP_PASSWORD)
            smtp.send_message(msg)


listener = TusTusListener("https://www.tustus.co.il/Arkia/Home")

async def run_every_30_minutes():
    while True:
        await asyncio.to_thread(listener.get_flight_locations)  # Run sync function without blocking
        await asyncio.sleep(600)

asyncio.run(run_every_30_minutes())
