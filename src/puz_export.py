from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

import puz

from .generate_puzzle import Cell


class PuzExportError(Exception):
	"""Raised when a puzzle cannot be exported to .puz format."""


@dataclass(frozen=True)
class _NormalizedCell:
	position: Tuple[int, int]
	letter: str


def _normalize_cells(cells: Iterable[Cell]) -> Dict[Tuple[int, int], _NormalizedCell]:
	if not cells:
		raise PuzExportError("Cannot export an empty puzzle.")

	normalized: Dict[Tuple[int, int], _NormalizedCell] = {}
	for cell in cells:
		x, y = cell.position
		letters = (cell.letters or '').strip()
		if not letters:
			continue
		if len(letters) != 1:
			raise PuzExportError(
				"Multi-letter cells are not currently supported for .puz export."
			)
		upper = letters.upper()
		normalized[(x, y)] = _NormalizedCell(position=(x, y), letter=upper)

	return normalized


def cells_to_puz(cells: Iterable[Cell], metadata: Dict[str, str] | None = None) -> puz.Puzzle:
	"""Convert crossword-helper cells into a puz.Puzzle instance."""
	metadata = metadata or {}
	cells_by_position = _normalize_cells(list(cells))

	if not cells_by_position:
		raise PuzExportError("No filled cells available for .puz export.")

	x_values = [pos[0] for pos in cells_by_position]
	y_values = [pos[1] for pos in cells_by_position]
	min_x, max_x = min(x_values), max(x_values)
	min_y, max_y = min(y_values), max(y_values)
	width = max_x - min_x + 1
	height = max_y - min_y + 1

	solution_chars: list[str] = []
	for y in range(min_y, max_y + 1):
		for x in range(min_x, max_x + 1):
			cell = cells_by_position.get((x, y))
			if cell is None:
				solution_chars.append(puz.BLACKSQUARE)
			else:
				solution_chars.append(cell.letter)

	solution = ''.join(solution_chars)
	fill = ''.join(
		puz.BLANKSQUARE if ch != puz.BLACKSQUARE else puz.BLACKSQUARE
		for ch in solution
	)

	puzzle = puz.Puzzle()
	puzzle.width = width
	puzzle.height = height
	puzzle.solution = solution
	puzzle.fill = fill
	puzzle.title = metadata.get('title', 'Crossword Helper Puzzle')
	puzzle.author = metadata.get('author', 'Crossword Helper')
	puzzle.copyright = metadata.get('copyright', '')
	puzzle.notes = metadata.get('notes', '')

	# Generate placeholder clues so the puzzle loads in Across Lite-compatible apps.
	across_entries, down_entries = puz.get_grid_numbering(solution, width, height)
	grid = puz.Grid(solution, width, height)

	clues: list[str] = []
	for entry in across_entries:
		answer = grid.get_string_for_clue(entry)
		clues.append(f"{entry['num']}A ({len(answer)})")
	for entry in down_entries:
		answer = grid.get_string_for_clue(entry)
		clues.append(f"{entry['num']}D ({len(answer)})")

	puzzle.clues = clues

	return puzzle
