
from .logic import Cell


def render_grid_ascii(cells: list[Cell]):
	min_x = min(cell.position[0] for cell in cells)
	min_y = min(cell.position[1] for cell in cells)
	max_x = max(cell.position[0] for cell in cells)
	max_y = max(cell.position[1] for cell in cells)
	max_cell_width = max(len(cell.letters) for cell in cells)

	output = ""
	for y in range(min_y, max_y + 1):
		for x in range(min_x, max_x + 1):
			cell = next((c for c in cells if c.position == (x, y)), None)
			if cell:
				output += cell.letters.upper().ljust(max_cell_width) + ("|" if cell.barRight else " ")
			else:
				output += "#" * max_cell_width + " "
		output += "\n"
		for x in range(min_x, max_x + 1):
			cell = next((c for c in cells if c.position == (x, y)), None)
			if cell and cell.barBottom:
				output += "-" * max_cell_width + " "
			else:
				output += " " * max_cell_width + " "
		output += "\n"
	
	return output

def render_grid_html(cells: list[Cell]) -> str:
	min_x = min(cell.position[0] for cell in cells)
	min_y = min(cell.position[1] for cell in cells)
	max_x = max(cell.position[0] for cell in cells)
	max_y = max(cell.position[1] for cell in cells)

	html = "<table style='border-collapse: collapse; table-layout: fixed;'>\n"
	for y in range(min_y, max_y + 1):
		html += "  <tr>\n"
		for x in range(min_x, max_x + 1):
			cell = next((c for c in cells if c.position == (x, y)), None)
			if cell:
				style = 'background: white; color: black; text-align: center; border: 3px solid transparent;'
				if cell.barRight:
					style += 'border-right: 3px solid black;'
				if cell.barBottom:
					style += 'border-bottom: 3px solid black;'
				html += f"    <td style='{style}'>{cell.letters.upper()}</td>\n"
			else:
				html += f"    <td style='background: black; border: 3px solid transparent;'></td>\n"
		html += "  </tr>\n"
	html += "</table>\n"
	return html
