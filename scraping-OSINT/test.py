from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import glob

# service = Service(executable_path="chromedriver.exe")
# driver = webdriver.Chrome(service=service)

import requests

def check_url(url):
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            return False
    

def generate_usernames(first_name, last_name):
    usernames = [
        f"{first_name}{last_name}",
        f"{first_name}.{last_name}",
        f"{first_name}_{last_name}",
        f"{last_name}{first_name}",
        f"{last_name}.{first_name}",
        f"{last_name}_{first_name}",
        f"{first_name}{last_name[0]}",
        f"{last_name}{first_name[0]}",
        f"{first_name[0]}{last_name}",
        f"{last_name[0]}{first_name}"
    ]
    return usernames

def check_instagram_profile(username):
    service = Service(executable_path="./chromedriver")
    chrome_options = Options()
    #chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(f"https://www.instagram.com/{username}/")
        time.sleep(2)  # Allow time for page to load
        substring1 = "Sorry, this page isn't available."
        substring2 = "Something went wrong"
        
        if "Page Not Found" in driver.title:
            return False
        
        elements_with_text = driver.find_elements(By.XPATH, "//*[text()]")
        
        for element in elements_with_text:
            if substring2 == element.text:
                return True
        for element in elements_with_text:
            if substring1 == element.text:
                return False

        return True
    
    except Exception as e:
        print(f"Error checking Instagram profile: {str(e)}")
        return False
    
    finally:
        driver.quit()

# def check_facebook_profile(username):
#     service = Service(executable_path="./chromedriver")
#     chrome_options = Options()
#     #chrome_options.binary_location = "/usr/bin/google-chrome"  # Adjust this path if necessary
#     #chrome_options.add_argument('--headless')  # Run in headless mode
#     chrome_options.add_argument('--no-sandbox')
#     chrome_options.add_argument('--disable-dev-shm-usage')

#     driver = webdriver.Chrome(service=service, options=chrome_options)
    
#     try:
#         driver.get(f"https://www.facebook.com/{username}/")
#         time.sleep(3)  # Allow time for page to load
        
#         if "Page Not Found" in driver.title:
#             return False

#         try:
#             # Locate the parent div with aria-label="Allow all cookies"
#             accept_cookies_div = driver.find_element(By.XPATH, "//*[@id='facebook']/body/div[3]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[2]/div[1]")
        
#             accept_cookies_div.click()
            
#             time.sleep(3)
#             
#             time.sleep(7)
#         except Exception as e:
#             print("No cookie consent dialog found or error: ", e)
        
#         buttonX = driver.find_element(By.XPATH, "//*[@id='mount_0_0_zw']/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div")
#         buttonX.click()
#         time.sleep(10) #pt test vizual

#         return True
    
#     except Exception as e:
#         print(f"Error checking FB profile: {str(e)}")
#         return False
    
#     finally:
#        driver.quit()


def check_facebook_profile(username):
    service = Service(executable_path="./chromedriver")
    chrome_options = Options()
    #chrome_options.add_argument('--headless')  
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--incognito")

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(f"https://www.facebook.com/{username}/")
        WebDriverWait(driver, 10).until(EC.title_contains("Facebook"))  # Wait for the page title to contain "Facebook"

        if "Page Not Found" in driver.title:
            return False

        try:
            # Accept cookies if the dialog is present
            accept_cookies_div = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='facebook']/body/div[3]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[2]/div[1]"))
            )
            accept_cookies_div.click()
        except Exception as e:
            #print("No cookie consent dialog found or error: ", e)
            return False

        # Wait for the main content to load after accepting cookies
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@aria-label='Close']"))
        )

        # Click the desired button or element
        buttonX = driver.find_element(By.XPATH, "//*[@aria-label='Close']")
        buttonX.click()

        # time.sleep(2)
        # driver.refresh()  
        # elements_with_text = driver.find_elements(By.XPATH, "//*[text()]")


        # for element in elements_with_text:
        # print(element.text)
        return True
    except Exception as e:
        #print(f"Error checking Facebook profile: {str(e)}")
        return False

    finally:
        driver.quit()

    return True

# Update check_social_media_accounts function to use check_instagram_profile
def check_social_media_accounts(usernames):
    base_urls = {
        "Facebook": "https://www.facebook.com/",
        "Instagram": "https://www.instagram.com/",
        
    }

    
    found_accounts = []

    for platform, base_url in base_urls.items():
        for username in usernames:
            url_to_check = base_url + username
            if platform == "Instagram":
                #if check_instagram_profile(username):
                    #found_accounts.append((platform, url_to_check))
                print(f"{platform}: {url_to_check}")

            else:
                if check_facebook_profile(username):
                    #found_accounts.append((platform, url_to_check))
                    #time.sleep(1)  # Add a delay to avoid rate limiting
                    print(f"{platform}: {url_to_check}")

    # if not found_accounts:
    #     print("No social media accounts found.")
    # else:
    #     print("Found social media accounts:")
    #     for platform, url in found_accounts:
    #         print(f"{platform}: {url}")

def setup_driver():
    service = Service(executable_path="./chromedriver")
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--disable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--incognito")

    # Prevent downloading files
    prefs = {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  # Open PDFs in Chrome, not download
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def search_google_for_pdfs(driver, query):
    search_url = f"https://www.google.com/search?q={query}+filetype:pdf"
    driver.get(search_url)
    time.sleep(3)  # Allow time for page to load

    pdf_links = driver.find_elements(By.XPATH, '//a[contains(@href, ".pdf")]')
    pdf_urls = [link.get_attribute('href') for link in pdf_links]
    return pdf_urls

def check_pdf_url(driver, url):
    driver.get(url)
    time.sleep(1)  # Allow time for page to load
    print(f"Opened URL: {url}")
    #print(f"Page title: {driver.title}")

def pdf_func(first_name, last_name):
    driver = setup_driver()
    username = first_name + ' ' + last_name
    print(username)
    pdf_urls = search_google_for_pdfs(driver, username)
    
    for url in pdf_urls:
        check_pdf_url(driver, url)
    
    driver.quit()

def delete_pdfs_in_current_directory():
    # Obține lista de toate fișierele PDF din directorul curent
    pdf_files = glob.glob("*.pdf")
    
    for pdf_file in pdf_files:
        try:
            os.remove(pdf_file)
            print(f"Deleted: {pdf_file}")
        except Exception as e:
            print(f"Error deleting {pdf_file}: {e}")

print("-----------------------------------------------------------------")
first_name = input("Prenume: ").strip().lower()
last_name = input("Nume: ").strip().lower()
usernames = generate_usernames(first_name, last_name)
print("-----------------------------------------------------------------")

check_social_media_accounts(usernames)

print("-----------------------------------------------------------------")

# pdf_func(first_name, last_name)
# pdf_func(last_name, first_name)
# delete_pdfs_in_current_directory()

print("-----------------------------------------------------------------")

# driver.quit()
