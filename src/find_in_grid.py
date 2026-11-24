from src.dictionary import load_words

words, words_by_length = load_words(score_filter=0.5)


# For diagonals, see find_diagonals.js

# This finds words by taking one letter from each successive row
# For now, assume full length (grid spanning) words and one orientation (down)

# sketch of one approach,
# if a full match is a given:  
# - form sets of words containing a given letter at a given position for each possible nth letter
# - take the intersection of said sets

# I went with a slightly different approach though

# TODO: find shorter (non-spanning) words; will need to optimize at this point
# TODO: search horizontally as well, by transposing the grid
# TODO: integrate diagonal word search from JS

def find_words_in_grid(grid: list[list[str]]) -> list[str]:
	height = len(grid)
	width = len(grid[0])
	found = []

	row_sets = []

	for y in range(height):
		row_set = {grid[y][x] for x in range(width) if grid[y][x] not in ". #"}
		row_sets.append(row_set)

	# print("row_sets", row_sets)

	for word in words_by_length[len(grid)]:
		if all(letter in row_sets[i] for i, letter in enumerate(word)):
			found.append(word)

	trivial = []
	for x in range(width):
		trivial.append("".join(grid[y][x] for y in range(height)))

	return [word for word in found if not word in trivial]

if __name__ == "__main__":
	DATA = """
R,E,P,L,E,T,E
E,T,A,I,L,E,R
.,C,R,E,M,A,.
.,.,O,B,I,.,.
.,A,D,A,S,H,.
E,V,I,C,T,E,D
L,A,C,K,I,N,G
	"""

	grid = [line.split(",") for line in DATA.strip().splitlines()]
	found = find_words_in_grid(grid)
	print(f"Found {len(found)} words reading down the grid while making arbitrary lateral jumps:")
	for word in found:
		print(f"- {word}")


