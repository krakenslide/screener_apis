import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from dotenv import load_dotenv
from io import BytesIO
import os

load_dotenv()

url = os.getenv("SCRAPER_URL")
csrf_token = os.getenv("CSRF_TOKEN")
session_id = os.getenv("SESSION_ID")

cookies = {
    "csrftoken": csrf_token,
    "sessionid": session_id,
    "theme": "dark"
}


def fetch_detailed_data():
    response = requests.get(url, cookies=cookies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        table_div = soup.find('div', class_="responsive-holder fill-card-width")
        if table_div:
            rows = table_div.find_all('tr')
            all_data = []
            main_headers = []

            links = []
            for row in rows[1:]:
                cells = row.find_all('td')
                if len(cells) > 2:
                    link = cells[2].find('a')
                    if link and 'href' in link.attrs:
                        links.append("https://www.screener.in" + link['href'])

            for idx, link in enumerate(links):
                print(f"Processing: {link}")
                link_response = requests.get(link, cookies=cookies)

                if link_response.status_code == 200:
                    link_soup = BeautifulSoup(link_response.content, 'html.parser')
                    profit_loss_section = link_soup.find('section', id="profit-loss")
                    if profit_loss_section:
                        last_div = profit_loss_section.find_all('div')[-1]
                        tables = last_div.find_all('table', class_="ranges-table")

                        row_data = []
                        for table_idx, table in enumerate(tables):
                            rows = table.find_all('tr')
                            if len(rows) >= 5:
                                # Dynamically update headers
                                for i in range(1, 5):
                                    th_text = rows[0].find('th').get_text(strip=True)
                                    td_text = rows[i].find('td').get_text(strip=True)
                                    column_name = f"{th_text} {td_text}"
                                    if column_name not in main_headers:
                                        main_headers.append(column_name)

                                # Add data to the row
                                for i in range(1, 5):
                                    cells = rows[i].find_all('td')
                                    if len(cells) > 1:
                                        row_data.append(cells[1].get_text(strip=True))

                        if len(row_data) > 0:
                            while len(row_data) < len(main_headers):
                                row_data.append("")  # Pad to match header length
                            all_data.append(row_data)
                time.sleep(2)

            return pd.DataFrame(all_data, columns=main_headers)
        else:
            print("Table div not found in the HTML.")
    else:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")
    return pd.DataFrame()


def fetch_main_table():
    response = requests.get(url, cookies=cookies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        table_div = soup.find('div', class_="responsive-holder fill-card-width")
        if table_div:
            rows = table_div.find_all('tr')
            table_data = []
            max_columns = 0

            for i, row in enumerate(rows):
                cells = row.find_all(['th', 'td'])

                # Skip the second <td> for data rows
                if i > 0:  # Data rows
                    row_data = [cell.get_text(strip=True) for j, cell in enumerate(cells) if j != 1]
                else:  # Header row
                    row_data = [cell.get_text(strip=True) for cell in cells]

                table_data.append(row_data)
                max_columns = max(max_columns, len(row_data))

            # Ensure all rows have the same number of columns
            for i in range(len(table_data)):
                if len(table_data[i]) < max_columns:
                    table_data[i].extend(["" for _ in range(max_columns - len(table_data[i]))])

            headers = table_data[0]
            data_rows = table_data[1:]
            return pd.DataFrame(data_rows, columns=headers)
        else:
            print("Table div not found in the HTML.")
    else:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")
    return pd.DataFrame()


def merge_tables(df1, df2):
    try:
        merged_df = pd.concat([df1, df2], axis=1)
        return merged_df
    except ValueError as e:
        print(f"Error merging tables: {e}")
        return pd.DataFrame()


def generate_excel():
    detailed_data = fetch_detailed_data()
    main_table = fetch_main_table()

    if detailed_data.empty or main_table.empty:
        return None

    merged_data = merge_tables(main_table, detailed_data)
    output = BytesIO()
    merged_data.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return output
