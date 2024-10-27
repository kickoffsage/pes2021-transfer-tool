import unittest
from unittest.mock import patch
from src.transfer_utils import apply_transfers


class TestTransferUtils(unittest.TestCase):
    def test_apply_transfers(self):
        teams_data = [
            (
                1,
                [
                    101,
                    102,
                    103,
                    104,
                    105,
                    106,
                    107,
                    108,
                    109,
                    110,
                    111,
                    112,
                    113,
                    114,
                    115,
                    116,
                    117,
                    118,
                    119,
                    120,
                    121,
                    122,
                    123,
                    124,
                    125,
                    126,
                    127,
                    128,
                    129,
                    130,
                    131,
                    132,
                    133,
                    134,
                    135,
                    136,
                    137,
                    138,
                    0,
                    0,
                ],
                [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                    29,
                    30,
                    31,
                    32,
                    33,
                    34,
                    35,
                    36,
                    37,
                    38,
                    0,
                    0,
                ],
            ),
            (
                2,
                [
                    201,
                    202,
                    203,
                    204,
                    205,
                    206,
                    207,
                    208,
                    209,
                    210,
                    211,
                    212,
                    213,
                    214,
                    215,
                    216,
                    217,
                    218,
                    219,
                    220,
                    221,
                    222,
                    223,
                    224,
                    225,
                    226,
                    227,
                    228,
                    229,
                    230,
                    231,
                    232,
                    233,
                    234,
                    235,
                    236,
                    237,
                    238,
                    0,
                    0,
                ],
                [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                    29,
                    30,
                    31,
                    32,
                    33,
                    34,
                    35,
                    36,
                    37,
                    38,
                    0,
                    0,
                ],
            ),
        ]

        transfers = [
            (
                102,
                "John Doe",
                1,
                "Team A",
                2,
                "Team B",
            ),  # Move player 102 from team 1 to team 2
            (
                216,
                "Jane Smith",
                2,
                "Team B",
                1,
                "Team A",
            ),  # Move player 216 from team 2 to team 1
        ]

        with patch("src.transfer_utils.update_tactics_for_team"):
            updated_teams_data = apply_transfers(
                "path/to/binary",
                teams_data,
                transfers,
                player_names={102: "John Doe", 216: "Jane Smith"},
            )

        # Check team 1 updated data
        team1_id, team1_player_ids, team1_shirt_numbers = updated_teams_data[0]
        self.assertEqual(team1_id, 1)
        self.assertNotIn(102, team1_player_ids)  # Player 102 should be removed
        self.assertIn(216, team1_player_ids)  # Player 216 should be added
        self.assertEqual(
            2, team1_shirt_numbers[37]
        )  # Shirt 2 (of new player) should be at the end
        self.assertEqual(
            38, team1_shirt_numbers[1]
        )  # Shirt 38 should be added moved to the removed player's position

        # Check team 2 updated data
        team2_id, team2_player_ids, team2_shirt_numbers = updated_teams_data[1]
        self.assertEqual(team2_id, 2)
        self.assertIn(102, team2_player_ids)  # Player 102 should be added
        self.assertNotIn(216, team2_player_ids)  # Player 201 should be removed
        self.assertNotIn(16, team2_shirt_numbers)  # Shirt 16 should be removed
        self.assertIn(39, team2_shirt_numbers)  # Shirt 39 should be added


if __name__ == "__main__":
    unittest.main()
