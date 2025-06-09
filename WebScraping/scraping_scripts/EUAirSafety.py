import requests
import glob
import os
import pandas as pd
from pymongo import MongoClient
import re  # Importing the regular expression module

# URL of the file
url = "https://transport.ec.europa.eu/document/download/67b75752-d144-4366-9f4a-c04157840211_en?filename=air-safety-list-2024-12-13.xlsx"

# Send a GET request to the URL
response = requests.get(url, verify=False)

# Check if the request was successful
if response.status_code == 200:
    filename = "air-safety-list-2024-12-13.xlsx"
    with open(filename, "wb") as file:
        file.write(response.content)
    print(f"File downloaded successfully as {filename}.")

    downloaded_files = glob.glob("air-safety-list*.xlsx")
    
    if downloaded_files:
        file_to_open = downloaded_files[0]
        data = pd.read_excel(file_to_open, header=5)
        data.columns = data.columns.str.strip()

        unwanted_strings = [
            "Name of the legal entity of the air carrier as indicated on its AOC (and its trading name, if different)",
            "Air Operator Certificate ('AOC') Number or Operating Licence Number",
            "ICAO three letter designator",
            "State of the Operator",
            "(RDC)",
            "AIR TANZANIA,TCAA/AOC/001,ATC,Tanzania",
            "Air carriers listed in Annex A could be permitted to exercise traffic rights by using wet-leased aircraft of an air carrier which is not subject to an operating ban, provided that the relevant safety standards are complied with."
        ]

        for unwanted_string in unwanted_strings:
            data = data[~data.apply(lambda row: row.astype(str).str.contains(unwanted_string).any(), axis=1)]
        
        pattern = r"^All air carriers certified by the authorities with responsibility for regulatory oversight of.*"
        data = data[~data.apply(lambda row: row.astype(str).str.contains(pattern).any(), axis=1)]
        
        data = data.iloc[:-2]
        data.columns = ['fullname', 'ninumber', 'otherinfo', 'country']

        data['passport']=""
        data['title']=""
        data['aliases'] = ""
        data['type_of'] = ""
        data['category'] = ""
        data['dob'] = ""
        data['place_birth'] = ""
        data['position']=""
        data['address']=""
        data['listedon'] = ""
        data['entity'] = "OTHERS"
        data['source_name'] = "From various other sources"

        output_filename = "air_safety_list_cleaned.csv"
        data.to_csv(output_filename, index=False)
        print(f"Data saved to {output_filename}")

        from db import get_db
        db = get_db()    
        
		
        collection = db["EU_AIRSAFETY_OTHERS"]#OTHERS1"]
        
        data_dict = data.to_dict(orient='records')

        # Check for duplicates before inserting
        new_records = []
        for record in data_dict:
            if not collection.find_one({"fullname": record["fullname"]}):
                new_records.append(record)

        if new_records:
            collection.insert_many(new_records)
            print(f"Inserted {len(new_records)} new records into MongoDB.")
        else:
            print("No new records found to insert.")

        try:
            os.remove(file_to_open)
            print(f"Deleted the intermediate file: {file_to_open}")
            os.remove(output_filename)
            print(f"Deleted the intermediate file: {output_filename}")
        except Exception as e:
            print(f"Error removing files: {e}")
else:
    print(f"Failed to retrieve the file. Status code: {response.status_code}")
