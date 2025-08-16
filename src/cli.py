import argparse
from .logic import find_similar_words, generate_rebus
from .render import render_grid

def main():
    parser = argparse.ArgumentParser(description='Crossword Helper CLI')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # similar-words subcommand
    sim_parser = subparsers.add_parser('similar-words', help='Find word pairs with similar definitions')
    sim_parser.add_argument('length', type=int, help='Target word length')
    sim_parser.add_argument('letter1', type=str, help='First letter to compare')
    sim_parser.add_argument('letter2', type=str, help='Second letter to compare')
    sim_parser.add_argument('--exactly-one-different', action='store_true', help='Exactly one letter different')

    # generate-rebus subcommand
    rebus_parser = subparsers.add_parser('generate-rebus', help='Generate rebus grid')
    # In the future could have min/max letters per cell
    rebus_parser.add_argument('--letters-per-cell', type=int, default=2, help='Number of letters per cell (default: 2)')
    rebus_parser.add_argument('--max-word-length', type=int, default=12, help='Maximum word length (default: 12)')
    rebus_parser.add_argument('--min-chunk-usage', type=int, default=20, help='Minimum number of usages of a span of letters in the dictionary to be considered for inclusion (default: 20)')
    rebus_parser.add_argument('--max-placement-attempts', type=int, default=10000, help='Maximum number of placement attempts (default: 10000)')
    rebus_parser.add_argument('--max-words', type=int, default=20, help='Maximum number of words to place (default: 20)')

    args = parser.parse_args()

    if args.command == 'similar-words':
        word_pairs = find_similar_words(args.length, args.letter1, args.letter2, args.exactly_one_different)
        for pair in word_pairs:
            print(pair)
    elif args.command == 'generate-rebus':
        cells = generate_rebus(args.letters_per_cell, args.max_word_length, args.min_chunk_usage, args.max_placement_attempts, args.max_words)
        render_grid(cells)

if __name__ == '__main__':
    main()