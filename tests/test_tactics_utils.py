import unittest
import struct
import tempfile
import os
from src.tactics_utils import update_tactics_for_team

class TestTacticsUtils(unittest.TestCase):
    def create_test_file(self, teams):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'wb') as f:
            offset = 10524800  # Tactics section start
            f.seek(offset)
            for team_id, player_indices in teams.items():
                # Write team ID
                f.write(struct.pack('<I', team_id))
                # Write 480 bytes of padding
                f.write(b'\x00' * 480)
                # Write player indices
                f.write(bytes(player_indices))
                # Write remaining padding to fill 628 bytes
                f.write(b'\x00' * (628 - 4 - 480 - len(player_indices)))
        return temp_file.name

    def test_update_tactics_for_team(self):
        teams = {
            1: [0, 5, 3, 8, 7, 10, 12, 11, 20, 18, 24, 1, 4, 6, 9, 13, 14, 15, 19, 21, 
                23, 25, 27, 2, 16, 17, 22, 26, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
            2: [0, 4, 3, 9, 7, 11, 13, 14, 17, 18, 21, 1, 5, 6, 8, 10, 12, 29, 16, 19, 
                20, 22, 23, 2, 26, 27, 24, 25, 15, 28, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]
        }

        test_file = self.create_test_file(teams)

        try:
            # Test removing player index 27 (value at index 22) from team 1
            update_tactics_for_team(test_file, 1, 27)
            # Test removing player index 29 (value at index 17) from team 2
            update_tactics_for_team(test_file, 2, 29)

            with open(test_file, 'rb') as f:
                team_1_indices_offset = 10524800 + 4 + 480
                f.seek(team_1_indices_offset)  # Seek to the start of team 1's player indices
                updated_indices_1 = list(f.read(40))
                team_2_indices_offset = 10524800 + 628 + 4 + 480
                f.seek(team_2_indices_offset)  # Seek to the start of team 2's player indices
                updated_indices_2 = list(f.read(40))

            expected_indices_1 = [0, 5, 3, 8, 7, 10, 12, 11, 20, 18, 24, 1, 4, 6, 9, 13, 14, 15, 19, 21, 
                                    23, 25, 2, 16, 17, 22, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]
            expected_indices_2 = [0, 4, 3, 9, 7, 11, 13, 14, 17, 18, 21, 1, 5, 6, 8, 10, 12, 16, 19, 20,
                                    22, 23, 2, 26, 27, 24, 25, 15, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]

            self.assertEqual(updated_indices_1, expected_indices_1)
            self.assertEqual(updated_indices_2, expected_indices_2)
        finally:
            os.remove(test_file)

if __name__ == '__main__':
    unittest.main()
