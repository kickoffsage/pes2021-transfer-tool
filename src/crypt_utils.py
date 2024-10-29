import os
import subprocess
import tempfile


def decrypt_save_file(save_file_path):
    """
    Decrypt the PES save file and return the paths to the decrypted folder and data.dat file.

    Args:
        save_file_path (str): Path to the encrypted save file

    Returns:
        tuple: A tuple containing:
            - str: Path to the decrypted folder
            - str: Path to the decrypted data.dat file

    Raises:
        subprocess.CalledProcessError: If decryption fails
    """
    # Create temp directory for decrypted files
    temp_dir = tempfile.mkdtemp()

    # Run decrypter on save file
    decrypter_path = os.path.join("vendor", "pesXdecrypter_2021", "decrypter21.exe")

    # Make the file executable on non-Windows platforms
    if os.name != "nt":
        os.chmod(decrypter_path, 0o777)

    # Run the executable directly on Windows, use wine on other platforms
    if os.name == "nt":
        subprocess.run([decrypter_path, save_file_path, temp_dir], check=True)
    else:
        subprocess.run(["wine", decrypter_path, save_file_path, temp_dir], check=True)

    # Get path to decrypted data.dat file
    data_bin_path = os.path.join(temp_dir, "data.dat")
    if not os.path.exists(data_bin_path):
        raise FileNotFoundError("data.dat not found in decrypted files")

    return temp_dir, data_bin_path


def encrypt_save_file(decrypted_folder_path, output_path):
    """
    Encrypt the modified data folder file back into a PES save file.

    Args:
        decrypted_folder_path (str): Path to the decrypted data folder
        output_path (str): Path where the new encrypted save file should be written

    Raises:
        subprocess.CalledProcessError: If encryption fails
    """
    # Get path to encrypter executable
    encrypter_path = os.path.join("vendor", "pesXdecrypter_2021", "encrypter21.exe")

    # Make executable on non-Windows platforms
    if os.name != "nt":
        os.chmod(encrypter_path, 0o777)

    # Run the encrypter with appropriate arguments
    if os.name == "nt":
        subprocess.run([encrypter_path, decrypted_folder_path, output_path], check=True)
    else:
        subprocess.run(
            ["wine", encrypter_path, decrypted_folder_path, output_path], check=True
        )

    if not os.path.exists(output_path):
        raise FileNotFoundError("Encrypted save file was not created")
