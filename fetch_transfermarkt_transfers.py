import requests
from bs4 import BeautifulSoup
import csv
import sys
from fuzzywuzzy import fuzz


def fetch_html(url):
    """Fetches the HTML content of the given URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Check for request errors
    return response.text


def search_team(team_name):
    """Searches for a team on Transfermarkt and returns the best match's slug and ID."""
    search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={team_name}"
    html_content = fetch_html(search_url)
    soup = BeautifulSoup(html_content, "html.parser")
    search_results = soup.select("a[href*='startseite/verein/']")

    best_match = None
    highest_ratio = 0
    for result in search_results:
        result_name = result.text.strip()
        ratio = fuzz.token_sort_ratio(team_name, result_name)
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = result

    if best_match:
        href_parts = best_match["href"].split("/")
        team_slug = href_parts[1]
        team_id = href_parts[-1]
        return team_slug, team_id

    return None, None


def parse_transfers(html, team_name):
    """Parses the HTML content to extract transfer data."""
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table", {"class": "items"})

    transfers = []

    for i, table in reversed(list(enumerate(tables))):
        rows = table.find_all("tr", {"class": ["odd", "even"]})

        for row in rows:
            columns = row.find_all("td", recursive=False)

            date = "N/A"
            player = columns[1].find("a").text.strip()
            current_club = team_name
            other_club = columns[4].find_all("img")[0].get("title").strip()

            if i == 0:
                transfers.append([date, player, other_club, current_club])
            else:
                transfers.append([date, player, current_club, other_club])

    return transfers


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
            player_id = ref_players.get(player_name_match, "N/A")
            player_name = player_name_match
        else:
            player_id = 0
            player_name = player

        if from_team_confidence >= confidence_threshold:
            from_team_id = ref_teams.get(from_team_match, "N/A")
            from_team_name = from_team_match
        else:
            from_team_id = 0
            from_team_name = from_club

        if to_team_confidence >= confidence_threshold:
            to_team_id = ref_teams.get(to_team_match, "N/A")
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


def write_to_csv(transfers, team_name, filename_prefix="dist/by_team/"):
    """Writes the transfer data to a CSV file."""
    filename = f"{filename_prefix}{team_name}_transfers.csv"
    with open(filename, "w", newline="", encoding="utf-8") as file:
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
    print(f"Data has been written to {filename}")


def read_input_csv(filename):
    """Reads the input CSV containing team and player data."""
    data = []
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data


def main(team_name, players_csv, teams_csv, confidence_threshold=80):
    team_slug, team_id = search_team(team_name)
    if not team_slug or not team_id:
        print(f"Team '{team_name}' not found.")
        return

    url = f"https://www.transfermarkt.com/{team_slug}/transfers/verein/{team_id}/saison_id/2024"

    html_content = fetch_html(url)
    transfers = parse_transfers(html_content, team_name)

    players_data = read_input_csv(players_csv)
    teams_data = read_input_csv(teams_csv)
    matched_transfers = match_data(
        transfers, players_data, teams_data, confidence_threshold
    )
    write_to_csv(matched_transfers, team_name)


if __name__ == "__main__":
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print(
            "Usage: python fetch_team_transfers.py <team_name> <players_csv> <teams_csv> [confidence_threshold]"
        )
    else:
        team_name = sys.argv[1]
        players_csv = sys.argv[2]
        teams_csv = sys.argv[3]
        confidence_threshold = int(sys.argv[4]) if len(sys.argv) == 5 else 80
        teams_data = read_input_csv(teams_csv)
        for team in teams_data:
            team_name = team["TeamName"]
            main(team_name, players_csv, teams_csv, confidence_threshold)
