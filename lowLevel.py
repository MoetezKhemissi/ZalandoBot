from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium_stealth import stealth
import random
from selenium.webdriver.common.keys import Keys
import string
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re
import csv
import os
import logging
import requests
from config import *

# Constants for login


def send_notification(item):
    if not enable_notifications:
        return

    item_description = item.get('name', '').lower()
    if keywords:
        if not any(keyword.lower() in item_description for keyword in keywords):
            return  # Skip sending notification if no keywords match

    app_token = PUSHOVER_APP_TOKEN
    user_key = PUSHOVER_KEY
    message = f"Name: {item['name']}\nInitial Price: {item['initial_price']}\nFinal Price: {item['final_price']}\nOut of Stock: {item['out_of_stock']}\nURL: https://www.zalando-prive.fr{item['link']}"
    image_url = item['image_url']

    data = {
        "token": app_token,
        "user": user_key,
        "message": message,
        "url": image_url,
        "url_title": "Item Image"
    }

    response = requests.post("https://api.pushover.net/1/messages.json", data=data)
    if response.status_code == 200:
        print("Notification sent successfully.")
    else:
        print(f"Failed to send notification. Response: {response.text}")
def click_taille_filter(driver):
    try:
        taille_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Taille')]]"))
        )
        taille_button.click()
        time.sleep(1.5)
        return True
    except TimeoutException:
        logging.info("Taille filter not found.")
        return False

def click_categories_tab(driver):
    try:
        categories_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "category-tab-selector"))
        )
        categories_tab.click()
        time.sleep(1.5)  # Wait for the categories to expand
        return True
    except TimeoutException:
        logging.info("Categories tab not found.")
        return False

def click_homme_button(driver):
    try:
        homme_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@aria-label='Homme']//button[contains(@class, 'MainCategoryListstyles__StyledButton')]"))
        )
        homme_button.click()
        time.sleep(1.5)  # Wait for the page to filter
        return True
    except TimeoutException:
        logging.info("Homme button not found.")
        return False


def legacy_browser():
    options = webdriver.EdgeOptions() 
    options.add_argument('--disable-blink-features=AutomationControlled')
    if headless:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
    return webdriver.Edge(options=options)

def login(driver, email, password):
    driver.get(LOGIN_URL)
    time.sleep(3)
    # Click on "Connexion" button
    connexion_button = WebDriverWait(driver, TIMEOUT_TIME).until(
        EC.presence_of_element_located((By.XPATH, '//span[text()="Connexion"]/parent::span'))
    )
    connexion_button.click()
    time.sleep(3)
    # Click on the actual login prompt to get to the email/password fields
    WebDriverWait(driver, TIMEOUT_TIME).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-labelledby="sso-login-lounge"]'))
    ).click()
    time.sleep(3)
    # Enter email
    email_input = WebDriverWait(driver, TIMEOUT_TIME).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
    )
    slow_type(email_input,email)
    time.sleep(3)
    # Enter password
    password_input = WebDriverWait(driver, TIMEOUT_TIME).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
    )
    slow_type(password_input,password)
    time.sleep(3)
    # Click on login button
    #TODO retry if uncessful
    for attempt in range(3):
        try:
            login_button = WebDriverWait(driver, TIMEOUT_TIME).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="login_button"]'))
            )
            login_button.click()

            # Wait for redirection to occur with a timeout
            WebDriverWait(driver, 10).until(EC.url_to_be(success_url))
            logging.info("Successfully logged in and redirected.")
            return  # If redirection is successful, exit the function
        except TimeoutException:
            # If the URL check times out, it means redirection did not occur as expected
            logging.warning("Redirection did not occur as expected. Retrying...")
            if attempt < 2:  # Wait before retrying unless it's the last attempt
                time.sleep(3)
    
    # If the function reaches this point, login or redirection was not successful
    logging.error("Failed to log in or redirect to the expected URL after 3 attempts.")

def get_campaign_hrefs(driver):
    # Regular expression to match the specific campaign URL pattern
    pattern = re.compile(r'https://www\.zalando-prive\.fr/campaigns/\w+/[0-9]$')
    
    # Find all <a> elements with hrefs containing "/campaigns/"
    campaign_links = driver.find_elements(By.XPATH, '//a[contains(@href, "/campaigns/")]')
    
    filtered_urls = set()  # Using a set to automatically remove duplicates
    for link in campaign_links:
        href = link.get_attribute('href')
        # Check if the href matches the specified pattern
        if pattern.match(href):
            filtered_urls.add(href)  # Add to set, duplicates are ignored
    logging.info("URL to process :")
    logging.info(filtered_urls)

    return list(filtered_urls)
def slow_type(element, text):
    """Send a text to an element one character at a time with a delay."""
    i = 0
    
    for character in text:
        i= i+1
        if i % 3 == 0:
            delay=random.uniform(0.3, 0.4)
        if i % 3 == 1:
            delay=random.uniform(0.1, 0.2)
        if i % 3 == 2:
                delay=random.uniform(0.2, 0.3)
        if i % 5 ==4:
            delay=random.uniform(0.1, 0.3)
            element.send_keys(random.choice(string.ascii_letters))
            delay=random.uniform(0.1, 0.3)
            element.send_keys(Keys.BACK_SPACE)
        
        element.send_keys(character)
        time.sleep(delay)

def extract_item_details(driver):
    """
    Extracts details of each item on the current campaign page,
    including the URL of the primary image for each item.
    """
    once_test_notif=0
    items = driver.find_elements(By.CSS_SELECTOR, 'li.Articlestyles__ArticleWrapper-sc-hib3gs-0')
    extracted_data = []
    for item in items:
        try:
            link = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            name = item.find_element(By.CSS_SELECTOR, 'div.Articlestyles__ArticleNameWrapper-sc-hib3gs-2').text
            initial_price = item.find_element(By.CSS_SELECTOR, 'span.eWHHNq').text
            final_price = item.find_element(By.CSS_SELECTOR, 'span.CaNPv').text
            out_of_stock = 'Épuisé' in item.text
            image_element = item.find_element(By.CSS_SELECTOR, 'img.ArticleImagestyles__PrimaryImage-sc-1l1eoim-1')
            image_url = image_element.get_attribute('src')
            #------------Notification Block ----------------

            send_notification({
                'link': link,
                'name': name,
                'initial_price': initial_price,
                'final_price': final_price,
                'out_of_stock': out_of_stock,
                'image_url': image_url  # Include the image URL
            })
            #-------------------------------------------------
            extracted_data.append({
                'link': link,
                'name': name,
                'initial_price': initial_price,
                'final_price': final_price,
                'out_of_stock': out_of_stock,
                'image_url': image_url  # Include the image URL
            })

        except NoSuchElementException:
            # Log or handle items where any detail is missing, if necessary
            pass
    return extracted_data


def scroll_until_no_new_items(driver):
    """
    Scrolls down the page until no new items are loaded after two scrolls.
    """
    previous_height = driver.execute_script("return document.body.scrollHeight")
    consecutive_no_change_count = 0
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Allow time for any new items to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == previous_height:
            consecutive_no_change_count += 1
        else:
            consecutive_no_change_count = 0  # Reset counter if new items were loaded
        
        if consecutive_no_change_count >= 2:
            break  # Exit loop if no new items after two scrolls
        
        previous_height = new_height
def create_empty_csv(csv_file):
    """
    Explicitly creates an empty CSV file for a campaign.
    This function is a wrapper around 'create_csv' to clarify its purpose
    in the context where it's used.
    """
    create_csv(csv_file)  # Calls 'create_csv' to create the file with headers
    logging.info(f"Empty CSV file created: {csv_file}")


def create_csv(csv_file):
    csv_columns = ['link', 'name', 'initial_price', 'final_price', 'out_of_stock', 'image_url']

    try:
        with open(csv_file, 'x', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
    except FileExistsError:
        pass  # File already exists, no need to add the header

def extract_campaign_id(url):

    match = re.search(r'/campaigns/([^/]+)/\d$', url)
    if match:
        return match.group(1)  # Return the campaign ID
    return None


def setup_driver():
    driver = legacy_browser()
    driver.maximize_window()
    return driver

def login_to_site(driver, username, password):
    try:
        login(driver, username, password)
        logging.info("Done Login")
    except Exception as e:
        logging.error('Could not login : ' , e)

def create_campaigns_dir(directory):
    os.makedirs(directory, exist_ok=True)

def get_and_process_campaigns(driver, campaigns_dir, csv_columns):
    campaign_hrefs = get_campaign_hrefs(driver)
    for campaign_href in campaign_hrefs:
        campaign_id = extract_campaign_id(campaign_href)
        if campaign_id:
            csv_file_path = os.path.join(campaigns_dir, f"{campaign_id}.csv")
            if not os.path.exists(csv_file_path):
                logging.info(f"New campaign found, processing: {campaign_href}")
                process_campaign_page(driver, campaign_href, campaign_id, campaigns_dir, csv_columns)  # Pass campaign_id as an argument
            else:
                logging.info(f"Campaign already processed, skipping: {campaign_href}")
        else:
            logging.error(f"Could not extract campaign ID from URL: {campaign_href}")


def process_campaign_page(driver, campaign_href, campaign_id, campaigns_dir, csv_columns):
    logging.info(f"Started processing URL: {campaign_href}")
    driver.get(campaign_href)
    time.sleep(1.5)  # Let the page load

    should_create_empty_csv = False  # Flag to determine whether to create an empty CSV

    # Conditionally filter by "Homme" category if requested
    if filter_homme:
        if not click_categories_tab(driver):
            logging.info("Skipping campaign due to missing 'Categories' tab.")
            create_empty_csv(os.path.join(campaigns_dir, f"{campaign_id}.csv"))
            return
        if not click_homme_button(driver):
            logging.info("Skipping campaign due to missing 'Homme' category.")
            create_empty_csv(os.path.join(campaigns_dir, f"{campaign_id}.csv"))
            return

    # Conditionally filter by shoe size if requested
    if filter_shoe_sizes:
        if not click_taille_filter(driver):
            logging.info("Missing 'Taille' filter. An empty CSV will be created.")
            should_create_empty_csv = True
        elif not click_chaussures_filter(driver):
            logging.info("Missing 'Chaussures' filter. An empty CSV will be created.")
            should_create_empty_csv = True
        else:
            if not select_shoe_sizes(driver, shoe_sizes):
                logging.info("Desired shoe sizes not found. An empty CSV will be created.")
                should_create_empty_csv = True

    if not should_create_empty_csv:
        scroll_until_no_new_items(driver)
        logging.info("Done scrolling.")
        item_details = extract_item_details(driver)

        if not item_details:
            logging.info("No items extracted. An empty CSV will be created.")
            should_create_empty_csv = True

    csv_file_path = os.path.join(campaigns_dir, f"{campaign_id}.csv")

    if should_create_empty_csv:
        create_empty_csv(csv_file_path)
    else:
        logging.info(f"Processing {csv_file_path} with extracted item details.")
        write_item_details_to_csv(csv_file_path, item_details, csv_columns)


def click_filter_element(driver, element_css_selector, wait_time=1.5):
    """
    Clicks on a filter element identified by its CSS selector.
    """
    try:
        filter_element = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, element_css_selector))
        )
        filter_element.click()
        time.sleep(wait_time)  # Wait for the specified time after clicking
    except TimeoutException:
        logging.info(f"Element with selector {element_css_selector} not found.")
        return False  # Indicate the element was not found/clicked
    return True

def click_chaussures_filter(driver):
    try:
        chaussures_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Chaussures')]]"))
        )
        chaussures_button.click()
        time.sleep(1.5)
        return True
    except TimeoutException:
        logging.info("Chaussures filter not found.")
        return False

def select_shoe_sizes(driver, size_values):
    size_found = False  # Initialize a flag to track if any size is found and clicked

    for size_value in size_values:
        try:
            # Locate the span that directly contains the size text, then find the preceding input checkbox
            size_label = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, f"//span[contains(@class, 'LabelWrapper') and contains(text(), '{size_value}')]/preceding-sibling::input[@type='checkbox']"))
            )
            if not size_label.is_selected():
                driver.execute_script("arguments[0].click();", size_label)
                size_found = True  # Mark that we've found and clicked at least one size
                time.sleep(1.5)  # Wait a bit after clicking
        except TimeoutException:
            logging.info(f"Size {size_value} checkbox not found.")

    if not size_found:
        logging.error("None of the specified shoe sizes were found.")
        return False

    return True




def write_item_details_to_csv(csv_file, item_details, csv_columns):
    # Check if your CSV file exists and write the header if it doesn't
    file_exists = os.path.exists(csv_file)
    with open(csv_file, 'a', newline='', encoding='utf-8') as csvfile:
        logging.info("Writing to csv %s ...", csv_file)
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        if not file_exists:
            writer.writeheader()
        for detail in item_details:
            writer.writerow(detail)
            
def go_to_main_page(driver):
    driver.get(LOGIN_URL)
    time.sleep(3)  # Adjust timing as necessary