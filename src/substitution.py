
from collections import defaultdict
import itertools
import logging
from typing import NamedTuple
import re

# from torch import Tensor

class SubstitutionalResult(NamedTuple):
	words: tuple[str, ...]
	# score: float

def find_substitutions(
	words_by_length: dict[int, list[str]],
	letter_sequences: list[str]
) -> list[SubstitutionalResult]:
	"""
	Find word sets that differ by a certain substitution.

	For example, for ["IR", "RATA"], it might find "STIR"->"STRATA".
	"""
	
	if len(letter_sequences) < 2:
		raise ValueError("At least two letter sequences must be provided.")

	results: list[SubstitutionalResult] = []

	all_words_set = set(word for words in words_by_length.values() for word in words)

	for length, words in words_by_length.items():
		for word in words:
			if letter_sequences[0] in word:
				# try different positions
				# in case of multiple occurrences in a word
				for i in range(len(word) - len(letter_sequences[0]) + 1):
					if word[i:i+len(letter_sequences[0])] == letter_sequences[0]:
						prefix = word[:i]
						suffix = word[i+len(letter_sequences[0]):]

						other_words_that_must_exist = [prefix + seq + suffix for seq in letter_sequences[1:]]
						if all(other_word in all_words_set for other_word in other_words_that_must_exist):
							results.append(SubstitutionalResult((word, *other_words_that_must_exist)))

	return results
