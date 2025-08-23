from collections import defaultdict
import json
import sys


# with open('data/ridyhew-3fbbc4-word-list.txt', 'r', encoding='utf-8') as f:
# 	words = f.read().splitlines()

# words_by_length = defaultdict(list)
# for word in words:
#     words_by_length[len(word)].append(word)

# worddb.json structure: { words: {[length]: [[word, score], ...], ...} }
with open('data/worddb.json', 'r', encoding='utf-8') as f:
    worddb = json.load(f)
    words_by_length: dict[int, list[str]] = {}
    for length, words_of_length in worddb['words'].items():
        words_by_length[int(length)] = [word for word, score in words_of_length]
    words = [word for sublist in words_by_length.values() for word in sublist]

print(f"Loaded {len(words)} words from worddb.json", file=sys.stderr)
print(f"First 10 words: {words[:10]}", file=sys.stderr)
print(f"Last 10 words: {words[-10:]}", file=sys.stderr)
