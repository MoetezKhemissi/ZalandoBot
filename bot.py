from lowLevel import *



if __name__ == "__main__":

    csv_columns = ['link', 'name', 'initial_price', 'final_price', 'out_of_stock', 'image_url']

    campaigns_dir = "campaigns"

    logging.basicConfig(filename='campaign_scraper.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
    logging.info("Starting the scraper...")

    logging.info("Creating campaigns directory ..")
    create_campaigns_dir(campaigns_dir)

    driver = setup_driver()

    logging.info("Logging into Zalando ..")
    #Normal way to login if you are not using headless
    login_to_site(driver, USERNAME, PASSWORD)
    #Hacky way to force login
    #load_session_data(driver)
    time.sleep(2)
    while True:
            logging.info("Fetching new campaigns...")
            get_and_process_campaigns(driver, campaigns_dir, csv_columns)

            logging.info("Finished processing. Waiting for 5 minutes before checking again...")
            time.sleep(300)  # Wait for 5 minutes

            logging.info("Revisiting the main page to check for new campaigns.")
            go_to_main_page(driver)
