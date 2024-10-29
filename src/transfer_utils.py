from tactics_utils import update_tactics_for_team


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


def remove_player_from_team(binary_file_path, team_id, players, shirts, player_id):
    """Remove the player with the given ID from the team."""
    index = players.index(player_id)
    players, shirts, last_non_zero_index = replace_with_last_non_zero(
        players, shirts, index
    )

    update_tactics_for_team(binary_file_path, team_id, last_non_zero_index)

    return (players, shirts)


def add_player_to_team(team_id, players, shirts, player_id, new_index):
    """Add the player with the given ID to the team."""
    # Add player to the new team
    players[new_index] = player_id

    # Find an unused shirt number
    used_shirt_numbers = set(shirts)
    new_shirt_number = 1
    while new_shirt_number in used_shirt_numbers:
        new_shirt_number += 1
    shirts[new_index] = new_shirt_number

    return (players, shirts)


def apply_transfers(
    binary_file_path,
    teams_data,
    transfers,
    player_names={},
    previous_skipped_transfers=[],
):
    team_dict = {
        team_id: (team_player_ids, shirt_numbers)
        for team_id, team_player_ids, shirt_numbers in teams_data
    }

    skipped_transfers = []

    for (
        player_id,
        player_name,
        from_team_id,
        from_team_name,
        to_team_id,
        to_team_name,
    ) in transfers:
        if not player_id in player_names:
            print(
                f"Player {player_name} ({player_id}) not found. Skipping transfer. From Team: {from_team_name} ({from_team_id}), To Team: {to_team_name} ({to_team_id})."
            )
            continue

        # Check if there's an empty spot in the new team
        try:
            # Transfer between two teams
            if from_team_id in team_dict and to_team_id in team_dict:
                from_team_players, from_team_shirts = team_dict[from_team_id]
                to_team_players, to_team_shirts = team_dict[to_team_id]

                new_index = to_team_players.index(0)  # Find the first empty spot

                if from_team_id == to_team_id and player_id in to_team_players:
                    print(
                        f"Player is already in the team. Skipping transfer for player {player_name} ({player_id}). From Team: {from_team_name} ({from_team_id}), To Team: {to_team_name} ({to_team_id})."
                    )
                    continue

                if player_id in from_team_players:
                    team_dict[from_team_id] = remove_player_from_team(
                        binary_file_path,
                        from_team_id,
                        from_team_players,
                        from_team_shirts,
                        player_id,
                    )

                team_dict[to_team_id] = add_player_to_team(
                    to_team_id,
                    to_team_players,
                    to_team_shirts,
                    player_id,
                    new_index,
                )

                # Log the successful transfer
                print(
                    f"Transfer successful for player {player_name} ({player_id}). From Team: {from_team_name}({from_team_id}), To Team: {to_team_name} ({to_team_id})."
                )

            # Transfer from a team to Without Team, Retired or a team that doesn't exist
            if from_team_id in team_dict and to_team_id not in team_dict:
                from_team_players, from_team_shirts = team_dict[from_team_id]

                if player_id in from_team_players:
                    remove_player_from_team(
                        binary_file_path,
                        from_team_id,
                        from_team_players,
                        from_team_shirts,
                        player_id,
                    )

                    # Log the successful transfer
                    print(
                        f"Transfer successful for player {player_name} ({player_id}). From Team: {from_team_name}({from_team_id}), To Team: {to_team_name} ({to_team_id})."
                    )
                else:
                    print(
                        f"Player is not in the team. Skipping transfer for player {player_name} ({player_id}). From Team: {from_team_name} ({from_team_id}), To Team: {to_team_name} ({to_team_id})."
                    )

            # Transfer from Without Team or a team that doesn't exist to a team
            if from_team_id not in team_dict and to_team_id in team_dict:
                to_team_players, to_team_shirts = team_dict[to_team_id]

                new_index = to_team_players.index(0)  # Find the first empty spot

                if player_id not in to_team_players:
                    team_dict[to_team_id] = add_player_to_team(
                        to_team_id,
                        to_team_players,
                        to_team_shirts,
                        player_id,
                        new_index,
                    )

                    # Log the successful transfer
                    print(
                        f"Transfer successful for player {player_name} ({player_id}). From Team: {from_team_name}({from_team_id}), To Team: {to_team_name} ({to_team_id})."
                    )
                else:
                    print(
                        f"Player is already in the team. Skipping transfer for player {player_name} ({player_id}). From Team: {from_team_name} ({from_team_id}), To Team: {to_team_name} ({to_team_id})."
                    )

        except ValueError:
            # No empty spot in the new team, store the skipped transfer and try again later
            skipped_transfers.append(
                (
                    player_id,
                    player_name,
                    from_team_id,
                    from_team_name,
                    to_team_id,
                    to_team_name,
                )
            )
            print(
                f"No empty spot in the new team. Skipping transfer for player {player_name} ({player_id}). From Team: {from_team_name} ({from_team_id}), To Team: {to_team_name} ({to_team_id})."
            )

    modified_teams_data = [
        (team_id, team_player_ids, shirt_numbers)
        for team_id, (team_player_ids, shirt_numbers) in team_dict.items()
    ]

    while skipped_transfers != previous_skipped_transfers:
        print(
            f"Retrying {len(skipped_transfers)} skipped transfers (because of no empty spot in new team)."
        )
        return apply_transfers(
            binary_file_path,
            modified_teams_data,
            skipped_transfers,
            player_names,
            skipped_transfers,
        )

    if len(skipped_transfers) > 0:
        print(
            f"Exhausted retrials to apply {len(skipped_transfers)} skipped transfers (because of no empty spot in new team)."
        )

    return modified_teams_data
