
from .generate_puzzle import Cell


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

def render_grid_svg(cells: list[Cell]) -> str:
	min_x = min(cell.position[0] for cell in cells)
	min_y = min(cell.position[1] for cell in cells)
	max_x = max(cell.position[0] for cell in cells)
	max_y = max(cell.position[1] for cell in cells)
	cell_width = 30
	cell_height = 30

	svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{(max_x - min_x + 1) * cell_width}" height="{(max_y - min_y + 1) * cell_height}" style="font-family: monospace;">\n'
	svg += f'<g transform="translate({-min_x * cell_width}, {-min_y * cell_height})">\n'
	for y in range(min_y, max_y + 1):
		for x in range(min_x, max_x + 1):
			cell = next((c for c in cells if c.position == (x, y)), None)
			if cell:
				svg += f'  <text x="{(x + 1/2) * cell_width}" y="{(y + 1/2) * cell_height}" font-size="16" text-anchor="middle" dominant-baseline="middle" fill="black">{cell.letters.upper()}</text>\n'
				svg += f'  <line x1="{(x + 1) * cell_width}" y1="{y * cell_height}" x2="{(x + 1) * cell_width}" y2="{(y + 1) * cell_height}" stroke="{"black" if cell.barRight else "rgba(0, 0, 0, 0.2)"}" stroke-width="{4 if cell.barRight else 2}" />\n'
				svg += f'  <line x1="{x * cell_width}" y1="{(y + 1) * cell_height}" x2="{(x + 1) * cell_width}" y2="{(y + 1) * cell_height}" stroke="{"black" if cell.barBottom else "rgba(0, 0, 0, 0.2)"}" stroke-width="{4 if cell.barBottom else 2}" />\n'
			else:
				svg += f'  <rect x="{x * cell_width}" y="{y * cell_height}" width="{cell_width}" height="{cell_height}" fill="black" />\n'
	svg += '</g>\n'
	svg += '</svg>\n'
	return svg
