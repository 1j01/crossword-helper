#!/usr/bin/env python3

import argparse
import nltk
from collections import defaultdict
from nltk.corpus import wordnet as wn

nltk.download("wordnet")
# nltk.download("omw-1.4")

VALID_POS = {"n", "v", "a", "s", "r"}

def collect_words(pos_filter: set[str] | None = None) -> dict[str, set[str]]:
    """
    Collect words that occur with multiple parts of speech.

    :param pos_filter: Optional set of POS tags (e.g. {"n", "v"})
    :return: dict[word] -> set of POS tags
    """
    pos_map = defaultdict(set)

    for syn in wn.all_synsets():
        pos = syn.pos()
        if pos_filter and pos not in pos_filter:
            continue

        for lemma in syn.lemma_names():
            pos_map[lemma.lower()].add(pos)

    if pos_filter:
        # require that all requested POS appear
        return {
            w: p for w, p in pos_map.items()
            if pos_filter.issubset(p)
        }
    else:
        # require more than one POS total
        return {
            w: p for w, p in pos_map.items()
            if len(p) > 1
        }

def parse_args():
    parser = argparse.ArgumentParser(
        description="Find WordNet words with multiple parts of speech"
    )
    parser.add_argument(
        "--pos",
        nargs="*",
        help="Optional POS tags: n v a s r (e.g. --pos n v)"
    )
    return parser.parse_args()

def main():
    args = parse_args()

    if args.pos:
        pos_filter = set(args.pos)
        unknown = pos_filter - VALID_POS
        if unknown:
            raise ValueError(f"Invalid POS tags: {unknown}")
    else:
        pos_filter = None

    results = collect_words(pos_filter)

    for word in sorted(results):
        print(f"{word}\t{','.join(sorted(results[word]))}")

if __name__ == "__main__":
    main()
