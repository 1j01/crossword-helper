"""Generate drop-off puzzles.

Drop-off puzzles are where in each row there are a series of words, each using
one fewer letter than the last. The letter that is dropped is placed in between
the word that has it and that doesn't. The columns that contain the dropped off
letters spell specific key words. There are bars between the rows everywhere
except these columns.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from .generate_puzzle import Cell
from .render import render_grid_ascii


@dataclass
class DropOffRow:
    """A single row in a drop-off puzzle."""
    words: list[str]
    dropped_letters: list[str]  # The letters dropped at each position


def find_anagrams(word: str, words_by_length: dict[int, list[str]]) -> list[str]:
    """Find all anagrams of the given word in the word list."""
    sorted_word = ''.join(sorted(word.lower()))
    target_length = len(word)

    if target_length not in words_by_length:
        return []

    anagrams = []
    for candidate in words_by_length[target_length]:
        if ''.join(sorted(candidate.lower())) == sorted_word:
            anagrams.append(candidate)
    
    return anagrams


def find_words_containing_letters(letters: str, min_length: int, words_by_length: dict[int, list[str]]) -> list[str]:
    """Find words containing all the given letters, with length >= min_length."""
    required_letters = set(letters.lower())
    candidates = []

    if not words_by_length:
        return []

    for length in range(min_length, max(words_by_length.keys()) + 1):
        if length not in words_by_length:
            continue
        for word in words_by_length[length]:
            word_letters = set(word.lower())
            if required_letters.issubset(word_letters):
                candidates.append(word)

    return candidates


def generate_row_candidates(
    key_words: list[str],
    key_index: int,
    min_word_length: int,
    words_by_length: dict[int, list[str]],
    max_candidates: int = 1000
) -> list[DropOffRow]:
    """Generate candidate rows for a given key letter index.
    
    Args:
        key_words: The key words to spell out in columns
        key_index: Index of the key letters we're working with
        min_word_length: Minimum length for the final word in the row
        words_by_length: Dictionary of words organized by length
        max_candidates: Maximum number of candidates to return
    
    Returns:
        List of candidate rows
    """
    # Get the key letters at this index from all key words
    key_letters = [kw[key_index].lower() for kw in key_words]
    
    # Find candidate first words (must contain all key letters)
    min_first_word_length = min_word_length + len(key_words)
    first_word_candidates = find_words_containing_letters(
        ''.join(key_letters), 
        min_first_word_length, 
        words_by_length
    )
    
    # Limit the number of first word candidates to avoid exponential explosion
    first_word_candidates = first_word_candidates[:100]
    
    row_candidates = []
    
    for first_word in first_word_candidates:
        # Try to build a complete row
        rows = build_row_from_first_word(first_word, key_letters, words_by_length)
        row_candidates.extend(rows)
        
        # Stop if we have enough candidates
        if len(row_candidates) >= max_candidates:
            row_candidates = row_candidates[:max_candidates]
            break
    
    return row_candidates


def build_row_from_first_word(
    first_word: str,
    key_letters: list[str],
    words_by_length: dict[int, list[str]],
    max_anagrams_per_step: int = 10
) -> list[DropOffRow]:
    """Build all possible rows starting from a given first word.

    For each key letter, we try removing it and finding anagrams.
    This generates all valid sequences of words where each word is an
    anagram of the previous word minus one of the key letters.

    Args:
        first_word: The starting word for the row
        key_letters: List of letters to drop in sequence (one per step)
        words_by_length: Dictionary of words organized by length
        max_anagrams_per_step: Maximum number of anagrams to consider at each step

    Returns:
        List of all possible valid rows starting from first_word
    """
    # We'll use recursive search to find all valid sequences
    def search(current_word: str, remaining_keys: list[str], words_so_far: list[str], dropped_so_far: list[str]) -> list[DropOffRow]:
        if not remaining_keys:
            # Base case: we've successfully built a complete row
            return [DropOffRow(words=words_so_far, dropped_letters=dropped_so_far)]
        
        results = []
        key_letter = remaining_keys[0].lower()
        
        # Check if current word contains the key letter
        if key_letter not in current_word.lower():
            return []
        
        # Try each occurrence of the key letter
        for i, char in enumerate(current_word.lower()):
            if char == key_letter:
                # Remove this occurrence
                word_without_letter = current_word[:i] + current_word[i+1:]
                
                # Find anagrams of the word without this letter
                anagrams = find_anagrams(word_without_letter, words_by_length)
                
                # Limit the number of anagrams to avoid exponential explosion
                anagrams = anagrams[:max_anagrams_per_step]
                
                for anagram in anagrams:
                    # Recursively search with the next word
                    sub_results = search(
                        anagram,
                        remaining_keys[1:],
                        words_so_far + [anagram],
                        dropped_so_far + [key_letter.upper()]
                    )
                    results.extend(sub_results)
        
        return results
    
    return search(first_word, key_letters, [first_word], [])


def count_black_cells_needed(row_lengths: list[int], target_lengths: list[int]) -> int:
    """Count the number of black cells needed to pad a row to match target lengths.
    
    Args:
        row_lengths: Actual word lengths in the row
        target_lengths: Target word lengths
    
    Returns:
        Number of black cells needed (0 if lengths match)
    """
    if len(row_lengths) != len(target_lengths):
        return float('inf')
    
    black_cells = 0
    for row_len, target_len in zip(row_lengths, target_lengths):
        if row_len > target_len:
            return float('inf')  # Can't fit
        black_cells += target_len - row_len
    
    return black_cells


def find_matching_rows(
    all_row_candidates: list[list[DropOffRow]],
    allow_partial: bool = False
) -> Optional[list[DropOffRow]]:
    """Find a set of rows that have matching word lengths across all positions.
    
    Args:
        all_row_candidates: List of candidate rows for each key index
        allow_partial: If True, allow partial puzzles with padding or missing rows
    
    Returns:
        A list of rows that match, or None if no match found
    """
    if not all_row_candidates:
        return None
    
    # Filter out empty candidate lists
    non_empty_candidates = [candidates for candidates in all_row_candidates if candidates]
    
    if not non_empty_candidates:
        if allow_partial:
            # Return empty rows for all positions
            return [None] * len(all_row_candidates)
        return None
    
    if not allow_partial and not all(all_row_candidates):
        return None
    
    # Try to find a combination where all rows have the same word lengths
    # Start with the first non-empty row candidates and try to match others
    best_solution = None
    best_black_cells = float('inf')
    
    for first_row in non_empty_candidates[0]:
        target_lengths = [len(word) for word in first_row.words]
        
        # Try to find matching rows for all other positions
        selected_rows = []
        total_black_cells = 0
        solution_valid = True
        
        for row_candidates in all_row_candidates:
            if not row_candidates:
                if allow_partial:
                    # Missing row - will be represented as blank
                    selected_rows.append(None)
                else:
                    solution_valid = False
                    break
            else:
                # Find a row with matching or padable lengths
                best_candidate = None
                best_candidate_black_cells = float('inf')
                
                for candidate in row_candidates:
                    candidate_lengths = [len(word) for word in candidate.words]
                    black_cells = count_black_cells_needed(candidate_lengths, target_lengths)
                    
                    if black_cells < best_candidate_black_cells:
                        best_candidate = candidate
                        best_candidate_black_cells = black_cells
                        if black_cells == 0:
                            break  # Perfect match
                
                if best_candidate is None or (not allow_partial and best_candidate_black_cells > 0):
                    solution_valid = False
                    break
                
                selected_rows.append(best_candidate)
                total_black_cells += best_candidate_black_cells
        
        if solution_valid and total_black_cells < best_black_cells:
            best_solution = selected_rows
            best_black_cells = total_black_cells
            if best_black_cells == 0:
                break  # Perfect solution found
    
    return best_solution


def generate_drop_off_puzzle(
    key_words: list[str],
    min_word_length: int,
    words_by_length: dict[int, list[str]],
    allow_partial: bool = False
) -> Optional[list[Optional[DropOffRow]]]:
    """Generate a complete drop-off puzzle.
    
    Args:
        key_words: The words to spell out in columns (must be equal length)
        min_word_length: Minimum length for the shortest word in each row
        words_by_length: Dictionary of words organized by length
        allow_partial: If True, allow partial puzzles with padding or missing rows
    
    Returns:
        List of rows forming a complete puzzle, or None if no solution found.
        When allow_partial=True, some rows may be None (representing blank rows).
    """
    # Validate that all key words have the same length
    if not key_words:
        return None
    
    key_length = len(key_words[0])
    if not all(len(kw) == key_length for kw in key_words):
        max_len = max(len(kw) for kw in key_words)
        logging.error("All key words must have the same length. Given key words:")
        for word in key_words:
            logging.error(f"  |{word.ljust(max_len)}| (length {len(word)})")
        return None
    
    # Generate candidates for each row (one row per key letter position)
    all_row_candidates = []
    for key_index in range(key_length):
        row_name = f"{key_index + 1}/{key_length} ({'->'.join([kw[key_index].upper() for kw in key_words])})"
        logging.info(f"Generating candidates for row {row_name}...")
        row_candidates = generate_row_candidates(
            key_words,
            key_index,
            min_word_length,
            words_by_length
        )
        logging.info(f"  Found {len(row_candidates)} candidates for row {row_name}")
        if logging.getLogger().isEnabledFor(logging.INFO):
            for i, candidate in enumerate(row_candidates[:5]):
                logging.info(f"    Candidate {i + 1}: {render_grid_ascii(drop_off_rows_to_cells([candidate]))}")
        if not row_candidates:
            logging.warning(f"  No candidates found for row {row_name}")
            if not allow_partial:
                return None
        all_row_candidates.append(row_candidates)
    
    # Find a set of rows that match in length
    logging.info("Finding rows that match in length...")
    result = find_matching_rows(all_row_candidates, allow_partial=allow_partial)
    if result:
        non_none_rows = [row for row in result if row is not None]
        if non_none_rows:
            logging.info(f"Found solution with matching row lengths: {[len(row.words) if row else 0 for row in result]}")
        else:
            logging.info("Found solution with all blank rows")
    else:
        logging.info("No matching set of row lengths found")
    return result


def drop_off_rows_to_cells(rows: list[Optional[DropOffRow]]) -> list[Cell]:
    """Convert drop-off puzzle rows to Cell objects for rendering.

    Args:
        rows: List of DropOffRow objects (can include None for blank rows)

    Returns:
        List of Cell objects with appropriate bars set
    """
    if not rows:
        return []
    
    # First pass: determine target word lengths from the first non-None row
    target_word_lengths = None
    for row in rows:
        if row is not None:
            target_word_lengths = [len(word) for word in row.words]
            break
    
    if target_word_lengths is None:
        # All rows are None - cannot create a meaningful puzzle
        logging.warning("All rows are blank, no puzzle to display")
        return []
    
    cells = []
    dropped_letter_columns = set()
    
    # Calculate the column positions for dropped letters based on target lengths
    dropped_letter_col_positions = []
    col_pos = 0
    for word_len in target_word_lengths[:-1]:
        col_pos += word_len
        dropped_letter_col_positions.append(col_pos)
        col_pos += 1  # The dropped letter column itself
    
    for row_idx, row in enumerate(rows):
        col_idx = 0
        
        if row is None:
            # Blank row - add space cells for the entire width
            total_width = sum(target_word_lengths) + len(target_word_lengths) - 1
            for x in range(total_width):
                cell = Cell(position=(x, row_idx), letters=' ')
                cells.append(cell)
        else:
            # Calculate padding needed for each word
            for word_idx, word in enumerate(row.words):
                target_len = target_word_lengths[word_idx]
                actual_len = len(word)
                padding = target_len - actual_len
                
                # Add black cells as padding on the left
                for _ in range(padding):
                    cell = Cell(position=(col_idx, row_idx), letters='#')
                    cells.append(cell)
                    col_idx += 1
                
                # Add cells for this word
                for char in word:
                    cell = Cell(position=(col_idx, row_idx), letters=char)
                    cells.append(cell)
                    col_idx += 1
                
                # Add a cell for the dropped letter if this isn't the last word
                if word_idx < len(row.dropped_letters):
                    dropped_letter = row.dropped_letters[word_idx]
                    cell = Cell(position=(col_idx, row_idx), letters=dropped_letter)
                    cells.append(cell)
                    dropped_letter_columns.add(col_idx)
                    col_idx += 1
    
    # Set bars for all cells
    for cell in cells:
        x, y = cell.position
        
        # Bar on the right if the right border is the border of a dropped letter column
        is_before_dropped_column = (x + 1 in dropped_letter_columns)
        is_in_dropped_column = (x in dropped_letter_columns)
        cell.barRight = is_before_dropped_column or is_in_dropped_column
        
        # Bar on the bottom everywhere except in dropped letter columns (and not the bottom of the grid)
        cell.barBottom = (x not in dropped_letter_columns) and y < len(rows) - 1
    
    return cells


def generate_all_candidates_puzzle(
    key_words: list[str],
    min_word_length: int,
    words_by_length: dict[int, list[str]],
    max_candidates_per_row: int = 100
) -> Optional[list[Optional[DropOffRow]]]:
    """Generate a puzzle that combines all row candidates into a single large puzzle.
    
    Args:
        key_words: The words to spell out in columns (must be equal length)
        min_word_length: Minimum length for the shortest word in each row
        words_by_length: Dictionary of words organized by length
        max_candidates_per_row: Maximum number of candidates to include per row position
    
    Returns:
        List of all row candidates combined, or None if no candidates found
    """
    # Validate that all key words have the same length
    if not key_words:
        return None
    
    key_length = len(key_words[0])
    if not all(len(kw) == key_length for kw in key_words):
        max_len = max(len(kw) for kw in key_words)
        logging.error("All key words must have the same length. Given key words:")
        for word in key_words:
            logging.error(f"  |{word.ljust(max_len)}| (length {len(word)})")
        return None
    
    # Generate candidates for each row (one row per key letter position)
    all_rows = []
    for key_index in range(key_length):
        row_name = f"{key_index + 1}/{key_length} ({'->'.join([kw[key_index].upper() for kw in key_words])})"
        logging.info(f"Generating candidates for row {row_name}...")
        row_candidates = generate_row_candidates(
            key_words,
            key_index,
            min_word_length,
            words_by_length,
            max_candidates=max_candidates_per_row
        )
        logging.info(f"  Found {len(row_candidates)} candidates for row {row_name}")
        
        if row_candidates:
            all_rows.extend(row_candidates[:max_candidates_per_row])
        else:
            logging.warning(f"  No candidates found for row {row_name}")
    
    return all_rows if all_rows else None
