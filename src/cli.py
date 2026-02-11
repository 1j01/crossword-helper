import argparse
from collections import Counter
import logging
import re

from src.dictionary import load_words
from .generate_puzzle import generate_puzzle
from .substitution import find_substitutions
from .superpuzzition import find_superpuzzitions
from .render import render_grid_ascii, render_grid_html, render_grid_svg
from .drop_off_puzzle import generate_drop_off_puzzle, drop_off_rows_to_cells

def output_puzzle(cells: list, format: str):
    if format == 'ascii':
        print(render_grid_ascii(cells))
    elif format == 'html':
        print(render_grid_html(cells))
    elif format == 'svg':
        print(render_grid_svg(cells))

def main():
    parser = argparse.ArgumentParser(description='Crossword Helper CLI')

    # parser.add_argument(
    #     '-d', '--debug',
    #     help="Print lots of debugging statements (more than verbose)",
    #     action="store_const", dest="loglevel", const=logging.DEBUG,
    #     default=logging.WARNING,
    # )
    parser.add_argument(
        '-v', '--verbose',
        help="Output more information",
        action="store_const", dest="loglevel", const=logging.INFO,
    )
    parser.add_argument('--min-quality', type=float, default=2, help='Minimum word quality score in range 0-3, distinct from result scores (default: 2)')

    subparsers = parser.add_subparsers(dest='command', required=True)

    # superpuzzition subcommand
    # TODO: rename to "find-words" or "word-search" or something
    # since it's useful for more than schrodinger puzzles
    superpuzzition_parser = subparsers.add_parser('superpuzzition', help='Find word pairs with specific letter differences')
    superpuzzition_parser.add_argument('--length', type=int, default=None, help='Shortcut for --min-length and --max-length')
    superpuzzition_parser.add_argument('--min-length', type=int, default=None, help='Minimum word length')
    superpuzzition_parser.add_argument('--max-length', type=int, default=None, help='Maximum word length')
    superpuzzition_parser.add_argument('--exactly-one-different', action='store_true', help='Only find pairs where one letter is different (default: False)')
    superpuzzition_parser.add_argument('--position', type=int, default=None, help='Position to compare (0-based, optional; can be negative to look from the end, -1 being the last letter)')
    superpuzzition_parser.add_argument('--max-results', type=int, default=100, help='Maximum number of pairs to return (default: 100)')
    superpuzzition_parser.add_argument('letters', nargs='+', type=str, help='Regular expression patterns for each superimposed grid to match words against')

    # sub subcommand
    sub_parser = subparsers.add_parser('sub', help='Find word pairs that differ by a certain substitution')
    sub_parser.add_argument('letters', nargs='+', type=str, help='')

    # join subcommand
    # experimental, might become part of word search
    join_parser = subparsers.add_parser('join', help='Forms longer answers by joining words from multiple lists, where the word lengths sum to the target length')
    join_parser.add_argument('--length', type=int, required=True, help='Target word length')
    join_parser.add_argument('--max-results', type=int, default=10000, help='Maximum number of pairs to return (default: %(default)s)')
    join_parser.add_argument('--sort-by-cromulence', action='store_true', help='Try to sort results by meaningfulness (default: False)')
    join_parser.add_argument('files', nargs='+', type=str, help='Text files containing word lists, one word per line')

    # draggable subcommand
    # experimental, related to word search / join
    # a manual workflow for drawing connections between words
    draggable_parser = subparsers.add_parser('draggable', help='Generate an SVG with draggable words from multiple lists')
    draggable_parser.add_argument('files', nargs='+', type=str, help='Text files containing word lists, one word per line')

    # gen-puzzle subcommand
    gen_puzzle_parser = subparsers.add_parser('gen-puzzle', help='Generate a crossword puzzle')
    # In the future could have min/max letters per cell
    gen_puzzle_parser.add_argument('--letters-per-cell', type=int, default=1, help='Number of letters per cell (default: 1)')
    gen_puzzle_parser.add_argument('--max-word-length', type=int, default=12, help='Maximum word length (default: 12)')
    gen_puzzle_parser.add_argument('--min-chunk-usage', type=int, default=20, help='Minimum number of usages of a span of letters in the dictionary to be considered for inclusion (default: 20)')
    gen_puzzle_parser.add_argument('--max-placement-attempts', type=int, default=10000, help='Maximum number of placement attempts (default: 10000)')
    gen_puzzle_parser.add_argument('--max-words', type=int, default=300, help='Maximum number of words to place (default: 300)')
    gen_puzzle_parser.add_argument('--format', type=str, choices=['ascii', 'html', 'svg'], default='ascii', help='Output format (default: ascii)')
    gen_puzzle_parser.add_argument('--max-width', type=int, default=15, help='Maximum grid width (default: 15)')
    gen_puzzle_parser.add_argument('--max-height', type=int, default=15, help='Maximum grid height (default: 15)')

    # gen-drop-off subcommand
    gen_drop_off_parser = subparsers.add_parser('gen-drop-off', help='Generate a drop-off puzzle')
    gen_drop_off_parser.add_argument('--min-word-length', type=int, default=3, help='Minimum length for the shortest word in each row (default: 3)')
    gen_drop_off_parser.add_argument('--format', type=str, choices=['ascii', 'html', 'svg'], default='ascii', help='Output format (default: ascii)')
    gen_drop_off_parser.add_argument('--all', action='store_true', help='Output a puzzle that combines all row candidates into a single large puzzle')
    gen_drop_off_parser.add_argument('--allow-partial', action='store_true', help='Allow partial puzzles with missing or padded rows')
    gen_drop_off_parser.add_argument('key_words', nargs='+', type=str, help='Key words of equal length to spell out in columns')

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    words, words_by_length = load_words(score_filter=args.min_quality)

    if args.command == 'superpuzzition':
        target_patterns = [re.compile(l.strip(), re.IGNORECASE) for l in args.letters]
        min_length = args.min_length if args.min_length is not None else (args.length if args.length is not None else 1)
        max_length = args.max_length if args.max_length is not None else (args.length if args.length is not None else 10000)
        results = find_superpuzzitions(words_by_length, min_length, max_length, target_patterns, args.position, args.exactly_one_different)
        for result in results[:args.max_results]:
            print(f"{' / '.join(result.words)} (score: {result.score:.4f})")
    elif args.command == 'sub':
        letter_sequences = [letter_sequence.upper() for letter_sequence in args.letters]
        results = find_substitutions(words_by_length, letter_sequences)
        
        counts = Counter()
        for result in results:
            counts[result.words[0]] += 1
        counts_logged = Counter()

        output_format = "console"
        # for result in results[:args.max_results]:
        for result in results:
            # print(f"{' -> '.join(result.words)} (score: {result.score:.4f})")
            # print(f"{' -> '.join(result.words)}")
            line = ""
            for i, word in enumerate(result.words):
                if i > 0:
                    line += " -> "
                used = 0
                for highlight in result.highlights[i]:
                    line += word[used:highlight[0]]
                    to_highlight = word[highlight[0]:highlight[1]]
                    if output_format == "markdown":
                        line += f"**{to_highlight}**"
                    elif output_format == "console":
                        # green (too "addition"-coded; these are mutual/symmetrical substitutions, really)
                        # line += f"\033[1;32m{to_highlight}\033[0m"
                        # yellow (too bright/distinct, in my terminal, in my opinion; makes it hard to read the word)
                        # line += f"\033[1;33m{to_highlight}\033[0m"
                        # cyan (nice balance, and a color often used for generic highlighting, like selections)
                        line += f"\033[1;36m{to_highlight}\033[0m"
                        # bold
                        # line += f"\033[1m{to_highlight}\033[0m"
                    else:
                        line += to_highlight
                    used = highlight[1]
                line += word[used:]
                if output_format == "markdown":
                    line = line.replace("****", "")
                # elif output_format == "console":
                #     # not necessary
                #     line = line.replace("\033[1m\033[0m", "")

            # Emphasize groups of results that make different substitutions
            # to the same base word
            if counts[result.words[0]] > 1:
                counts_logged[result.words[0]] += 1
                line += f" ({counts_logged[result.words[0]]} of {counts[result.words[0]]})"
            if counts[result.words[0]] > 2:
                line += " ⭐"

            print(line)
    elif args.command == 'gen-puzzle':
        cells = generate_puzzle(words, args.letters_per_cell, args.max_word_length, args.min_chunk_usage, args.max_placement_attempts, args.max_words, args.max_width, args.max_height)
        output_puzzle(cells, args.format)
    elif args.command == 'join':
        from .join import join_words
        word_lists = []
        for filename in args.files:
            with open(filename, 'r') as f:
                words = [line.strip() for line in f if line.strip()]
                word_lists.append(words)
        results = join_words(word_lists, args.length)
        for result in results[:args.max_results]:
            print(f"{'|'.join(result.words)} (score: {result.score:.4f})")
    elif args.command == 'draggable':
        from .draggable import make_draggable_svg
        word_lists = []
        for filename in args.files:
            with open(filename, 'r') as f:
                words = [line.strip() for line in f if line.strip()]
                word_lists.append(words)
        print(make_draggable_svg(word_lists))
    elif args.command == 'gen-drop-off':
        if args.all:
            from .drop_off_puzzle import generate_all_candidates_puzzle
            rows = generate_all_candidates_puzzle(args.key_words, args.min_word_length, words_by_length)
        else:
            rows = generate_drop_off_puzzle(args.key_words, args.min_word_length, words_by_length, allow_partial=args.allow_partial)
        if rows is None:
            logging.error("No solution found for the given key words.")
        else:
            cells = drop_off_rows_to_cells(rows)
            output_puzzle(cells, args.format)
    else:
        # might only happen in development when a new subcommand is added but not handled yet
        parser.print_help()

if __name__ == '__main__':
    main()