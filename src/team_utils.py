import struct

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
                # if player_id == 0x00000000:
                #     player_id = 0  # Interpret 0x00000000 as 0 for internal processing
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
