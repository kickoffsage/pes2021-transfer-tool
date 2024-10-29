# PES 2021 Transfer Tool

**⚠️ IMPORTANT: This project is currently in development and not yet ready for production use. Features may be incomplete or subject to change. ⚠️**

This tool allows you to apply transfers to a Pro Evolution Soccer (PES) 2021 save game file and generate updated team and player data. It also allows you to fetch the latest transfers from Transfermarkt.

## How It Works

This tool manipulates PES 2021 save files to apply transfers. The process is based on the file structure information provided by the PES modding community, specifically referencing the [Pro Evolution Soccer 2021 Edit File wiki page](https://implyingrigged.info/wiki/Pro_Evolution_Soccer_2021/Edit_file#Team-Player_Table).

The tool performs the following main operations:

1. Reads the binary save file and extracts team and player data.
2. Applies transfers by modifying the team-player associations in memory.
3. Updates the binary save file with the new team-player data.
4. Generates a CSV file with the updated team and player information.

The tool also includes functionality to fetch the latest transfer data from Transfermarkt, allowing you to keep your PES 2021 save file up-to-date with real-world transfers.

## Dependencies

To run and develop this project, you'll need:

1. Python 3.7 or higher
2. Poetry for package management

## Setup

1. Install Python 3.7 or higher if you haven't already.
2. Install Poetry by following the instructions at https://python-poetry.org/docs/#installation

3. Clone this repository:
   ```
   git clone https://github.com/kickoffsage/pes-2021-transfer-tool.git
   cd pes-2021-transfer-tool
   ```

4. Install the project dependencies using Poetry:
   ```
   poetry install
   ```

## Save File Decryption and Encryption

This tool uses `pesXdecrypter` to handle encrypted save files. 

Compiled binaries for `pesXdecrypter_2021` are included in the vendor directory of this project for convenience, but please note that it maintains its original license separate from this project's license. Refer to the `pesXdecrypter` repository for its specific licensing terms and usage instructions. You can find it at [https://github.com/the4chancup/pesXdecrypter](https://github.com/the4chancup/pesXdecrypter).

## Running the Tool

To run the tool, use Poetry to execute one of the following scripts:

### To apply transfers:
   ```
   poetry run python apply_transfers.py <arguments>
   ```

### To extract team data:
   ```
   poetry run python export_squads.py <arguments>
   ```

### To fetch transfer data:
   ```
   poetry run python fetch-latest-transfers.py <arguments>
   ```
    
   ```
   poetry run python fetch-team-transfers.py <arguments>
   ```

Replace `<arguments>` with the required command-line arguments for each script. Refer to the script's help message for detailed information on the required arguments.
