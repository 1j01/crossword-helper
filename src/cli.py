import argparse
import re
from .generate_puzzle import generate_puzzle
from .superpuzzition import find_superpuzzitions
from .render import render_grid_ascii, render_grid_html, render_grid_svg

def main():
    parser = argparse.ArgumentParser(description='Crossword Helper CLI')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # superpuzzition subcommand
    superpuzzition_parser = subparsers.add_parser('superpuzzition', help='Find word pairs with specific letter differences')
    superpuzzition_parser.add_argument('--length', type=int, required=True, help='Target word length')
    superpuzzition_parser.add_argument('--exactly-one-different', action='store_true', help='Only find pairs where one letter is different (default: False)')
    superpuzzition_parser.add_argument('--position', type=int, default=None, help='Position to compare (0-based, optional; can be negative to look from the end, -1 being the last letter)')
    superpuzzition_parser.add_argument('--max-results', type=int, default=100, help='Maximum number of pairs to return (default: 100)')
    superpuzzition_parser.add_argument('letters', nargs='+', type=str, help='Regular expression patterns for each superimposed grid to match words against')

    # gen-puzzle subcommand
    gen_puzzle_parser = subparsers.add_parser('gen-puzzle', help='Generate a crossword puzzle')
    # In the future could have min/max letters per cell
    gen_puzzle_parser.add_argument('--letters-per-cell', type=int, default=1, help='Number of letters per cell (default: 1)')
    gen_puzzle_parser.add_argument('--max-word-length', type=int, default=12, help='Maximum word length (default: 12)')
    gen_puzzle_parser.add_argument('--min-chunk-usage', type=int, default=20, help='Minimum number of usages of a span of letters in the dictionary to be considered for inclusion (default: 20)')
    gen_puzzle_parser.add_argument('--max-placement-attempts', type=int, default=10000, help='Maximum number of placement attempts (default: 10000)')
    gen_puzzle_parser.add_argument('--max-words', type=int, default=20, help='Maximum number of words to place (default: 20)')
    gen_puzzle_parser.add_argument('--format', type=str, choices=['ascii', 'html', 'svg'], default='ascii', help='Output format (default: ascii)')
    gen_puzzle_parser.add_argument('--max-width', type=int, default=15, help='Maximum grid width (default: 15)')
    gen_puzzle_parser.add_argument('--max-height', type=int, default=15, help='Maximum grid height (default: 15)')

    args = parser.parse_args()

    if args.command == 'superpuzzition':
        target_patterns = [re.compile(l.strip(), re.IGNORECASE) for l in args.letters]
        pairs = find_superpuzzitions(args.length, target_patterns, args.position, args.exactly_one_different)
        for pair in pairs[:args.max_results]:
            print(pair[0] + " / " + pair[1] + " (score: " + f"{pair[2]:.4f}" + ")")
    elif args.command == 'gen-puzzle':
        cells = generate_puzzle(args.letters_per_cell, args.max_word_length, args.min_chunk_usage, args.max_placement_attempts, args.max_words, args.max_width, args.max_height)
        if args.format == 'ascii':
            print(render_grid_ascii(cells))
        elif args.format == 'html':
            print(render_grid_html(cells))
        elif args.format == 'svg':
            print(render_grid_svg(cells))

if __name__ == '__main__':
    main()