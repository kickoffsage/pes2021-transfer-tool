import unittest
import struct
import tempfile
import os
from src.team_utils import read_team_data

class TestTeamUtils(unittest.TestCase):
    def create_test_file(self, teams):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'wb') as f:
            offset = 10307144  # Start offset
            f.seek(offset)
            for team_id, player_ids, shirt_numbers in teams:
                # Write team ID
                f.write(struct.pack('<I', team_id))
                # Write player IDs
                for player_id in player_ids:
                    f.write(struct.pack('<I', player_id))
                # Write shirt numbers
                for shirt_number in shirt_numbers:
                    f.write(struct.pack('<H', shirt_number))
                # Write padding (40 bytes)
                f.write(b'\x00' * 40)
        return temp_file.name

    def test_read_team_data(self):
        teams = [
            (1, [101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
                 111, 112, 113, 114, 115, 116, 117, 118, 119, 120,
                 121, 122, 123, 124, 125, 126, 127, 128, 129, 130,
                 131, 132, 133, 134, 135, 136, 137, 138, 139, 140],
             [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
              11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
              21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
              31, 32, 33, 34, 35, 36, 37, 38, 39, 40]),
            (2, [201, 202, 203, 204, 205, 206, 207, 208, 209, 210,
                 211, 212, 213, 214, 215, 216, 217, 218, 219, 220,
                 221, 222, 223, 224, 225, 226, 227, 228, 229, 230,
                 231, 232, 233, 234, 235, 236, 237, 238, 239, 240],
             [101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
              111, 112, 113, 114, 115, 116, 117, 118, 119, 120,
              121, 122, 123, 124, 125, 126, 127, 128, 129, 130,
              131, 132, 133, 134, 135, 136, 137, 138, 139, 140])
        ]

        test_file = self.create_test_file(teams)
        print(test_file)

        try:
            teams_data = read_team_data(test_file, 10307144, 10520143)

            print(teams_data)
            self.assertEqual(len(teams_data), 2)

            # Check team 1 data
            team1_id, team1_player_ids, team1_shirt_numbers = teams_data[0]
            self.assertEqual(team1_id, 1)
            self.assertEqual(team1_player_ids, [
                101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
                111, 112, 113, 114, 115, 116, 117, 118, 119, 120,
                121, 122, 123, 124, 125, 126, 127, 128, 129, 130,
                131, 132, 133, 134, 135, 136, 137, 138, 139, 140
            ])
            self.assertEqual(team1_shirt_numbers, [
                1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                31, 32, 33, 34, 35, 36, 37, 38, 39, 40
            ])

            # Check team 2 data
            team2_id, team2_player_ids, team2_shirt_numbers = teams_data[1]
            self.assertEqual(team2_id, 2)
            self.assertEqual(team2_player_ids, [
                201, 202, 203, 204, 205, 206, 207, 208, 209, 210,
                211, 212, 213, 214, 215, 216, 217, 218, 219, 220,
                221, 222, 223, 224, 225, 226, 227, 228, 229, 230,
                231, 232, 233, 234, 235, 236, 237, 238, 239, 240
            ])
            self.assertEqual(team2_shirt_numbers, [
                101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
                111, 112, 113, 114, 115, 116, 117, 118, 119, 120,
                121, 122, 123, 124, 125, 126, 127, 128, 129, 130,
                131, 132, 133, 134, 135, 136, 137, 138, 139, 140
            ])

        finally:
            os.remove(test_file)

if __name__ == '__main__':
    unittest.main()
