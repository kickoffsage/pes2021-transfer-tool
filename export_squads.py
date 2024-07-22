import argparse
from src.team_utils import read_team_data
from src.csv_utils import read_csv_mapping, write_to_csv

def main():
    parser = argparse.ArgumentParser(description='Extract team and player data from binary file.')
    parser.add_argument('binary_file_path', type=str, help='Path to the binary file.')
    parser.add_argument('csv_output_path', type=str, help='Path to the output CSV file.')
    parser.add_argument('team_names_csv', type=str, help='Path to the CSV file containing team names.')
    parser.add_argument('player_names_csv', type=str, help='Path to the CSV file containing player names.')

    args = parser.parse_args()

    team_entries_start_offset = 10307144
    team_entries_end_offset = 10520143

    teams_data = read_team_data(
        args.binary_file_path,
        team_entries_start_offset,
        team_entries_end_offset
    )

    team_names = read_csv_mapping(args.team_names_csv)
    player_names = read_csv_mapping(args.player_names_csv)

    write_to_csv(args.csv_output_path, teams_data, team_names, player_names)

if __name__ == "__main__":
    main()
