
from typing import NamedTuple
from itertools import chain, combinations

def powerset(iterable):
    """
	Returns all possible subsets of the input iterable,
	including the empty set and the full set of values from the iterable.

    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
	"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

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
				# handle multiple substitutions in one word [TODO: optionally]
				for substitution_points in powerset(occurances):
					if not substitution_points:
						continue
					# Check for overlapping substitutions
					# This assumes substitution_points is ordered for efficiency.
					overlaps = False
					for i in range(len(substitution_points) - 1):
						if substitution_points[i] + len(base_seq) > substitution_points[i+1]:
							overlaps = True
							break
					if overlaps:
						continue

					other_words_that_must_exist = []
					for seq in letter_sequences[1:]:
						new_word = word
						for point in substitution_points:
							new_word = new_word[:point] + seq + new_word[point+len(base_seq):]
						other_words_that_must_exist.append(new_word)
					if all(other_word in all_words_set for other_word in other_words_that_must_exist):
						results.append(SubstitutionalResult((word, *other_words_that_must_exist)))

	return results
