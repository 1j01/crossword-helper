# Crossword Helper CLI

This project is a command-line interface (CLI) tool designed assist in making certain kinds of crosswords.

## Features

- Generate rebus puzzles where every cell contains a specific number of letters.

## Installation

To get started, clone the repository and install the dependencies:

```bash
git clone https://github.com/1j01/crossword-helper.git
cd crossword-helper
pip install -r requirements.txt
```

## Usage

To generate a crossword, try running the following command:

```bash
python -m src.cli generate-rebus --max-words 100 --letters-per-cell 3 --format html >xw.html
```

Then open xw.html in your browser.

See help for more options:
```bash
python -m src.cli generate-rebus --help
```

## License

This project is licensed under CC0 License.
