import pandas as pd
import time
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class NuforcScraper:
    def __init__(self):
        self.url = 'https://nuforc.org/subndx/?id=all'
        self.output_file = '../data/raw/nuforc_reports.csv'
        self.batch_size = 100
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def extract_row_data(self, row):
        try:
            cells = row.find_all('td')
            if not cells or len(cells) < 10:
                return None
            
            # Get the details link from first column
            link_cell = cells[0].find('a')
            link = link_cell['href'] if link_cell else ''
            
            return {
                'link': link,
                'occurred': cells[1].text.strip(),
                'city': cells[2].text.strip(),
                'state': cells[3].text.strip(),
                'country': cells[4].text.strip(),
                'shape': cells[5].text.strip(),
                'summary': cells[6].text.strip(),
                'reported': cells[7].text.strip(),
                'media': cells[8].text.strip(),
                'explanation': cells[9].text.strip()
            }
        except Exception as e:
            logging.error(f"Error extracting row data: {e}")
            return None

    def save_to_csv(self, records, mode='w'):
        df = pd.DataFrame(records)
        # Ensure columns are in correct order
        columns = ['link', 'occurred', 'city', 'state', 'country', 
                  'shape', 'summary', 'reported', 'media', 'explanation']
        df = df[columns]
        df.to_csv(self.output_file, index=False, mode=mode, header=(mode=='w'))
        logging.info(f"Saved {len(records)} records to {self.output_file}")

    def get_last_record_number(self):
        try:
            if os.path.exists(self.output_file):
                df = pd.read_csv(self.output_file)
                return len(df)
            return 0
        except Exception as e:
            logging.error(f"Error reading existing file: {e}")
            return 0

    def scrape_reports(self):
        logging.info(f"Opening URL: {self.url}")
        self.driver.get(self.url)
        
        # Calculate starting page
        last_record_count = self.get_last_record_number()
        start_page = (last_record_count // 100) + 1
        total_records = last_record_count
        page = 1  # Always start at page 1
        
        logging.info(f"Need to get to page {start_page} (existing records: {last_record_count})")
        
        # Flag to determine if we've already written the header
        first_write = not os.path.exists(self.output_file) or last_record_count == 0
        
        while True:
            try:
                # Wait for table load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "wpdt-c"))
                )
                time.sleep(2)  # Extra wait for stability
                
                # Only scrape and save if we're at or past our start page
                if page >= start_page:
                    logging.info(f"Scraping page {page} (Total records so far: {total_records})")
                    
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    table = soup.find('table')
                    rows = table.find_all('tr')[1:]
                    logging.info(f"Found {len(rows)} rows")
                    
                    page_records = []
                    for row in rows:
                        data = self.extract_row_data(row)
                        if data:
                            page_records.append(data)
                    
                    if page_records:
                        total_records += len(page_records)
                        # Use 'w' mode only if we're writing for the first time
                        save_mode = 'w' if first_write else 'a'
                        self.save_to_csv(page_records, mode=save_mode)
                        first_write = False  # After first write, switch to append mode
                        logging.info(f"Progress: {total_records}/151,495 records ({(total_records/151495)*100:.1f}%)")
                else:
                    logging.info(f"Skipping page {page}, need to get to page {start_page}")
                
                # Wait for table to be ready again
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "wpdt-c"))
                )
                
                # Try to find and click the next button with retries
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        next_button = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "a.next.paginate_button"))
                        )
                        
                        if "disabled" in next_button.get_attribute("class"):
                            logging.info("Reached last page")
                            return
                            
                        # Scroll and click with small delays
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                        time.sleep(1)
                        self.driver.execute_script("arguments[0].click();", next_button)
                        time.sleep(3)
                        break
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise
                        logging.warning(f"Click attempt {attempt + 1} failed, retrying...")
                        time.sleep(2)
                
                page += 1
                
            except Exception as e:
                logging.error(f"Error on page {page}: {e}")
                # Try to recover
                self.driver.refresh()
                time.sleep(5)
                continue
                
        logging.info(f"Scraping complete. Total records: {total_records}")
        self.driver.quit()

if __name__ == '__main__':
    scraper = NuforcScraper()
    scraper.scrape_reports()