import argparse
from logic import find_similar_words, generate_rebus

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
    rebus_parser.add_argument('letters_per_cell', type=int, help='Number of letters per cell')

    args = parser.parse_args()

    if args.command == 'similar-words':
        word_pairs = find_similar_words(args.length, args.letter1, args.letter2, args.exactly_one_different)
        for pair in word_pairs:
            print(pair)
    elif args.command == 'generate-rebus':
        grid = generate_rebus(args.letters_per_cell)
        print(grid)

if __name__ == '__main__':
    main()