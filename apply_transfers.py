import argparse
import shutil
from src.csv_utils import read_csv_mapping, read_transfers, write_to_csv
from src.team_utils import read_team_data, write_team_data
from src.transfer_utils import apply_transfers


def main():
    parser = argparse.ArgumentParser(
        description="Apply transfers to binary file and output the updated team and player data."
    )
    parser.add_argument(
        "original_binary_file_path", type=str, help="Path to the original binary file."
    )
    parser.add_argument(
        "new_binary_file_path", type=str, help="Path to the new binary file."
    )
    parser.add_argument(
        "csv_output_path", type=str, help="Path to the output CSV file after transfers."
    )
    parser.add_argument(
        "team_names_csv", type=str, help="Path to the CSV file containing team names."
    )
    parser.add_argument(
        "player_names_csv",
        type=str,
        help="Path to the CSV file containing player names.",
    )
    parser.add_argument(
        "transfers_csv", type=str, help="Path to the CSV file containing transfers."
    )

    args = parser.parse_args()

    team_entries_start_offset = 10307144
    team_entries_end_offset = 10520143

    shutil.copyfile(args.original_binary_file_path, args.new_binary_file_path)

    teams_data = read_team_data(
        args.new_binary_file_path, team_entries_start_offset, team_entries_end_offset
    )

    team_names = read_csv_mapping(args.team_names_csv)
    player_names = read_csv_mapping(args.player_names_csv)
    transfers = read_transfers(args.transfers_csv)

    teams_data = apply_transfers(
        args.new_binary_file_path, teams_data, transfers, player_names
    )

    write_to_csv(args.csv_output_path, teams_data, team_names, player_names)

    write_team_data(args.new_binary_file_path, teams_data, team_entries_start_offset)


if __name__ == "__main__":
    main()
