import requests
from bs4 import BeautifulSoup
import csv
import sys
from fuzzywuzzy import fuzz

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
        from_club = columns[3].find_all('img')[0].get('title').strip()
        to_club = columns[4].find_all('img')[0].get('title').strip()
        
        transfers.append([date, player, from_club, to_club])

    return transfers

def get_next_page_url(soup):
    """Gets the URL of the next page if it exists, otherwise returns None."""
    next_page_tag = soup.select_one('li.tm-pagination__list-item--icon-next-page > a')
    if next_page_tag:
        return 'https://www.transfermarkt.com' + next_page_tag['href']
    return None

def read_input_csv(filename):
    """Reads the input CSV containing team and player data."""
    data = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def get_best_match(query, choices):
    """Finds the best match for a query string within a list of choices and returns the match and the confidence score."""
    best_match = None
    highest_ratio = 0
    for choice in choices:
        ratio = fuzz.token_sort_ratio(query, choice)
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = choice
    return best_match, highest_ratio

def match_data(transfers, players_data, teams_data):
    """Matches the transfer data with the reference data to find player and team IDs."""
    ref_players = {row['PlayerName']: row['PlayerID'] for row in players_data}
    ref_teams = {row['TeamName']: row['TeamID'] for row in teams_data}

    matched_transfers = []
    for transfer in transfers:
        date, player, from_club, to_club = transfer

        player_name_match, player_confidence = get_best_match(player, ref_players.keys())
        from_team_match, from_team_confidence = get_best_match(from_club, ref_teams.keys())
        to_team_match, to_team_confidence = get_best_match(to_club, ref_teams.keys())

        player_id = ref_players.get(player_name_match, 'N/A')
        from_team_id = ref_teams.get(from_team_match, 'N/A')
        to_team_id = ref_teams.get(to_team_match, 'N/A')

        matched_transfers.append([
            date,
            player_id, player_name_match, player_confidence,
            from_team_id, from_team_match, from_team_confidence,
            to_team_id, to_team_match, to_team_confidence
        ])

    return matched_transfers

def write_to_csv(transfers, filename='temp/latest_transfermarkt_transfers.csv'):
    """Writes the transfer data to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'TransferDate',
            'PlayerID', 'PlayerName', 'PlayerMatchConfidence',
            'FromTeamID', 'FromTeamName', 'FromTeamMatchConfidence',
            'ToTeamID', 'ToTeamName', 'ToTeamMatchConfidence'
        ])
        writer.writerows(transfers)
    print(f'Data has been written to {filename}')

def main(players_csv, teams_csv):
    # League ID to filter transfers
    league = 'GB1'  # English Premier League

    # Base URL of the Transfermarkt page to scrape
    base_url = 'https://www.transfermarkt.com/transfers/neuestetransfers/statistik/plus/?plus=1&galerie=0&wettbewerb_id=%s&land_id=&selectedOptionInternalType=nothingSelected&minMarktwert=0&maxMarktwert=500.000.000&minAbloese=0&maxAbloese=500.000.000&yt0=Show' % league
    
    current_url = base_url
    all_transfers = []

    while current_url:
        print(current_url)
        html_content = fetch_transfermarkt_page(current_url)
        transfers = parse_transfers(html_content)
        all_transfers.extend(transfers)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        current_url = get_next_page_url(soup)

    players_data = read_input_csv(players_csv)
    teams_data = read_input_csv(teams_csv)
    matched_transfers = match_data(all_transfers, players_data, teams_data)
    write_to_csv(matched_transfers)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python fetch_latest_transfermarkt_transfers.py <players_csv> <teams_csv>")
    else:
        players_csv = sys.argv[1]
        teams_csv = sys.argv[2]
        main(players_csv, teams_csv)
