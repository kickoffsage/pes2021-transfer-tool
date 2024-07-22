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
            1: [22, 1, 14, 3, 5, 9, 8, 7, 11, 19, 10, 6, 23, 16, 20, 13, 4, 18, 12, 15,
                21, 17, 2, 0, 25, 28, 26, 29, 32, 33, 24, 30, 31, 35, 36, 37, 38, 39, 27, 34],
            2: [11, 5, 2, 9, 4, 3, 7, 6, 15, 10, 13, 12, 8, 14, 0, 1, 17, 18, 16, 19,
                21, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]
        }

        test_file = self.create_test_file(teams)

        try:
            # Test removing player index 19 (value at index 9) from team 1
            update_tactics_for_team(test_file, 1, 19)

            with open(test_file, 'rb') as f:
                f.seek(10524800 + 4 + 480)  # Seek to the start of team 1's player indices
                updated_indices = list(f.read(40))

            expected_indices = [22, 1, 14, 3, 5, 9, 8, 7, 11, 10, 6, 23, 16, 20, 13, 4, 18, 12, 15,
                                21, 17, 2, 0, 25, 28, 26, 29, 32, 33, 24, 30, 31, 35, 36, 37, 38, 39, 27, 34, 0xFF]

            self.assertEqual(updated_indices, expected_indices)
        finally:
            os.remove(test_file)

if __name__ == '__main__':
    unittest.main()
