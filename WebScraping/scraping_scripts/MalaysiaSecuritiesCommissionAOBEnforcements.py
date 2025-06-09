import requests
import pandas as pd
import pymongo
import os
from bs4 import BeautifulSoup

# URL of the webpage
url = "https://www.sc.com.my/aob/aobs-sanctions"

# Fetch the webpage
response = requests.get(url, verify=False)
soup = BeautifulSoup(response.content, "html.parser")

# Find all tables
tables = soup.find_all("table")

all_data = []

for table in tables:
    headers = [th.text.strip() for th in table.find_all("th")]

    # Extract rows
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = [td.text.strip() for td in tr.find_all("td")]
        if len(cells) == len(headers):
            rows.append(cells)

    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=headers)

    # Drop unwanted columns
    drop_cols = ["No.", "No"]
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors="ignore")

    # Rename columns
    rename_map = {
        "Auditor": "fullname",
        "Nature of Breach": "type_of",
        "Nature of Misconduct": "category",
        "Action Taken": "charge",
        "Brief Description of Misconduct": "description",
        "Brief Description of Breach": "otherinfo"
    }
    df = df.rename(columns=rename_map)

    # Merge relevant columns into 'otherinfo'
    AOB_date = "Date of AOB's Action"
    DateOfAction = "Date of Action"

    if AOB_date in df.columns and DateOfAction in df.columns:
        df["otherinfo"] = df[AOB_date].fillna("") + "," + df[DateOfAction].fillna("")
        df = df.drop(columns=[AOB_date, DateOfAction], errors="ignore")

    # Drop 'Parties Involved' column if it exists
    df = df.drop(columns=["Parties Involved", "Date of AOB's Action", "Date of Action"], errors="ignore")

    all_data.append(df)

# Combine all tables into one DataFrame
final_df = pd.concat(all_data, ignore_index=True)

# Add new columns
final_df["aliases"] = ""
final_df["entity"] = "WATCHLIST"
final_df["source_name"] = "Malaysia Securities Commission AOB Enforcements"
final_df["ninumber"] = ""
final_df["passport"] = ""
final_df["country"] = "Malaysia"
final_df["address"] = ""

# Save to CSV
csv_filename = "sanctions_data.csv"
final_df.to_csv(csv_filename, index=False)
print("✅ Data extracted and saved to 'sanctions_data.csv'.")

# ✅ **Connect to MongoDB**
from db import get_db
db = get_db()
collection = db["MALAYSIA_AOBE_WATCHLIST"]

# Retrieve existing fullnames from MongoDB for duplicate check
existing_fullnames = set(collection.distinct("fullname"))

# Convert DataFrame to list of dictionaries and filter out duplicates
new_data = [record for record in final_df.to_dict(orient="records") if record["fullname"] not in existing_fullnames]

# Insert only new records
if new_data:
    collection.insert_many(new_data)
    print(f"✅ {len(new_data)} new records inserted into MongoDB.")
else:
    print("✅ No new records to insert (all names already exist).")

# Clean up CSV file
os.remove(csv_filename)
print("✅ Data processing completed successfully.")
