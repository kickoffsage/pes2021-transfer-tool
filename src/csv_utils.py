import csv

def read_csv_mapping(file_path):
    mapping = {}
    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
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

def write_to_csv(output_path, teams_data, team_names, player_names):
    with open(output_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['TeamID', 'TeamName', 'PlayerID', 'PlayerName', 'ShirtNumber'])

        for team_id, team_player_ids, shirt_numbers in teams_data:
            team_name = team_names.get(team_id, 'Unknown Team')
            for team_player_id, shirt_number in zip(team_player_ids, shirt_numbers):
                player_name = player_names.get(team_player_id, 'Empty Player' if team_player_id == 0 else 'Unknown Player')
                csvwriter.writerow([team_id, team_name, team_player_id, player_name, shirt_number])
