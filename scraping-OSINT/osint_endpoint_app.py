from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import os
import glob
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import requests

app = Flask(__name__)
CORS(app)

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

def setup_driver():
    service = Service(executable_path="./chromedriver")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    prefs = {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def search_google_for_pdfs(driver, query):
    search_url = f"https://www.google.com/search?q={query}+filetype:pdf"
    driver.get(search_url)
    time.sleep(3)
    pdf_links = driver.find_elements(By.XPATH, '//a[contains(@href, ".pdf")]')
    pdf_urls = [link.get_attribute('href') for link in pdf_links]
    return pdf_urls

def check_pdf_url(driver, url):
    driver.get(url)
    time.sleep(1)
    return url

def delete_pdfs_in_current_directory():
    pdf_files = glob.glob("*.pdf")
    for pdf_file in pdf_files:
        try:
            os.remove(pdf_file)
        except Exception as e:
            print(f"Error deleting {pdf_file}: {e}")

@app.route('/check_social_media', methods=['POST'])
def check_social_media():
    data = request.json
    first_name = data.get('first_name').strip().lower()
    last_name = data.get('last_name').strip().lower()
    usernames = generate_usernames(first_name, last_name)
    found_accounts = []

    base_urls = {
        "Facebook": "https://www.facebook.com/",
        "Instagram": "https://www.instagram.com/",
    }

    for platform, base_url in base_urls.items():
        for username in usernames:
            url_to_check = base_url + username
            if platform == "Instagram":
                if check_instagram_profile(username):
                    found_accounts.append((platform, url_to_check))
            else:
                if check_facebook_profile(username):
                    found_accounts.append((platform, url_to_check))                   
    
    return jsonify(found_accounts)

@app.route('/search_pdfs', methods=['POST'])
def search_pdfs():
    data = request.json
    first_name = data.get('first_name').strip().lower()
    last_name = data.get('last_name').strip().lower()

    def generate():
        driver = setup_driver()
        try:
            queries = [first_name + ' ' + last_name, last_name + ' ' + first_name]
            for query in queries:
                pdf_urls = search_google_for_pdfs(driver, query)
                for url in pdf_urls:
                    yield f"data:{url}\n\n"
        except Exception as e:
            print(f"Error in search_pdfs: {e}")
        finally:
            driver.quit()
            delete_pdfs_in_current_directory()

    return Response(generate(), content_type='text/event-stream')

def check_instagram_profile(username):
    service = Service(executable_path="./chromedriver")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(f"https://www.instagram.com/{username}/")
        time.sleep(2)
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
        return False
    
    finally:
        driver.quit()

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
        WebDriverWait(driver, 10).until(EC.title_contains("Facebook"))  

        if "Page Not Found" in driver.title:
            return False

        try:
            
            accept_cookies_div = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='facebook']/body/div[3]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[2]/div[1]"))
            )
            accept_cookies_div.click()
        except Exception as e:
            
            return False

        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@aria-label='Close']"))
        )

        
        buttonX = driver.find_element(By.XPATH, "//*[@aria-label='Close']")
        buttonX.click()

        time.sleep(2)
        # driver.refresh()  
        # elements_with_text = driver.find_elements(By.XPATH, "//*[text()]")


        # for element in elements_with_text:
        # print(element.text)
        return True
    except Exception as e:
        
        return False

    finally:
        driver.quit()

    return True

def search_google(driver, query):
    search_url = f"https://www.google.com/search?q={query}"
    driver.get(search_url)
    
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@id="W0wltc"]'))
        )
        accept_button.click()
    except TimeoutException:
        print("No cookies prompt found or error accepting cookies")
    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//cite[@class="qLRx3b tjvcx GvPZzd cHaqb"]')))
        result_cites = driver.find_elements(By.XPATH, '//cite[@class="qLRx3b tjvcx GvPZzd cHaqb"]')
        urls = [cite.text.replace(' › ', '/') for cite in result_cites[:10]]
    except Exception as e:
        print(f"Error finding search results: {e}")
        urls = []
    
    return urls


def scrape_page(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        title = driver.title
        page_content = driver.find_element(By.TAG_NAME, 'body').text
        return title, page_content[:500]  
    except TimeoutException:
        return None, "Content not available: Page took too long to load."
    except NoSuchElementException:
        return None, "Content not available: Element not found on the page."
    except WebDriverException as e:
        return None, f"Error scraping {url}: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error scraping {url}: {str(e)}"


@app.route('/search_web', methods=['POST'])
def search_web():
    data = request.json
    first_name = data.get('first_name').strip().lower()
    last_name = data.get('last_name').strip().lower()
    
    query = f"{first_name} {last_name}"
    
    driver = setup_driver()
    
    search_results = search_google(driver, query)
    results = []
    
    for url in search_results:
        title, page_content = scrape_page(driver, url)
        if title is None or page_content.startswith('Error'):
            results.append({
                "url": url,
                "error": page_content  
            })
        else:
            results.append({
                "url": url,
                "title": title,
                "content": page_content[:200]  
            })
    
    driver.quit()
    
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=False)
