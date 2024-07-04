import struct
import csv
import argparse

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

            teams_data.append((team_id, team_player_ids))

            # Skip the next 80 bytes (shirt numbers)
            f.seek(80, 1)

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

def write_to_csv(output_path, teams_data, team_names, player_names):
    with open(output_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        # Write the header
        csvwriter.writerow(['TeamID', 'TeamName', 'TeamPlayerID', 'PlayerName'])
        # Write the teamID, teamName, teamPlayerID, and playerName
        for team_id, team_player_ids in teams_data:
            team_name = team_names.get(team_id, 'Unknown Team')
            for team_player_id in team_player_ids:
                player_name = player_names.get(team_player_id, 'Empty Player' if team_player_id == 0 else 'Unknown Player')
                csvwriter.writerow([team_id, team_name, team_player_id, player_name])

def main():
    parser = argparse.ArgumentParser(description='Extract team and player data from binary file.')
    parser.add_argument('binary_file_path', type=str, help='Path to the binary file.')
    parser.add_argument('csv_output_path', type=str, help='Path to the output CSV file.')
    parser.add_argument('team_names_csv', type=str, help='Path to the CSV file containing team names.')
    parser.add_argument('player_names_csv', type=str, help='Path to the CSV file containing player names.')
    
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

    write_to_csv(args.csv_output_path, teams_data, team_names, player_names)

if __name__ == "__main__":
    main()
