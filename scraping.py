import requests
import pandas as pd
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin 

input_file = "School Data.xlsx"
df_file = pd.read_excel(input_file)

all_data = []

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}

for index, row in df_file.iterrows():
    url = row["Website"]
    new_row = row.to_dict()
    new_row["Email"] = ""
    new_row["Phone"] = ""

    try:
        if pd.isna(url):
            all_data.append(new_row)
            continue

        print(f"Scraping: {url}")

        url = str(url).strip()

        if not url.startswith("http"):
            url = "https://" + url

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()

            emails = list(set(re.findall(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",text)))
            phones = list(set(re.findall(r"\b(?:\+91[\s-]?|0)?[6-9]\d{9}\b",text)))

            if not emails and not phones:
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    if "contact" in href.lower() or "about" in href.lower():
                        contact_url = urljoin(url, href)
                        print(f"Checking contact page: {contact_url}")
                        try:
                            contact_response = requests.get(contact_url, headers=headers, timeout=10)
                            if contact_response.status_code == 200:
                                contact_soup = BeautifulSoup(contact_response.text, "html.parser")
                                contact_text = contact_soup.get_text()

                                emails = list(set(re.findall(
                                    r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
                                    contact_text)))

                                phones = list(set(re.findall(
                                    r"\b(?:\+91[\s-]?|0)?[6-9]\d{9}\b",
                                    contact_text)))

                                if emails or phones:
                                    break
                        except:
                            continue

            max_len = max(len(emails), len(phones), 1)
            for i in range(max_len):
                temp_row = row.to_dict()
                temp_row["Email"] = emails[i] if i < len(emails) else ""
                temp_row["Phone"] = phones[i] if i < len(phones) else ""

                all_data.append(temp_row)
        else:
            print(f"Response request status is not 200")
            all_data.append(new_row)
            time.sleep(2)

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        all_data.append(new_row)

df_output = pd.DataFrame(all_data)
df_output.to_excel("Output Data.xlsx", index=False)

print("Scraping completed. Data saved to File")