import requests
from bs4 import BeautifulSoup
import csv

def fetch_transfermarkt_page(url):
    """Fetches the HTML content of the Transfermarkt page."""
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Check for request errors

    return response.text

def parse_transfers(html):
    """Parses the HTML content to extract transfer data."""
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': 'items'})
    rows = table.find_all('tr', {'class': ['odd', 'even']})
    
    transfers = []

    for row in rows:
        columns = row.find_all('td', recursive=False)
        
        date = columns[5].text.strip()
        player = columns[0].find('a').text.strip()
        from_club = columns[3].find_all('a')[1].get('title').strip()
        to_club = columns[4].find_all('a')[1].get('title').strip()
        
        transfers.append([date, player, from_club, to_club])

    return transfers

def write_to_csv(transfers, filename='temp/latest_transfermarkt_transfers.csv'):
    """Writes the transfer data to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['TransferDate', 'PlayerName', 'FromTeamName', 'ToTeamName'])
        writer.writerows(transfers)
    print(f'Data has been written to {filename}')


def main():
    # League ID to filter transfers
    league = 'GB1' # English Premier League

    # URL of the Transfermarkt page to scrape
    url = 'https://www.transfermarkt.com/transfers/neuestetransfers/statistik/plus/?plus=1&galerie=0&wettbewerb_id=%s&land_id=&selectedOptionInternalType=nothingSelected&minMarktwert=0&maxMarktwert=500.000.000&minAbloese=0&maxAbloese=500.000.000&yt0=Show' % (league)
    
    html_content = fetch_transfermarkt_page(url)
    transfers = parse_transfers(html_content)
    write_to_csv(transfers)

if __name__ == '__main__':
    main()