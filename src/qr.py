from collections import defaultdict
import itertools
import json
import qrcode

from count_isolated_cells import count_isolated_cells


id = "GEuZfB1sjbTaeHJ3n9tp"

def generate_qr_candidate(id: str, nonce="") -> qrcode.QRCode:
	data = "https://crosshare.org/crosswords/" + id + ("?" + nonce if nonce else "")
	qr = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_L)
	qr.add_data(data)
	qr.make(fit=True)
	return qr

def qr_to_crosshare_puzzle(qr: qrcode.QRCode, id: str) -> str:

	matrix = qr.get_matrix()

	height = len(matrix)
	width = len(matrix[0])

	grid = []
	for row in matrix:
		for cell in row:
			grid.append("." if cell else " ")

	result = {
		"id": id,
		"width": width,
		"height": height,
		"grid": grid,
		"vBars": [],
		"hBars": [],
		"hidden": [],
		"cellStyles": {},
		"clues": {},
		"title": None,
		"notes": None,
		"blogPost": None,
		"guestConstructor": None,
		"isPrivate": False,
		"alternates": [],
		"userTags": [],
		"symmetry": 3, # No symmetry
	}

	return json.dumps(result, indent=2)

def count_horizontal_word_lengths(matrix: list[list[bool]]) -> dict[int, int]:
	word_lengths = defaultdict(int)

	for row in matrix:
		current_length = 0
		for cell in row:
			if cell:
				current_length += 1
			else:
				if current_length > 0:
					word_lengths[current_length] += 1
					current_length = 0
		if current_length > 0:
			word_lengths[current_length] += 1

	return word_lengths

def score_candidate(qr: qrcode.QRCode) -> int:
	matrix = qr.get_matrix()
	transpose = [list(x) for x in zip(*matrix)]

	across_word_lengths = count_horizontal_word_lengths(matrix)
	down_word_lengths = count_horizontal_word_lengths(transpose)

	# TODO: check for unches
	score = 0
	for word_lengths in (across_word_lengths, down_word_lengths):
		for length, count in word_lengths.items():
			if length == 1:
				score -= 3 * count
			elif length == 2:
				score -= 1 * count
	return score

def render_qr(qr: qrcode.QRCode) -> None:
	matrix = qr.get_matrix()
	for row in matrix:
		print("".join(["██" if cell else "  " for cell in row]))

def render(best_qr: qrcode.QRCode, best_score: int, latest_qr: qrcode.QRCode|None=None, latest_score: int|None=None) -> None:
	# Clear screen and move cursor to top-left
	print("\033[2J\033[H", end="")
	if latest_qr is not None:
		print("Latest Candidate:")
		print(f"Score: {latest_score}")
		render_qr(latest_qr)
	print("\nBest Candidate So Far:")
	print(f"Score: {best_score}")
	render_qr(best_qr)

def nonces():
	alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_~"
	length = 0
	while True:
		for nonce_tuple in itertools.product(alphabet, repeat=length):
			yield "".join(nonce_tuple)
		length += 1

# print(list(itertools.islice(nonces(), 1000)))

if __name__ == "__main__":
	best_qr = generate_qr_candidate(id)
	best_score = -99999999999
	try:
		for nonce in nonces():
			qr = generate_qr_candidate(id, str(nonce))
			score = score_candidate(qr)
			if score > best_score:
				best_score = score
				best_qr = qr
			render(best_qr, best_score, qr, score)
	except KeyboardInterrupt:
		pass
	render(best_qr, best_score)
	print("\nBest QR Code JSON:")
	print(qr_to_crosshare_puzzle(best_qr, id))
	print("\nNumber of isolated cells:", count_isolated_cells(best_qr.get_matrix()))

