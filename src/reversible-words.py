from src.dictionary import load_words

words, words_by_length = load_words(score_filter=0.5)

words = set(words) # crucial for performance

reversible = {word for word in words if word[::-1] in words}

for word in reversible:
	print(word)