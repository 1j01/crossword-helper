# Crossword Helper CLI

This project is a command-line interface (CLI) tool designed assist in making certain kinds of crosswords.

## Features

- Generate rebus puzzles where every cell contains a specific number of letters.
- For schrodinger puzzles, search for combinations of words that have similar meanings but match certain different letters in the same positions, in order to create crossings on a grid that has superimposed words.
- Uses a high-quality word list from [Crosshare](https://crosshare.org/) which is curated from multiple sources.

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
python -m src.cli gen-puzzle --letters-per-cell 3 --format svg >xw.svg
```

Then open xw.svg in your browser or an SVG editor.

See help for more options:
```bash
python -m src.cli gen-puzzle --help
```

Sample output:
![sample crossword with 3 letters per cell](sample-xw.svg)


### `superpuzzition` command

To find pairs of five-letter words that contain S and P in the same position, run:
```bash
python -m src.cli superpuzzition --length 5 s p
```

See help for more options:
```bash
python -m src.cli superpuzzition --help
```

Sample output:
```
$ python -m src.cli superpuzzition e.s o.s

ADAPTERS / ADAPTORS (score: 0.9613)
TORMENTERS / TORMENTORS (score: 0.9579)
INDIRECTNESS / INDIRECTIONS (score: 0.9522)
CLAIMSADJUSTERS / CLAIMSADJUSTORS (score: 0.9518)
CONVEYERS / CONVEYORS (score: 0.9481)
ERECTERS / ERECTORS (score: 0.9345)
RESISTERS / RESISTORS (score: 0.9311)
FEETS / FOOTS (score: 0.9289)
ADVISERS / ADVISORS (score: 0.9123)
PIGEONPEAS / PIGEONTOES (score: 0.9088)
ATTESTERS / ATTESTORS (score: 0.9076)
TOENAILCLIPPERS / TOENAILSCISSORS (score: 0.9038)
PETSOUNDS / DOGSOUNDS (score: 0.8938)
DEBTEES / DEBTORS (score: 0.8907)
MARITIMEBORDERS / MARITIMENATIONS (score: 0.8885)
POWERADAPTERS / POWERADAPTORS (score: 0.8881)
IDOLIZERS / IDOLATORS (score: 0.8859)
BAILERS / BAILORS (score: 0.8828)
JAILERS / JAILORS (score: 0.8812)
PETSITTERS / DOGSITTERS (score: 0.8810)
PETSITTER / DOGSITTER (score: 0.8807)
SECRETNESS / SECRETIONS (score: 0.8777)
VILLAINESS / VILLAINOUS (score: 0.8765)
SIDEWINDERS / SIDEWINDOWS (score: 0.8736)
GRANTERS / GRANTORS (score: 0.8719)
IMPOSTERS / IMPOSTORS (score: 0.8712)
SORCERESS / SORCEROUS (score: 0.8657)
PROTESTERS / PROTESTORS (score: 0.8631)
HABITUALNESS / HABITUATIONS (score: 0.8613)
```

You can then try to think of clues that would work for both words. Some examples:
- ADVISERS / ADVISORS: *They give guidance* (some of these are just alternate spellings, so are trivial to clue)
- VILLAINESS / VILLAINOUS: *Like Bellatrix Lestrange or The Wicked Witch of the West* ("like" is useful for matching different parts of speech, but it tends to be vague so don't overuse it!)
- PETSOUNDS / DOGSOUNDS: *Arfs, for example* ("for example" is useful for matching hypernyms and hyponyms - an "arf" is a "dog sound" is a "pet sound" - but it is a crutch so try not to overuse it!)
- DEBTEES / DEBTORS: *People involved in owing money* or *One side of a loan agreement* (secretly it's both sides, but you phrase the clue so it applies to either, not both)

Some more examples (4-letter A/B pairs)

- CRAB / RIBS: *Meaty dish* (one noun is singular, one plural, but as dishes, they're both singular)
- VIAL / LABS: *What may be used for science experiments* ("What" can be used for avoiding implying a plural/singular, but it's awkward here; there's probably a better way)
- SPAS / TUBS: *Places to soak and relax* (this is the best kind of clue, just a natural description of either based on their shared characteristics)
- TAXI / UBER: *Ride service* (one is a proper noun, but that doesn't matter)
- ANDI / BUTI: *"I want to go ___ don't want to go"* (either conjunction works here, due to the internal contradiction; it's a dichotomy, and/but/yet it's not a dichotomy)
- ROWA / ROWB: *Pretty neat seats in a theater* ("Sweat seats" would be fine for row A but too much hype for row B; it's a Balancing Act)


To find superpuzzitions matching a board that is more filled, say where a grid contains `A_EH` and `A_SS` superimposed, you can specify a list of regular expression patterns instead of simple letters:
```bash
python -m src.cli superpuzzition --length 5 a.eh a.ss
```
`.` is a placeholder for a single letter.

## Possible Improvements

These are not necessarily planned features, but just ideas.

- Crossword generation algorithm
  - Make puzzle generator try to plan ahead, placing words that have more crossing potential.
  - Maybe try several placements at once and pick the option that leads to the most words placed.
  - Make sure constraint intended to avoid run-ons\* aren't making certain crossings impossible. (\*like accidental portmanteaus, e.g. placing "CAT" onto "TOUCAN" making "CATOUCAN")
  - The left top corner is trickier because it can become impossible to end words on a cell to connect it without creating a run-on.
  - Could try making it mutate the grid rather than just adding.
  - Could try a graph-based approach.
- Word searching:
  - Use word quality scores from the word list when sorting results. The word list is already filtered by quality by default, and there aren't that many quality levels, but it could help boost the best options.
  - Could support using a single pattern with alternations like `a.[es][hs]` or `a.(e|s)(h|s)` to do the same thing as specifying a pattern for each superimposed grid (`a.eh` and `a.ss`).
    - I'm not sure if this is really better, since the way it is, while it's technically more repetitive, it reads/writes more clearly, expressing the separate grids separately, and it's shorter without the extra syntax.
    - Could at least detect if the user tries using alternations/character classes and warn them that it won't work as they expect.
  - Highlight where patterns match in the output, with color or bolding.
- Could suggest clues using a large language model.
  - You can always do this externally, and many people would want to disable this, so it should be optional. 
  - Also, while LLMs are good at word association (thesaurus is one of the best use cases, IMO!), they're really bad about thinking from the solver's perspective, and separately considering whether a clue works for each word rather than either *the set of both* or *just one* (or *neither*).
  - So this would involve a multi-step process of asking it whether a clue works for each word, ideally probably without the context of the other word (maybe even without the context of the answer, asking it to solve the clue on its own), and then asking it to refine the clue until it works for both. But it likely would fail to do the refinement anyways, so it might be a lot of trouble for nothing. I will say though that asking it to brainstorm connections between words before asking for clues can help.

## License

This project is licensed under CC0 License.

This license does not apply to the word data included in the repo.
