
from collections import defaultdict
from numpy import ndarray

from .dictionary import words


def find_superpuzzitions(target_length: int, target_letters: list[str], target_position: int | None = None, exactly_one_different=False) -> list[tuple[str, str, float]]:
	words_fitting_length = [word for word in words if len(word) == target_length]
	if not words_fitting_length:
		raise ValueError(f"No words in dictionary with length {target_length}")

	if exactly_one_different:
		# TODO: implement
		raise NotImplementedError("Exactly one different letter mode is not implemented.")

	results: list[tuple[str, str, float]] = []

	from sentence_transformers import SentenceTransformer
	model = SentenceTransformer("all-MiniLM-L6-v2")

	for target_position in ([target_position] if target_position is not None else range(target_length)):
		words_by_letter_there: defaultdict[str, list[str]] = defaultdict(list)
		for word in words_fitting_length:
			if target_position < len(word) and word[target_position] in target_letters:
				words_by_letter_there[word[target_position]].append(word)

		# TODO: put logs behind a verbose flag
		print("target_position", target_position, "words_by_letter_there", words_by_letter_there)

		# Calculate embeddings by calling model.encode()
		# TODO: could try looking up definitions of words for better embeddings
		# (after culling to top N most similar, for efficiency? or before, for accuracy, i.e. to avoid culling based on low quality embeddings)

		embeddings_by_letter_there: dict[str, ndarray] = {}
		for letter, matching_words in words_by_letter_there.items():
			embeddings = model.encode(matching_words)
			embeddings_by_letter_there[letter] = embeddings

		# Calculate the embedding similarities
		if len(target_letters) != 2:
			# TODO: allow more than 2 target letters
			raise ValueError("Exactly two target letters must be specified.")
		letter1, letter2 = target_letters
		embeddings1 = embeddings_by_letter_there.get(letter1)
		embeddings2 = embeddings_by_letter_there.get(letter2)
		if embeddings1 is None or embeddings2 is None:
			continue # TODO: error handling???
		similarities = model.similarity(embeddings1, embeddings2)
		print("similarities", similarities)

		# Find the word pairs
		for i, word1 in enumerate(words_by_letter_there[letter1]):
			for j, word2 in enumerate(words_by_letter_there[letter2]):
				score = similarities[i][j].item()
				results.append((word1, word2, score))

	# Sort by score descending
	return sorted(results, key=lambda x: x[2], reverse=True)
