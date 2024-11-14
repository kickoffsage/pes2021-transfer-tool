import argparse
import os
import subprocess

from crypt_utils import decrypt_save_file, encrypt_save_file
from csv_utils import read_csv_mapping, read_transfers, write_to_csv
from team_utils import read_team_data, read_team_id_and_name, write_team_data
from transfer_utils import apply_transfers


def main():
    parser = argparse.ArgumentParser(
        description="Apply transfers to binary file and output the updated team and player data."
    )
    parser.add_argument(
        "original_save_file_path", type=str, help="Path to the original save file."
    )
    parser.add_argument(
        "new_save_file_path", type=str, help="Path to the new save file."
    )
    parser.add_argument(
        "csv_output_path", type=str, help="Path to the output CSV file after transfers."
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

    teams_start_offset = 0x8ED2FC
    teams_end_offset = 0x958DA3

    try:
        temp_binary_folder_path, temp_binary_file_path = decrypt_save_file(
            args.original_save_file_path
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error decrypting save file: {e}")
        exit(1)

    teams_data = read_team_data(
        temp_binary_file_path, team_entries_start_offset, team_entries_end_offset
    )

    team_names = read_team_id_and_name(
        temp_binary_file_path, teams_start_offset, teams_end_offset
    )
    player_names = read_csv_mapping(args.player_names_csv)
    transfers = None
    if os.path.isdir(args.transfers_csv):
        # If it's a directory, read all CSV files in the directory
        transfers = []
        for file_name in os.listdir(args.transfers_csv):
            if file_name.endswith(".csv"):
                file_path = os.path.join(args.transfers_csv, file_name)
                transfers.extend(read_transfers(file_path))
    else:
        # If it's a single CSV file, read transfers from that file
        transfers = read_transfers(args.transfers_csv)

    teams_data = apply_transfers(
        temp_binary_file_path, teams_data, transfers, player_names
    )

    write_to_csv(args.csv_output_path, teams_data, team_names, player_names)

    write_team_data(temp_binary_file_path, teams_data, team_entries_start_offset)

    encrypt_save_file(temp_binary_folder_path, args.new_save_file_path)


if __name__ == "__main__":
    main()
