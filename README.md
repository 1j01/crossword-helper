# Crossword Helper CLI

This project is a command-line interface (CLI) tool designed assist in making certain kinds of crosswords.

## Features

- Generate rebus puzzles where every cell contains a specific number of letters.
- For schrodinger puzzles, search for combinations of words that have similar meanings but match certain different letters in the same positions, in order to create crossings on a grid that has superimposed words.

## Installation

To get started, clone the repository and install the dependencies:

```bash
git clone https://github.com/1j01/crossword-helper.git
cd crossword-helper
pip install -r requirements.txt
```

## Usage

### `gen-puzzle` command

To generate a crossword, try running the following command:

```bash
python -m src.cli gen-puzzle --max-words 100 --letters-per-cell 3 --format svg >xw.svg
```

Then open xw.svg in your browser or an SVG editor.

See help for more options:
```bash
python -m src.cli gen-puzzle --help
```

Sample output:
![sample crossword with 3 letters per cell](sample-xw.svg)

(I like the "AMORPHOUS" that ended up in a plus shape. Amorphous+ is a great game.)


### `superpuzzition` command

To find superpuzzitions:
```bash
python -m src.cli superpuzzition --length 5 s p
```

See help for more options:
```bash
python -m src.cli superpuzzition --help
```

Sample output (annotated):
```
CTRLS / CTRLP (score: 0.9132) <- okay
SITUS / SITUP (score: 0.8657)
EQUIS / EQUIP (score: 0.8656)
KRUPS / KRUPP (score: 0.8594)
GINOS / GINUP (score: 0.8481)
GINKS / GINUP (score: 0.8445)
DIPSY / DIPPY (score: 0.8360)
CHUBS / CHUMP (score: 0.8351) <- good
SUSAH / SUPAH (score: 0.8341)
EARSS / EARPS (score: 0.8326)
ZIPES / ZIPUP (score: 0.8318)
LOUSE / LOUPE (score: 0.8314)
KRISS / KRISP (score: 0.8254)
LIEUS / LIEUP (score: 0.8243)
GLAMS / GLAMP (score: 0.8234) <- okay
WISHI / HOPEI (score: 0.8212) <- good
RASSE / RASPE (score: 0.8204)
GINKS / GINEP (score: 0.8142)
CLAPS / CLAPP (score: 0.8140)
DESPE / DEPEW (score: 0.8136)
CHAST / CHAPS (score: 0.8135)
TWEES / TWEEP (score: 0.8075)
GUMPS / GUMUP (score: 0.8069)
WAXES / WAXUP (score: 0.8062) <- okay (tense mismatch though)
BLOIS / BLOOP (score: 0.8048)
TIPSY / TIPPY (score: 0.8044) <- good
...
MIXES / MIXUP (score: 0.7918) <- okay (plural/singular though)
...
GOATS / SHEEP (score: 0.7710) <- ⭐ best (not always at the top!)
...
BLIPS / ABLIP (score: 0.7675) <- okay (plural/singular though)
...
TWITS / TWIRP (score: 0.7661) <- okay (plural/singular though)
SAYTO / PUTTO (score: 0.7659) <- good
...
JAMBS / JAMUP (score: 0.7547) <- okay (tense mismatch though)
```

Note that the dictionary has many uncommon words so the results are very noisy.

I believe that the similarity scores will be less accurate for uncommon words (more based on spelling, and more arbitrary), due to the machine learning dataset not having enough examples of these words, which will bias it towards uncommon words. It may even consider all unknown words more similar to each other than known words, as a by-product of trying to sort the embeddings to be distant from each other, taking into account only words that it's trained on.

However there are some gems in the rough:
- CRAB / RIBS (score: 0.5713) could be clued with "Meaty dish"
- VIAL / LABS (score: 0.5460) could be clued with "What may be used for science experiments" (awkwardly avoiding plural/singular hint; probably a better way)
- SPAS / TUBS (score: 0.5303) could be clued with "Places to soak and relax"

It now uses the crosshare curated word list, which is much better since it's focused on clueable words, and also includes multi-word answers.

TODO: Take the score information from the word list into account when sorting results. This should help cut through the noise!


To find superpuzzitions matching a board that is more filled, say where a grid contains `A_EH` and `A_SS` superimposed, you can specify a list of regular expression patterns instead of simple letters:
```bash
python -m src.cli superpuzzition --length 5 a.eh a.ss
```
`.` is a placeholder for a single letter.

In the future patterns like `a.[es][hs]` or `a.(e|s)(h|s)` might be supported to do the same thing in a single pattern, but right now you have to specify a pattern for each superimposed grid.

## License

This project is licensed under CC0 License.
