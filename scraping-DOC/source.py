from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re

def setup_driver():
    service = Service(executable_path="./chromedriver")  # Adjust the path to your chromedriver
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_data(driver1, driver2):
    driver1.get("https://im-fine.app/ro/psihologi-psihoterapeuti")
    time.sleep(10)  # Allow time for the page to load

    # Click the "Nu acum" button
    try:
        wait = WebDriverWait(driver1, 10)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[span[text()="Nu acum"]]')))
        driver1.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(1)  # Wait a bit after scrolling
        driver1.execute_script("arguments[0].click();", button)
        print("Button clicked.")
        time.sleep(3)  # Wait for the action to complete
    except Exception as e:
        print(f"Error clicking the button: {e}")

    # Click the cookie button
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, 'rcc-decline-button')))
        driver1.execute_script("arguments[0].scrollIntoView(true);", cookie_button)
        time.sleep(1)  # Wait a bit after scrolling
        driver1.execute_script("arguments[0].click();", cookie_button)
        print("Button 'Acceptă selectate' clicked.")
        time.sleep(3)  # Wait for the action to complete
    except Exception as e:
        print(f"Error clicking the cookie button: {e}")


    start_time = time.time()
    while time.time() - start_time < 200:
        driver1.execute_script("window.scrollBy(0, 800);")  # Scroll down 500px
        time.sleep(1)  # Adjust this sleep duration to control the scroll speed


    time.sleep(2)  # Allow time for the page to load

    try:
        profiles = driver1.find_elements(By.XPATH, '//div[contains(@class, "MuiCardHeader-content")]')
        print(f"Found {len(profiles)} profiles.")
    except Exception as e:
        print(f"Error finding profiles: {e}")
        return []  # Return an empty list in case of failure

    data = []

    # Iterate through profiles and extract details
    for profile in profiles:
        try:
            name = profile.find_element(By.XPATH, './/h2[contains(@class, "MuiTypography-h4")]').text
            profession = profile.find_element(By.XPATH, './/p[contains(@class, "MuiTypography-body1")]').text
            location = profile.find_element(By.XPATH, './/p[contains(@class, "MuiTypography-root jss478 MuiTypography-body1 MuiTypography-noWrap")]').text

            base_url = "https://im-fine.app/ro/psihoterapeut/"
            namecpy = name.lower()
            namecpy = re.sub(r'\s+', '-', namecpy)
            namecpy = re.sub(r'[^\w-]', '', namecpy)
            profile_url = base_url + namecpy

            # Use driver2 to open the profile URL and extract email
            driver2.get(profile_url)
            time.sleep(2)
            body_text = driver2.find_element(By.TAG_NAME, 'body').text
            pattern = re.compile(r'^(?!imfineapp@gmail\.com$)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', re.MULTILINE)
            matches = pattern.findall(body_text)

            data.append({
                "Name": name,
                "Profession": profession,
                "Location": location,
                "Email": matches
            })
        except Exception as e:
            print(f"Error extracting data from profile: {e}")

    return data

def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)  # Save the data to an Excel file

def print_data(data):
    for entry in data:
        print(f"Name: {entry['Name']}")
        print(f"Email: {entry['Email']}")
        print(f"Profession: {entry['Profession']}")
        print(f"Location: {entry['Location']}")
        print("-" * 40)  # Print a line separator for better readability

def main():
    driver1 = setup_driver()
    driver2 = setup_driver()
    try:
        data = scrape_data(driver1, driver2)
        save_to_excel(data, "psychologists_data.xlsx")
        #print_data(data)
        #print("Data has been saved to psychologists_data.xlsx")
    finally:
        driver1.quit()
        driver2.quit()

if __name__ == "__main__":
    main()
