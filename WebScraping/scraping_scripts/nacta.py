from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os
from pymongo import MongoClient

# Source URL
source_url = "https://nfs.nacta.gov.pk/"

# Setup driver
driver = webdriver.Chrome()
driver.get(source_url)

# Wait for page to load
wait = WebDriverWait(driver, 10)

all_data = []

while True:
    table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table')))
    rows = table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) == 6:
            all_data.append({
                #"sr_no": cols[0].text.strip(),
                "fullname": cols[1].text.strip(),
                "fatherName": cols[2].text.strip(),
                "uniquekey": cols[3].text.strip(),
                "province": cols[4].text.strip(),
                "district": cols[5].text.strip(),
                "entity": "NACTA",
                "source_id": source_url,
                "delisted":"false"
            })

    try:
        next_btn = driver.find_element(By.XPATH, '//button[text()="NEXT"]')
        if next_btn.get_attribute("disabled"):
            break
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(2)
    except:
        break

# Save to CSV
csv_filename = "nacta_nfs_data.csv"
df = pd.DataFrame(all_data)
df.to_csv(csv_filename, index=False, encoding='utf-8-sig')

# Insert into MongoDB with duplicate checking
client = MongoClient("mongodb://localhost:27017/")
db = client["AML"]
collection = db["NACTA"]

new_records = []
for record in df.to_dict("records"):
    if not collection.find_one({
        "fullname": record["fullname"]
    }):
        new_records.append(record)

if new_records:
    collection.insert_many(new_records)
    print(f"Inserted {len(new_records)} new records into MongoDB collection 'NACTA'.")
else:
    print("No new records to insert. All entries already exist.")

# Delete CSV file
if os.path.exists(csv_filename):
    os.remove(csv_filename)
    print(f"Deleted file: {csv_filename}")
else:
    print(f"File not found: {csv_filename}")

driver.quit()
