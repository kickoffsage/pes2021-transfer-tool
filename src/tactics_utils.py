import struct

def update_tactics_for_team(binary_file_path, team_id, player_index):
    tactics_start_offset = 10524800
    team_block_size = 628
    team_id_size = 4
    padding_size = 480
    player_indices_size = 40

    with open(binary_file_path, 'r+b') as f:
        current_offset = tactics_start_offset
        
        while True:
            f.seek(current_offset)
            current_team_id = struct.unpack('<I', f.read(team_id_size))[0]

            if current_team_id == team_id:
                f.seek(current_offset + team_id_size + padding_size)
                player_indices = list(f.read(player_indices_size))
                
                if player_index in player_indices:
                    # Find the index of the player index to be removed
                    index_to_remove = player_indices.index(player_index)
                    # Remove the player index and shift the rest
                    player_indices.pop(index_to_remove)
                    player_indices = player_indices[:player_index] + [player_index] + player_indices[player_index:]
                    
                    # Write back the modified player indices
                    f.seek(current_offset + team_id_size + padding_size)
                    f.write(bytes(player_indices))
                break
            
            current_offset += team_block_size
