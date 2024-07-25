from src.tactics_utils import update_tactics_for_team


def replace_with_last_non_zero(players, shirts, index):
    """Replace the player at the given index with the last non-zero player in the list."""
    last_non_zero_index = next((i for i in range(len(players) - 1, -1, -1) if players[i] != 0), index)
    players[index] = players[last_non_zero_index]
    shirts[index] = shirts[last_non_zero_index]
    players[last_non_zero_index] = 0
    shirts[last_non_zero_index] = 0
    return players, shirts, last_non_zero_index

def apply_transfers(binary_file_path, teams_data, transfers):
    team_dict = {team_id: (team_player_ids, shirt_numbers) for team_id, team_player_ids, shirt_numbers in teams_data}
    
    for player_id, from_team_id, to_team_id in transfers:
        if from_team_id in team_dict and to_team_id in team_dict:
            from_team_players, from_team_shirts = team_dict[from_team_id]
            to_team_players, to_team_shirts = team_dict[to_team_id]
            
            if player_id in from_team_players:
                # Remove player from the old team
                index = from_team_players.index(player_id)
                from_team_players, from_team_shirts, last_non_zero_index = replace_with_last_non_zero(from_team_players, from_team_shirts, index)
                team_dict[from_team_id] = (from_team_players, from_team_shirts)

                update_tactics_for_team(binary_file_path, from_team_id, last_non_zero_index)

                # Add player to the new team if there's an empty spot
                try:
                    new_index = to_team_players.index(0)  # Find the first empty spot
                    to_team_players[new_index] = player_id
                    
                    # Find an unused shirt number
                    used_shirt_numbers = set(to_team_shirts)
                    new_shirt_number = 1
                    while new_shirt_number in used_shirt_numbers or new_shirt_number == 0:
                        new_shirt_number += 1
                    to_team_shirts[new_index] = new_shirt_number  # Assign new shirt number

                    team_dict[to_team_id] = (to_team_players, to_team_shirts)

                except ValueError:
                    print(f"No empty spot for player {player_id} in team {to_team_id}. Transfer skipped.")

    return [(team_id, team_player_ids, shirt_numbers) for team_id, (team_player_ids, shirt_numbers) in team_dict.items()]
