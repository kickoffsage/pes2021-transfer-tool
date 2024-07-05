import requests
from bs4 import BeautifulSoup
import csv
import sys

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

def read_input_csv(filename):
    """Reads the input CSV containing team and player data."""
    data = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def match_data(transfers, reference_data):
    """Matches the transfer data with the reference data to find player and team IDs."""
    ref_players = {row['PlayerName']: row['PlayerID'] for row in reference_data}
    ref_teams = {row['TeamName']: row['TeamID'] for row in reference_data}

    matched_transfers = []
    for transfer in transfers:
        date, player, from_club, to_club = transfer
        player_id = ref_players.get(player, 'N/A')
        from_team_id = ref_teams.get(from_club, 'N/A')
        to_team_id = ref_teams.get(to_club, 'N/A')
        matched_transfers.append([date, player_id, player, from_team_id, from_club, to_team_id, to_club])

    return matched_transfers

def write_to_csv(transfers, filename='temp/latest_transfermarkt_transfers.csv'):
    """Writes the transfer data to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['TransferDate', 'PlayerID', 'PlayerName', 'FromTeamID', 'FromTeamName', 'ToTeamID', 'ToTeamName'])
        writer.writerows(transfers)
    print(f'Data has been written to {filename}')


def main(input_csv):
    # League ID to filter transfers
    league = 'GB1' # English Premier League

    # URL of the Transfermarkt page to scrape
    url = 'https://www.transfermarkt.com/transfers/neuestetransfers/statistik/plus/?plus=1&galerie=0&wettbewerb_id=%s&land_id=&selectedOptionInternalType=nothingSelected&minMarktwert=0&maxMarktwert=500.000.000&minAbloese=0&maxAbloese=500.000.000&yt0=Show' % (league)
    
    html_content = fetch_transfermarkt_page(url)
    transfers = parse_transfers(html_content)
    reference_data = read_input_csv(input_csv)
    matched_transfers = match_data(transfers, reference_data)
    write_to_csv(matched_transfers)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python transfermarkt_scraper.py <input_csv>")
    else:
        input_csv = sys.argv[1]
        main(input_csv)
