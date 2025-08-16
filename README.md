# Crossword Helper CLI

This project is a command-line interface (CLI) tool designed assist in making certain kinds of crosswords.

## Features

- Generate rebus puzzles where every cell contains a specific number of letters.
- For schrodinger puzzles, find words that have similar meanings but specific different letters in a given position, and match in length. I'm calling these "superpuzzitions". This is useful when you already have one superpuzzition and you want to find crossing words that have to now match multiple different letters to fit two grids simultaneously.

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
python -m src.cli gen-puzzle --max-words 100 --letters-per-cell 3 --format html >xw.html
```

Then open xw.html in your browser.

See help for more options:
```bash
python -m src.cli gen-puzzle --help
```

To find superpuzzitions:
```bash
python -m src.cli superpuzzition --length 5 s p
```

See help for more options:
```bash
python -m src.cli superpuzzition --help
```


## License

This project is licensed under CC0 License.
