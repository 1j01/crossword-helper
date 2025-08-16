from collections import defaultdict


with open('data/ridyhew-3fbbc4-word-list.txt', 'r', encoding='utf-8') as f:
	words = f.read().splitlines()

words_by_length = defaultdict(list)
for word in words:
    words_by_length[len(word)].append(word)

