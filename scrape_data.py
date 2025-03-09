from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import json
import logging
import coloredlogs

# Constants
LOG_LEVEL = 'INFO'
NUM_MORE_CLICKS = 10
# URL of the Shopify event page
URL = "https://shop.app/events/shop-canada"

# Set up colored logs
coloredlogs.install(level=LOG_LEVEL)

# Create a logger
logger = logging.getLogger(__name__)

# Set up the WebDriver (Chrome in this case)
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Run headless for faster scraping (no browser window)
# doesn't work w headless

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

logger.info(f"Opening URL: {URL} with Selenium 🏂")
# Open the page
driver.get(URL)
logger.info("Page opened successfully ✅")

# Function to load more brands (click the "more" button)
def load_more_brands():
    try:
        more_buttons = driver.find_elements(By.XPATH, '//button[span[contains(text(), "More")]]')
        if len(more_buttons) == 0:
            raise Exception('No more "More" buttons found')
        logger.info(f"Found {len(more_buttons)} 'More' buttons on the page")
        for more_button in more_buttons:
            driver.execute_script("arguments[0].click();", more_button) # use JS to click the button (bc it actually works)
        logger.info(f"Clicked {len(more_buttons)} 'More' button(s) ✅")
        time.sleep(3)  # Wait for the page to load the new brands
    except Exception as e:
        print("No more brands to load or error:", e)

# Load initial brands and keep clicking "More" until no more brands are shown
logger.info(f'Clicking "More" buttons {NUM_MORE_CLICKS} times to load more brands... 🏂')
for _ in tqdm(range(NUM_MORE_CLICKS)):
    load_more_brands()
    try:
        # Check if "More" button is still present, if not, break
        more_buttons = driver.find_elements(By.XPATH, '//button[span[contains(text(), "More")]]')
    except Exception:
        break
logger.info(f"Finished loading brands, clicked more buttons {NUM_MORE_CLICKS} times ✅")

logger.info("Parsing the page content using BeautifulSoup 🥣")
# Parse the page content using BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")
logger.info("Page content parsed successfully ✅")

logger.info("Extracting sections... 📝")
# 1. Find all section titles (e.g., "Women")
sections = soup.find_all('div', class_='flex flex-col mb-space-36 md:mb-space-48')
logger.info(f"Found {len(sections)} sections on the page")

logger.info("Extracting section titles and URLs... 📝")
# 2. Extract section titles and their associated URLs
section_data = {}

i = 0
for section in tqdm(sections):
    # Extract the section title (e.g., "Women")
    title_tag = section.find('h4', class_='md:text-sectionTitle')
    if title_tag:
        section_title = title_tag.text.strip()
        
        # Find all URLs within this section (relative URLs)
        relative_urls = [a['href'] for a in section.find_all('a', href=True) if a['href'].startswith('/m/')]
        
        # Convert relative URLs to absolute URLs
        absolute_urls = [urljoin(URL, url) for url in relative_urls]
        
        # Store section title and URLs in a list
        section_data[i] = {
            'section_title': section_title,
            'urls': list(set(absolute_urls))  # Remove duplicates
        }
        i += 1

logger.info("Section titles and URLs extracted successfully ✅")

logger.info(f"Titles + URLs:\n{json.dumps(section_data, indent=4)}")

logger.info("Scraping individual brand pages... 🏂")

# Function to scrape details from each brand's individual page
def scrape_brand_details(brand_url):
    driver.get(brand_url)
    time.sleep(3)  # Allow the page to load

    soup = BeautifulSoup(driver.page_source, "html.parser")

    try:
        # Extract the title
        title = soup.find('p', class_='font-bodyTitleLarge').text.strip()
        # Extract the rating
        rating = soup.find('p', class_='font-captionBold').text.strip().split()[0]
        # Extract the volume of ratings (number in parentheses)
        volume_of_ratings = soup.find('span', class_='font-captionBold').text.strip()[1:-1]  # Removing parentheses
        # Extract the bio
        bio = soup.find('p', class_='font-bodySmall').text.strip()
        # Extract the URL
        url = soup.find('a', {'data-testid': 'store-actions-website-link'})['href']
        clean_url = url.split('?')[0]
    except AttributeError:
        title = "N/A"
        rating = "N/A"
        volume_of_ratings = "N/A"
        bio = "No bio available"
        url = "N/A"

    return {
        'title': title,
        'rating': rating,
        'volume_of_ratings': volume_of_ratings,
        'bio': bio,
        'url': clean_url,
        'shop_app_url': brand_url
    }

logger.info("Scraping details for each brand... 🏂")
# Iterate over each section, scrape details for each brand, and print results
for ix, section in tqdm(section_data.items()):
    logger.info(f"Scraping details for section: {section['section_title']}... 🏂")

    details_per_brand = []
    for brand_url in tqdm(section['urls']):
    # for brand_url in tqdm(section['urls'][:3]): # Limit to 3 brands per section for testing
        logger.info(f"Scraping details for: {brand_url}")
        brand_details = scrape_brand_details(brand_url)
        details_per_brand.append(brand_details)
    
    section_data[ix]['details_per_brand'] = details_per_brand


logger.info("Scraping complete ✅")        

logger.info("Saving the data to a JSON file... 📂")
with open('./data/shop_canada_data.json', 'w') as f:
    json.dump(section_data, f, indent=4)
logger.info("Data saved to ./data/shop_canada_data.json ✅")

# Close the WebDriver
driver.quit()

logger.info('Done! 🎉')