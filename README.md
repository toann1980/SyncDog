# SyncDog

<p align="center">
  <img src="UI/syncdog-full.svg" alt="SyncDog Logo" height="512" style="width:auto;">
</p>

SyncDog is a tool for automatically synchronizing files between two directories. It supports multiple synchronization modes, including mirroring and directional syncs.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Creating an Executable](#creating-an-executable)

## Features

- **A to B Mode**: Synchronize files from Directory A to Directory B.
- **B to A Mode**: Synchronize files from Directory B to Directory A.
- **Mirror Mode**: Synchronize files bidirectionally between two directories.
- **User Interface**: Intuitive GUI built with PySide6.
- **File System Monitoring**: Uses WatchDog to monitor file system events.
- **Efficient Patching**: Utilizes BSDiff4 for efficient binary diff and patching.

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/toann1980/SyncDog.git
   cd syncdog
   ```

2. (Optional) Create a virtual environment:

   ```sh
   python -m venv .venv
   .venv\Scripts\activate  # On Linux use `source .venv/bin/activate`
   ```

3. Install the required dependencies:

   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:

   ```sh
   python main.py
   ```

2. Use the GUI to select directories and choose the synchronization mode.

## Creating an Executable

To create an executable file for the SyncDog application, follow these steps:

1. Install PyInstaller:

   ```sh
   pip install pyinstaller
   ```

2. Run PyInstaller with the provided `makefile.spec`:

   ```sh
   pyinstaller makefile.spec
   ```

3. The executable will be created in the `dist` directory.

You can now distribute the executable file to users who do not have Python installed.

## Development

### Running Tests

To run the tests, use:

```sh
pytest
```

## License

This project is licensed under the GNU General Public License. See the [LICENSE](LICENSE) file for details.
