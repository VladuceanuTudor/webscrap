from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up the WebDriver
options = Options()
options.add_argument('--headless')  # Run in headless mode, comment this if you want to see the browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# List of cities
cities = [
    "aiud", "alba-iulia", "alexandria", "arad", "bacau", "baia-mare", "barlad", "bistrita", "botosani", "braila",
    "brasov", "buftea", "buzau", "calarasi", "campina", "campulung", "campulung-moldoven", "caransebes",
    "constanta", "craiova", "curtea-de-arges", "dej", "deva", "drobeta-turnu-severin", "falticeni",
    "floresti", "focsani", "galati", "gheorgheni", "giurgiu", "hunedoara", "lugoj", "mangalia", "medgidia",
    "medias", "miercurea-ciuc", "navodari", "oradea", "otopeni", "pascani", "petrosani", "piatra-neamt", "pitesti",
    "ploiesti", "ramnicu-valcea", "resita", "roman", "satu-mare", "sfantu-gheorghe", "sibiu", "sighetu-marmatiei",
    "slatina", "slobozia", "suceava", "targoviste", "targu-jiu", "targu-mures", "targu-neamt", "targu-secuiesc",
    "tecuci", "tulcea", "turda", "urziceni", "vaslui", "vatra-dornei", "voluntari"
]

# Function to scrape the text from a page
def scrape_page(url):
    driver.get(url)
    time.sleep(3)  # Wait for the page to load
    # Extract all the text from the body of the page
    page_text = driver.find_element(By.TAG_NAME, 'body').text
    return page_text

# Start scraping for each city
all_text = ""  # This will hold the collected text

for city in cities:
    base_url = f"https://www.la-psiholog.ro/{city}/"
    page_number = 1

    while True:
        if page_number == 1:
            url = base_url  # First page doesn't have a page number
        else:
            url = f"{base_url}pag--{page_number}"

        print(f"Scraping {url}")
        page_text = scrape_page(url)
        all_text += page_text + "\n\n"  # Append the text with spacing between pages

        # Stop after scraping a predefined number of pages (e.g., 11), or you can add another condition to stop scraping
        if page_number == 20:
            print(f"No more pages to scrape for {city}.")
            break

        page_number += 1

# After scraping, close the driver
driver.quit()

# Save the scraped text to a file
with open("scraped_text.txt", "w", encoding="utf-8") as f:
    f.write(all_text)

print("Scraping completed. Text saved to scraped_text.txt")
