import struct
import csv
import argparse
import shutil

def read_team_data(file_path, team_entries_start_offset, team_entries_end_offset):
    teams_data = []

    with open(file_path, 'rb') as f:
        f.seek(team_entries_start_offset)

        while f.tell() < team_entries_end_offset:
            # Read the next 4 bytes for teamID in little-endian format
            team_id_bytes = f.read(4)
            if len(team_id_bytes) < 4:
                break
            team_id = struct.unpack('<I', team_id_bytes)[0]

            # Read the next 160 bytes for playerIDs in little-endian format
            team_player_ids = []
            for _ in range(40):
                player_id_bytes = f.read(4)
                if len(player_id_bytes) < 4:
                    break
                player_id = struct.unpack('<I', player_id_bytes)[0]
                team_player_ids.append(player_id)

            # Read the next 80 bytes for shirtNumbers in little-endian format
            shirt_numbers = []
            for _ in range(40):
                shirt_number_bytes = f.read(2)
                if len(shirt_number_bytes) < 2:
                    break
                shirt_number = struct.unpack('<H', shirt_number_bytes)[0]
                shirt_numbers.append(shirt_number)

            teams_data.append((team_id, team_player_ids, shirt_numbers))

            # Skip the next 40 bytes to reach next team
            f.seek(40, 1)

    return teams_data

def read_csv_mapping(file_path):
    mapping = {}
    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header
        for row in csvreader:
            id_ = int(row[0])
            name = row[1]
            mapping[id_] = name
    return mapping

def read_transfers(file_path):
    transfers = []
    with open(file_path, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            player_id = int(row['PlayerID'])
            from_team_id = int(row['FromTeamID'])
            to_team_id = int(row['ToTeamID'])
            transfers.append((player_id, from_team_id, to_team_id))
    return transfers

def apply_transfers(teams_data, transfers):
    team_dict = {team_id: (team_player_ids, shirt_numbers) for team_id, team_player_ids, shirt_numbers in teams_data}
    
    for player_id, from_team_id, to_team_id in transfers:
        if from_team_id in team_dict and to_team_id in team_dict:
            from_team_players, from_team_shirts = team_dict[from_team_id]
            to_team_players, to_team_shirts = team_dict[to_team_id]
            
            if player_id in from_team_players:
                # Remove player from the old team
                index = from_team_players.index(player_id)
                from_team_players[index] = 0  # Mark as empty
                from_team_shirts[index] = 0

                # Add player to the new team if there's an empty spot
                try:
                    new_index = to_team_players.index(0)  # Find the first empty spot
                    to_team_players[new_index] = player_id
                    to_team_shirts[new_index] = 0  # Assuming the shirt number needs to be reassigned
                except ValueError:
                    print(f"No empty spot for player {player_id} in team {to_team_id}. Transfer skipped.")

    return [(team_id, team_player_ids, shirt_numbers) for team_id, (team_player_ids, shirt_numbers) in team_dict.items()]

def write_to_csv(output_path, teams_data, team_names, player_names):
    with open(output_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['TeamID', 'TeamName', 'PlayerID', 'PlayerName', 'ShirtNumber'])

        for team_id, team_player_ids, shirt_numbers in teams_data:
            team_name = team_names.get(team_id, 'Unknown Team')
            for team_player_id, shirt_number in zip(team_player_ids, shirt_numbers):
                player_name = player_names.get(team_player_id, 'Empty Player' if team_player_id == 0 else 'Unknown Player')
                csvwriter.writerow([team_id, team_name, team_player_id, player_name, shirt_number])

def rewrite_binary(original_file_path, new_file_path, teams_data, team_entries_start_offset):
    shutil.copyfile(original_file_path, new_file_path)
    
    with open(new_file_path, 'r+b') as f:
        f.seek(team_entries_start_offset)
        
        for team_id, team_player_ids, shirt_numbers in teams_data:
            # Write team ID
            f.write(struct.pack('<I', team_id))
            
            # Write player IDs
            for player_id in team_player_ids:
                f.write(struct.pack('<I', player_id))
            
            # Write shirt numbers
            for shirt_number in shirt_numbers:
                f.write(struct.pack('<H', shirt_number))
            
            # Skip 40 bytes
            f.seek(40, 1)

def main():
    parser = argparse.ArgumentParser(description='Extract team and player data from binary file.')
    parser.add_argument('binary_file_path', type=str, help='Path to the binary file.')
    parser.add_argument('csv_output_before_path', type=str, help='Path to the output CSV file before transfers.')
    parser.add_argument('csv_output_after_path', type=str, help='Path to the output CSV file after transfers.')
    parser.add_argument('team_names_csv', type=str, help='Path to the CSV file containing team names.')
    parser.add_argument('player_names_csv', type=str, help='Path to the CSV file containing player names.')
    parser.add_argument('transfers_csv', type=str, help='Path to the CSV file containing transfers.')
    parser.add_argument('new_binary_file_path', type=str, help='Path to the new binary file.')

    args = parser.parse_args()

    team_entries_start_offset = 10307144  # Hardcoded start offset value
    team_entries_end_offset = 10520143   # Hardcoded end offset value

    teams_data = read_team_data(
        args.binary_file_path,
        team_entries_start_offset,
        team_entries_end_offset
    )

    team_names = read_csv_mapping(args.team_names_csv)
    player_names = read_csv_mapping(args.player_names_csv)
    transfers = read_transfers(args.transfers_csv)

    write_to_csv(args.csv_output_before_path, teams_data, team_names, player_names)

    teams_data = apply_transfers(teams_data, transfers)

    write_to_csv(args.csv_output_after_path, teams_data, team_names, player_names)
    rewrite_binary(args.binary_file_path, args.new_binary_file_path, teams_data, team_entries_start_offset)

if __name__ == "__main__":
    main()
