from src.tactics_utils import update_tactics_for_team


def replace_with_last_non_zero(players, shirts, index):
    """Replace the player at the given index with the last non-zero player in the list."""
    last_non_zero_index = next(
        (i for i in range(len(players) - 1, -1, -1) if players[i] != 0), index
    )
    players[index] = players[last_non_zero_index]
    shirts[index] = shirts[last_non_zero_index]
    players[last_non_zero_index] = 0
    shirts[last_non_zero_index] = 0
    return players, shirts, last_non_zero_index


def apply_transfers(binary_file_path, teams_data, transfers):
    team_dict = {
        team_id: (team_player_ids, shirt_numbers)
        for team_id, team_player_ids, shirt_numbers in teams_data
    }

    for (
        player_id,
        player_name,
        from_team_id,
        from_team_name,
        to_team_id,
        to_team_name,
    ) in transfers:
        if not from_team_id in team_dict:
            print(
                f"From team {from_team_name} ({from_team_id}) not found. Skipping transfer for player {player_name} ({player_id})."
            )
            continue
        if not to_team_id in team_dict:
            print(
                f"To team {to_team_name} ({to_team_id}) not found. Skipping transfer for player {player_name} ({player_id})."
            )
            continue
        if from_team_id in team_dict and to_team_id in team_dict:
            from_team_players, from_team_shirts = team_dict[from_team_id]
            to_team_players, to_team_shirts = team_dict[to_team_id]

            if player_id != 0 and player_id in from_team_players:
                if from_team_id == to_team_id:
                    print(
                        f"Player is already in the team. Skipping transfer for player {player_name} ({player_id}). From Team: {from_team_name} ({from_team_id}), To Team: {to_team_name} ({to_team_id})."
                    )
                    continue
                # Check if there's an empty spot in the new team
                try:
                    new_index = to_team_players.index(0)  # Find the first empty spot

                    # Remove player from the old team
                    index = from_team_players.index(player_id)
                    from_team_players, from_team_shirts, last_non_zero_index = (
                        replace_with_last_non_zero(
                            from_team_players, from_team_shirts, index
                        )
                    )
                    team_dict[from_team_id] = (from_team_players, from_team_shirts)

                    update_tactics_for_team(
                        binary_file_path, from_team_id, last_non_zero_index
                    )

                    # Add player to the new team
                    to_team_players[new_index] = player_id

                    # Find an unused shirt number
                    used_shirt_numbers = set(to_team_shirts)
                    new_shirt_number = 1
                    while new_shirt_number in used_shirt_numbers:
                        new_shirt_number += 1
                    to_team_shirts[new_index] = new_shirt_number

                    team_dict[to_team_id] = (to_team_players, to_team_shirts)
                    # Log the successful transfer
                    print(
                        f"Transfer successful for player {player_name} ({player_id}). From Team: {from_team_name}({from_team_id}), To Team: {to_team_name} ({to_team_id})."
                    )
                except ValueError:
                    # No empty spot in the new team, skip the transfer
                    print(
                        f"No empty spot in the new team. Skipping transfer for player {player_name} ({player_id}). From Team: {from_team_name} ({from_team_id}), To Team: {to_team_name} ({to_team_id})."
                    )

    return [
        (team_id, team_player_ids, shirt_numbers)
        for team_id, (team_player_ids, shirt_numbers) in team_dict.items()
    ]
