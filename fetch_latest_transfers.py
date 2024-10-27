import requests
from bs4 import BeautifulSoup
import csv
import sys
from rapidfuzz import fuzz, process
import os


def fetch_transfermarkt_page(url):
    """Fetches the HTML content of the Transfermarkt page."""
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Check for request errors
    return response.text


def parse_transfers(html):
    """Parses the HTML content to extract transfer data."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"class": "items"})
    rows = table.find_all("tr", {"class": ["odd", "even"]})

    transfers = []

    for row in rows:
        columns = row.find_all("td", recursive=False)

        date = columns[5].text.strip()
        player = columns[0].find("a").text.strip()
        from_club = columns[3].find_all("img")[0].get("title").strip()
        to_club = columns[4].find_all("img")[0].get("title").strip()

        transfers.append([date, player, from_club, to_club])

    return transfers


def get_next_page_url(soup):
    """Gets the URL of the next page if it exists, otherwise returns None."""
    next_page_tag = soup.select_one("li.tm-pagination__list-item--icon-next-page > a")
    if next_page_tag:
        return "https://www.transfermarkt.com" + next_page_tag["href"]
    return None


def read_input_csv(filename):
    """Reads the input CSV containing team and player data."""
    data = []
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data


def get_best_match(query, choices):
    """Finds the best match for a query string within a list of choices and returns the match and the confidence score."""
    best_match = process.extractOne(query, choices, scorer=fuzz.ratio)
    return best_match[0], best_match[1] if best_match else (None, 0)


def match_data(transfers, players_data, teams_data, confidence_threshold=80):
    """Matches the transfer data with the reference data to find player and team IDs."""
    ref_players = {row["PlayerName"]: row["PlayerID"] for row in players_data}
    ref_teams = {row["TeamName"]: row["TeamID"] for row in teams_data}

    matched_transfers = []
    for transfer in transfers:
        date, player, from_club, to_club = transfer

        player_name_match, player_confidence = get_best_match(
            player, ref_players.keys()
        )
        from_team_match, from_team_confidence = get_best_match(
            from_club, ref_teams.keys()
        )
        to_team_match, to_team_confidence = get_best_match(to_club, ref_teams.keys())

        if player_confidence >= confidence_threshold:
            player_id = ref_players.get(player_name_match, 0)
            player_name = player_name_match
        else:
            player_id = 0
            player_name = player

        if from_team_confidence >= confidence_threshold:
            from_team_id = ref_teams.get(from_team_match, 0)
            from_team_name = from_team_match
        else:
            from_team_id = 0
            from_team_name = from_club

        if to_team_confidence >= confidence_threshold:
            to_team_id = ref_teams.get(to_team_match, 0)
            to_team_name = to_team_match
        else:
            to_team_id = 0
            to_team_name = to_club

        matched_transfers.append(
            [
                date,
                player_id,
                player_name,
                player_confidence,
                from_team_id,
                from_team_name,
                from_team_confidence,
                to_team_id,
                to_team_name,
                to_team_confidence,
            ]
        )

    return matched_transfers


def write_to_csv(transfers, filename="latest_transfermarkt_transfers.csv"):
    """Writes the transfer data to a CSV file."""
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Create a 'dist' directory in the same folder as the script
    dist_dir = os.path.join(script_dir, "dist")
    os.makedirs(dist_dir, exist_ok=True)

    # Create the full path for the output file
    full_path = os.path.join(dist_dir, filename)

    print(f"Attempting to write to file: {full_path}")

    try:
        with open(full_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "TransferDate",
                    "PlayerID",
                    "PlayerName",
                    "PlayerMatchConfidence",
                    "FromTeamID",
                    "FromTeamName",
                    "FromTeamMatchConfidence",
                    "ToTeamID",
                    "ToTeamName",
                    "ToTeamMatchConfidence",
                ]
            )
            writer.writerows(transfers)
        print(f"Data has been written to {full_path}")
    except Exception as e:
        print(f"Error writing to file: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Script directory: {script_dir}")
        print(f"Dist directory: {dist_dir}")


def main(players_csv, teams_csv, confidence_threshold=80, league="GB1"):
    # Base URL of the Transfermarkt page to scrape
    base_url = (
        "https://www.transfermarkt.com/transfers/neuestetransfers/statistik/plus/?plus=1&galerie=0&wettbewerb_id=%s&land_id=&selectedOptionInternalType=nothingSelected&minMarktwert=0&maxMarktwert=500.000.000&minAbloese=0&maxAbloese=500.000.000&yt0=Show"
        % league
    )

    current_url = base_url
    all_transfers = []

    while current_url:
        print(current_url)
        html_content = fetch_transfermarkt_page(current_url)
        transfers = parse_transfers(html_content)
        all_transfers.extend(transfers)

        soup = BeautifulSoup(html_content, "html.parser")
        current_url = get_next_page_url(soup)

    players_data = read_input_csv(players_csv)
    teams_data = read_input_csv(teams_csv)
    matched_transfers = match_data(
        all_transfers, players_data, teams_data, confidence_threshold
    )
    write_to_csv(matched_transfers)


if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print(
            "Usage: python fetch_latest_transfermarkt_transfers.py <players_csv> <teams_csv> [confidence_threshold] [league]"
        )
        print("Optional parameters:")
        print(
            "  [confidence_threshold]: Integer (default 80). Minimum confidence level for matching."
        )
        print(
            "  [league]: String (default 'GB1' for English Premier League). League ID for transfers."
        )
        print("\nExample:")
        print(
            "  python fetch_latest_transfermarkt_transfers.py players.csv teams.csv 85 ES1"
        )
    else:
        players_csv = sys.argv[1]
        teams_csv = sys.argv[2]
        confidence_threshold = int(sys.argv[3]) if len(sys.argv) == 4 else 80
        league = sys.argv[4] if len(sys.argv) > 4 else "GB1"  # English Premier League
        main(players_csv, teams_csv, confidence_threshold, league)
