
import itertools
from typing import NamedTuple

class JoinResult(NamedTuple):
	words: tuple[str, ...]
	score: float

def join_words(
	word_lists: list[list[str]],
	target_length: int | None, 
) -> list[JoinResult]:
	"""
	Forms longer answers by joining words from multiple lists,
	where the word lengths sum to the target length.
	"""

	if len(word_lists) < 2:
		raise ValueError("At least two word lists must be specified.")

	# Code suggested by AI:
	# TODO: optimize by breaking down word lists by length,
	# choosing indices from 0-target_length,
	# and only combining words whose lengths sum to target_length
	# at least for pairs (two lists)
	results = []
	for words in itertools.product(*word_lists):
		combined_word = ''.join(words)
		if target_length is not None and len(combined_word) != target_length:
			continue
		# Simple scoring: prefer words with more even length distribution
		lengths = [len(word) for word in words]
		mean_length = sum(lengths) / len(lengths)
		variance = sum((length - mean_length) ** 2 for length in lengths) / len(lengths)
		score = -variance
		results.append(JoinResult(words=words, score=score))

	# TODO: sort by meaningfulness
	# Could I compare embeddings to a the subtraction of something like
	# embedding("A very reasonable phrase") - embedding("Zxc,mnwerslkfdjSFDKJ")?

	# Sort by score descending
	return sorted(results, key=lambda result: result.score, reverse=True)
