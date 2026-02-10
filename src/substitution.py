
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

	base_seq = letter_sequences[0]
	for length, words in words_by_length.items():
		for word in words:
			if base_seq in word:
				occurances = (i for i in range(len(word) - len(base_seq) + 1)
				  if word[i:i+len(base_seq)] == base_seq
				)
				# TODO: handle multiple substitutions in one word [optionally]
				for i in occurances:
					prefix = word[:i]
					suffix = word[i+len(base_seq):]

					other_words_that_must_exist = [prefix + seq + suffix for seq in letter_sequences[1:]]
					if all(other_word in all_words_set for other_word in other_words_that_must_exist):
						results.append(SubstitutionalResult((word, *other_words_that_must_exist)))

	return results
