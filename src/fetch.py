from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import sqlite3

date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
cookies = {
    'epex-data-use-agreed': '1',
    'cookie-agreed-version': '1.0.0',
    'cookie-agreed-categories': '["functional"]',
    'cookie-agreed': '2',
}

request_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    # 'Cookie': 'epex-data-use-agreed=1; cookie-agreed-version=1.0.0; cookie-agreed-categories=["functional"]; cookie-agreed=2',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

areas = ['FR','BE', 'DE', 'NL']


res1_0 =  BeautifulSoup("<td>res1</td>", "html.parser")
res2_0 =  BeautifulSoup("<td>res2</td>", "html.parser")
res3_0 =  BeautifulSoup("<td>res3</td>", "html.parser")

def daily_fetch(params):
    response = requests.get('https://www.epexspot.com/en/market-data', params=params, cookies=cookies, headers= request_headers)
    soup = BeautifulSoup(response.content, "html.parser")
    a = soup.find(class_="table-container").find("ul").find_all("li")
    b = soup.find(class_="table-container").find("tbody").find_all("tr")
    l = list(zip(a,b))

    for index, i in enumerate(l):
        if "child" in i[0]['class']:
            l[index] += (res1_0,)
        elif "lvl-1" in i[0]['class']:
            l[index] += (res2_0,)
        elif "lvl-2" in i[0]['class']:
            l[index] += (res3_0,)

    for item in (body := [[g.text.strip().replace("\n", "//") for g in i] for i in l]):
        item[1] = item[1].split("//")

    headers = [i.text.strip() for i in soup.find(class_="table-container").find("thead").find_all("th")]
    headers.append('Resolution')

    return headers, body, soup


def create_database(headers, body, area):
    conn = sqlite3.connect("src/stash1.db")
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {area} (
            Date TEXT,
            Time TEXT,
            "{headers[1]}" INTEGER,
            "{headers[2]}" INTEGER,
            "{headers[3]}" INTEGER,
            "{headers[4]}" INTEGER,
            "{headers[5]}" INTEGER,
            "{headers[6]}" INTEGER,
            "{headers[7]}" INTEGER,
            "{headers[8]}" INTEGER,
            "{headers[9]}" INTEGER,
            "{headers[10]}" INTEGER,
            "{headers[11]}" INTEGER,
            PRIMARY KEY(Date, Time)
            
        )
    ''')

    for time, values, resolution in body:
        cursor.execute(f"INSERT OR IGNORE INTO {area} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (date, time, *values, resolution))
    
    conn.commit()
    conn.close()

def verify_table(soup):
    metadata = soup.find(class_='table-container').find('h2').text.replace("\n", "").replace(" ", "").split(">")
    print(metadata)
    try:
        assert metadata[0] == 'Continuous'
        assert metadata[2] == area
        assert datetime.strptime(metadata[3], '%d%B%Y').strftime("%Y-%m-%d") == date
    except AssertionError as e:
        print(e)
        override = input("Override Error?: ")


if __name__ == "__main__":
    for area in areas:
        params = {
            'market_area': area,
            'auction': '',
            'trading_date': '',
            'delivery_date': date,
            'underlying_year': '',
            'modality': 'Continuous',
            'sub_modality': '',
            'technology': '',
            'data_mode': 'table',
            'period': '',
            'production_period': '',
            'product': '15',
        }
        head, body, soup = daily_fetch(params)
        verify_table(soup)
        create_database(head, body, area)