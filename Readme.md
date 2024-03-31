# Zalando Private Scraper

This application is designed to automate the process of scraping campaign data from Zalando Private. It includes functionality for filtering specific items, sending notifications via Pushover based on specific keywords, and more. The application can run both in a headless mode for deployment on servers and in a GUI mode for development and testing purposes.

## Features

- Automated login and navigation through Zalando Private.
- Filters campaigns based on configurable criteria such as `Homme` category and shoe sizes.
- Sends notifications for items matching specific keywords via Pushover.
- Configurable for headless operation on servers or GUI mode for local testing.
- Extracts and saves campaign data into a CSV file for further analysis or display.
- Webapp to view all items after you merge csvs

## Installation

### Prerequisites

- Python 3.10

### Setup Steps

1. **Clone the repository or download the source code.**

2. **Install Python 3.10**: Make sure Python 3.10 is installed on your machine. You can download it from the [official Python website](https://www.python.org/downloads/release/python-3100/).

3. **Install Required Packages**: Navigate to the project directory and run the following command to install the required Python packages:
``` pip install -r requirements.txt  ```
4. **Create a `config.py` File**: Based on the `config.example.py` template provided, create a `config.py` file in the project directory. Fill in your details and preferences .
5. **Running the application**:To start the scraper, run the following command in the terminal:
``` python bot.py ```

## Configuration Explanation

Each configuration variable in the `config.py` file serves a specific purpose. Here's a breakdown of each:

### Zalando Credentials
- `USERNAME`: Your Zalando account email.
- `PASSWORD`: Your Zalando account password.

### Pushover Credentials
- `PUSHOVER_KEY`: Your Pushover user key to receive notifications.
- `PUSHOVER_APP_TOKEN`: The application token/key from Pushover.

### Filters
- `filter_homme`: Set to `True` to only scrape items categorized under "Homme" (Men). Default is `False`.
- `filter_shoe_sizes`: Set to `True` to enable shoe size filtering. Default is `False`.
- `shoe_sizes`: A list of desired shoe sizes to filter by if `filter_shoe_sizes` is `True`.

### Notification Config
- `enable_notifications`: Enable Pushover notifications for matched items. Default is `False`.
- `keywords`: List of keywords to match in item descriptions for notifications. Notifications are sent for items containing any of the listed keywords.

### Timeout
- `TIMEOUT_TIME`: The maximum time in seconds to wait for page elements to load before timing out. Adjust based on your internet speed and server response times.

### Literals
- `LOGIN_URL`: The Zalando login URL. It's advised not to change this value.
- `success_url`: The URL to confirm a successful login. It's advised not to change this value.

### Headless Mode
- `headless`: Run the browser in headless mode when set to `True`. Useful for running the script on a server without a GUI. Default is `False`.

Make sure to edit the `config.py` file with your own information before running the application.
