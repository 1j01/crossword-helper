import argparse
import logging
import re

from src.dictionary import load_words
from .generate_puzzle import generate_puzzle
from .superpuzzition import find_superpuzzitions
from .render import render_grid_ascii, render_grid_html, render_grid_svg
from .drop_off_puzzle import generate_drop_off_puzzle, drop_off_rows_to_cells

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
    elif args.command == 'gen-puzzle':
        cells = generate_puzzle(words, args.letters_per_cell, args.max_word_length, args.min_chunk_usage, args.max_placement_attempts, args.max_words, args.max_width, args.max_height)
        if args.format == 'ascii':
            print(render_grid_ascii(cells))
        elif args.format == 'html':
            print(render_grid_html(cells))
        elif args.format == 'svg':
            print(render_grid_svg(cells))
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
        try:
            rows = generate_drop_off_puzzle(args.key_words, args.min_word_length, words_by_length)
        except ValueError as e:
            print(f"Error: {e}")
        else:
            if rows is None:
                print("No solution found for the given key words.")
            else:
                cells = drop_off_rows_to_cells(rows)
                if args.format == 'ascii':
                    print(render_grid_ascii(cells))
                elif args.format == 'html':
                    print(render_grid_html(cells))
                elif args.format == 'svg':
                    print(render_grid_svg(cells))
    else:
        # might only happen in development when a new subcommand is added but not handled yet
        parser.print_help()

if __name__ == '__main__':
    main()