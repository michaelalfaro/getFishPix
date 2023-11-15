import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time


# Paths to the CSV file and output directory
csv_file_path = 'fishpix.csv'
output_path = '/fishpix_output'

# Read the CSV file
fishpix_data = pd.read_csv(csv_file_path)

# Ensure the output directory exists
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Base URL of the search page
search_url = 'https://fishpix.kahaku.go.jp/fishimage-e/search'

# Base URL for the image links (assumed from the provided HTML)
base_image_url = 'https://fishpix.kahaku.go.jp'

# Headers to simulate a browser visit
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Iterate over each row in the DataFrame
for index, row in fishpix_data.iterrows():
    # Construct the data payload for the GET request
    params = {
        'SPECIES': row['species'],
        'FAMILY': row['family'],
        'PHOTO_ID': row['img_file']  # Assuming this column contains the Photograph No.: KPM-NR
    }

    # Send the GET request
    response = requests.get(search_url, params=params, headers=headers)
    
    # If the request is successful
    if response.status_code == 200:
        # Parse the result page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the `img` tag with the `src` attribute containing the image link
        image_tag = soup.find('img', src=lambda s: 'photos' in s if s else False)
        
        if image_tag and 'src' in image_tag.attrs:
            # Construct the full image URL
            image_link = base_image_url + image_tag['src'].replace('..', '')
            
            # Download the image
            image_response = requests.get(image_link, stream=True)
            if image_response.status_code == 200:
                image_file_path = os.path.join(output_path, f"{row['img_file']}.jpg")
                with open(image_file_path, 'wb') as f:
                    f.write(image_response.content)
                print(f"Downloaded image for {row['img_file']} to {image_file_path}")
            else:
                print(f"Failed to download image for {row['img_file']} (Status Code: {image_response.status_code})")
        else:
            print(f"No image tag found for {row['img_file']}")

    else:
        print(f"Search failed for {row['img_file']} (Status Code: {response.status_code})")

    # Throttle the requests to avoid overloading the server
    time.sleep(1)  # Sleep for 1 second between requests