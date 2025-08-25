
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
		# lengths = [len(word) for word in words]
		# mean_length = sum(lengths) / len(lengths)
		# variance = sum((length - mean_length) ** 2 for length in lengths) / len(lengths)
		# score = -variance
		score = -1  # determined later
		results.append(JoinResult(words=words, score=score))

	# Try to sort by meaningfulness
	# This approach is fraut because it requires balancing
	# concepts on either side of the subtraction
	# For instance, if the positive list has "BEAUTIFULSUNSETS"
	# it will favor the word sunset unless it is balanced by "SUNSETS TURKEYS"
	# or something in the negative list.
	# And comparing absolute embeddings to a relative vector might tend towards
	# favoring things with smaller magnitudes
	from sentence_transformers import SentenceTransformer
	model = SentenceTransformer("all-MiniLM-L6-v2")
	embeddings = model.encode([' '.join(result.words) for result in results])
	def average_embedding(texts: list[str]):
		vecs = model.encode(texts)
		return sum(vecs) / len(vecs)
	nonsense_embedding = average_embedding([
		"Zxc,mnwerslkfdjSFDKJ",
		"CUPCAKESASSESSAS",
		"SUNSETS DESPISALS",
	])
	reasonable_embedding = average_embedding([
		"A very reasonable phrase",
		"BEAUTIFULSUNSETS",
		"CURIOUSITY KILLEDTHECAT",
	])
	reasonableness_vector = reasonable_embedding - nonsense_embedding
	for i, result in enumerate(results):
		result_embedding = embeddings[i]
		# Cosine similarity
		# AI autocomplete suggested this formula
		# Does it actually make sense to compare an embedding to a vector difference?
		cosine_similarity = (result_embedding @ reasonableness_vector) / ( ( (result_embedding @ result_embedding) ** 0.5 ) * ( (reasonableness_vector @ reasonableness_vector) ** 0.5 ) )
		# Combine with previous score
		# result_score = result.score + cosine_similarity
		# or don't
		result_score = cosine_similarity
		results[i] = JoinResult(words=result.words, score=result_score)

	# Sort by score descending
	return sorted(results, key=lambda result: result.score, reverse=True)
