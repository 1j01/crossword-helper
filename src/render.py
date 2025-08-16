
from .logic import Cell


def render_grid(cells: list[Cell]):
	min_x = min(cell.position[0] for cell in cells)
	min_y = min(cell.position[1] for cell in cells)
	max_x = max(cell.position[0] for cell in cells)
	max_y = max(cell.position[1] for cell in cells)
	max_cell_width = max(len(cell.letters) for cell in cells)

	for y in range(min_y, max_y + 1):
		for x in range(min_x, max_x + 1):
			cell = next((c for c in cells if c.position == (x, y)), None)
			if cell:
				print(cell.letters.ljust(max_cell_width), end=" ")
			else:
				print(".".ljust(max_cell_width), end=" ")
		print()
