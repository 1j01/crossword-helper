
from collections import defaultdict
import re
import sys

from .dictionary import words_by_length


def find_superpuzzitions(target_length: int | None, target_patterns: list[re.Pattern], target_position: int | None = None, exactly_one_different=False) -> list[tuple[str, str, float]]:
	"""
	Find and rank candidate word pairs that fit divergent grids for Schrodinger puzzles.
	
	Note that rather than one pattern like `..A.(E|S)(H|S).` to find word pairs
	where a grid contains `A_EH` and `A_SS` superimposed,
	this function takes a list of patterns like `..A.EH.` and `..A.SS.`
	"""
	for pattern in target_patterns:
		if not (pattern.flags & re.IGNORECASE):
			raise ValueError("Input regexp pattern must be case insensitive")

	if exactly_one_different:
		# TODO: implement
		# also rename to be more general since patterns can have multiple alternations
		raise NotImplementedError("Exactly one different letter mode is not implemented.")

	results: list[tuple[str, str, float]] = []

	from sentence_transformers import SentenceTransformer
	model = SentenceTransformer("all-MiniLM-L6-v2")

	some_words_of_target_length = False
	for target_length in ([target_length] if target_length is not None else words_by_length.keys()):
		if target_length not in words_by_length:
			continue
		some_words_of_target_length = True

		for target_position in ([target_position] if target_position is not None else range(target_length)):
			words_by_pattern: defaultdict[str, list[str]] = defaultdict(list)
			for word in words_by_length[target_length]:
				if target_position < len(word): #and word[target_position] in target_letters:
					# words_by_letter_there[word[target_position]].append(word)
					for pattern in target_patterns:
						m = pattern.search(word)
						if m and m.start() == target_position:
							words_by_pattern[str(pattern)].append(word)
							break

			# TODO: put logs behind a verbose flag
			print("target_position", target_position, "words_by_pattern", words_by_pattern, file=sys.stderr)

			# Calculate embeddings by calling model.encode()
			# TODO: could try looking up definitions of words for better embeddings
			# (after culling to top N most similar, for efficiency? or before, for accuracy, i.e. to avoid culling based on low quality embeddings)

			embeddings_by_pattern = { k: model.encode(v) for k, v in words_by_pattern.items() }

			# Calculate the embedding similarities
			if len(target_patterns) != 2:
				# TODO: allow more than 2 target patterns
				# (or just one in case it can just find and rank individual words
				# based on their quality rating from the word list)
				raise ValueError("Exactly two target patterns must be specified.")
			p1, p2 = target_patterns
			embeddings1 = embeddings_by_pattern.get(str(p1))
			embeddings2 = embeddings_by_pattern.get(str(p2))
			if embeddings1 is None or embeddings2 is None:
				continue # TODO: error handling???
			similarities = model.similarity(embeddings1, embeddings2)
			print("similarities", similarities, file=sys.stderr)

			# Find the word pairs
			for i, word1 in enumerate(words_by_pattern[str(p1)]):
				for j, word2 in enumerate(words_by_pattern[str(p2)]):
					score = similarities[i][j].item()
					results.append((word1, word2, score))

	if not some_words_of_target_length:
		raise ValueError("No words of the specified target length(s) were found in the word list.")

	# Sort by score descending
	return sorted(results, key=lambda x: x[2], reverse=True)
