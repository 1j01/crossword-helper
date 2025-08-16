from collections import Counter, defaultdict
from dataclasses import dataclass
from random import choice
from .dictionary import words

def find_similar_words(length, letter1, letter2, exactly_one_different=False):
	# Placeholder implementation
	return [(f"word{letter1}", f"word{letter2}")]


@dataclass
class Cell:
	position: tuple[int, int]
	letters: str = ""
	barRight: bool = False
	barBottom: bool = False

def generate_rebus(letters_per_cell: int, max_word_length: int, min_chunk_usage: int):
	chunked_words: dict[str, list[str]] = dict()
	words_using_chunk: dict[str, set[str]] = defaultdict(set)
	chunk_counts: Counter[str] = Counter()

	for word in words:
		if len(word) % letters_per_cell == 0 and len(word) <= max_word_length:
			chunks = [word[i:i + letters_per_cell] for i in range(0, len(word), letters_per_cell)]
			chunked_words[word] = chunks
			for chunk in chunks:
				words_using_chunk[chunk].add(word)
				chunk_counts[chunk] += 1

	# Filter out words that have uncommon chunks
	for word, chunks in list(chunked_words.items()):
		if any(chunk_counts[chunk] < min_chunk_usage for chunk in chunks):
			del chunked_words[word]
			for chunk in chunks:
				if chunk in words_using_chunk:
					if word in words_using_chunk[chunk]:
						words_using_chunk[chunk].remove(word)
					if not words_using_chunk[chunk]:
						del words_using_chunk[chunk]

	# Build a map of chunk connections
	next_chunks = defaultdict(set)
	for some_words in words_using_chunk.values():
		for word in some_words:
			chunks = chunked_words[word]
			for i in range(len(chunks) - 1):
				next_chunks[chunks[i]].add(chunks[i + 1])

	# Build a grid
	cells: list[Cell] = []
	connections: list[tuple[tuple[int, int], tuple[int, int]]] = []
	# Start with a random word
	allowed_words = list(chunked_words.keys())
	start_word = choice(allowed_words)
	start_chunks = chunked_words[start_word]
	for i, chunk in enumerate(start_chunks):
		cells.append(Cell(position=(i, 0), letters=chunk))
		if i < len(start_chunks) - 1:
			connections.append(((i, 0), (i + 1, 0)))

	# Add more words
	for _ in range(100): # TODO: options to control generation limits
		# Pick a random cell to branch off from
		cell = choice(cells)
		# Pick a random word that can overlap this cell
		word_to_place = choice(list(words_using_chunk[cell.letters]))
		chunks_to_place = chunked_words[word_to_place]
		# Find the overlap (there may be multiple possible overlap points)
		matching_indices = [i for i, chunk in enumerate(chunks_to_place) if chunk == cell.letters]
		if not matching_indices:
			raise ValueError(f"No matching indices found for '{cell.letters}' in '{word_to_place}'")
		matching_index = choice(matching_indices)
		# TODO: prevent words running together like portmanteaus
		# (and maybe try both orientations in one iteration of cell/word picking for efficiency)
		down = choice([True, False])

		cells_to_place: list[Cell] = []
		for i, chunk in enumerate(chunks_to_place):
			# Include the overlapped chunk to simplify iteration for adding connections
			# Complicates adding the cells though (if we make sure to avoid duplicating the overlapped cell)
			# TODO: instead just keep track of cells to place and positions of the word separately
			# Cells to place can exclude the overlapped cell, and the positions can include it.
			# if i == matching_index:
			# 	continue
			if down:
				cells_to_place.append(Cell(position=(cell.position[0], cell.position[1] + i - matching_index), letters=chunk))
			else:
				cells_to_place.append(Cell(position=(cell.position[0] + i - matching_index, cell.position[1]), letters=chunk))

		# Check for collisions
		collision = False
		for new_cell in cells_to_place:
			if any(existing_cell.position == new_cell.position and existing_cell.letters != new_cell.letters for existing_cell in cells):
				collision = True
				break

		if not collision:
			# Add the new cells (excluding the overlapped cell) and connections
			cells.extend([new_cell for new_cell in cells_to_place if new_cell.position != cell.position])
			for i in range(len(cells_to_place) - 1):
				connections.append((cells_to_place[i].position, cells_to_place[i + 1].position))

	# Calculate bars
	for cell in cells:
		cell.barRight = not any(connection[0] == cell.position and connection[1] == (cell.position[0] + 1, cell.position[1]) for connection in connections)
		cell.barBottom = not any(connection[0] == cell.position and connection[1] == (cell.position[0], cell.position[1] + 1) for connection in connections)

	# print("words_by_chunk:", words_using_chunk)
	# print("chunk_counts:", chunk_counts)
	# print("next_chunks:", next_chunks)

	return cells
