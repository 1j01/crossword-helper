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


def find_matching_rows(
    all_row_candidates: list[list[DropOffRow]]
) -> Optional[list[DropOffRow]]:
    """Find a set of rows that have matching word lengths across all positions.
    
    Args:
        all_row_candidates: List of candidate rows for each key index
    
    Returns:
        A list of rows that match, or None if no match found
    """
    if not all_row_candidates or not all(all_row_candidates):
        return None
    
    # Try to find a combination where all rows have the same word lengths
    # Start with the first row candidates and try to match others
    for first_row in all_row_candidates[0]:
        target_lengths = [len(word) for word in first_row.words]
        
        # Try to find matching rows for all other positions
        selected_rows = [first_row]
        match_found = True
        
        for row_candidates in all_row_candidates[1:]:
            # Find a row with matching lengths
            matching_row = None
            for candidate in row_candidates:
                candidate_lengths = [len(word) for word in candidate.words]
                if candidate_lengths == target_lengths:
                    matching_row = candidate
                    break
            
            if matching_row is None:
                match_found = False
                break
            
            selected_rows.append(matching_row)
        
        if match_found:
            return selected_rows
    
    return None


def generate_drop_off_puzzle(
    key_words: list[str],
    min_word_length: int,
    words_by_length: dict[int, list[str]]
) -> Optional[list[DropOffRow]]:
    """Generate a complete drop-off puzzle.
    
    Args:
        key_words: The words to spell out in columns (must be equal length)
        min_word_length: Minimum length for the shortest word in each row
        words_by_length: Dictionary of words organized by length
    
    Returns:
        List of rows forming a complete puzzle, or None if no solution found
    """
    # Validate that all key words have the same length
    if not key_words:
        return None
    
    key_length = len(key_words[0])
    if not all(len(kw) == key_length for kw in key_words):
        raise ValueError("All key words must have the same length")
    
    # Generate candidates for each row (one row per key letter position)
    all_row_candidates = []
    for key_index in range(key_length):
        logging.info(f"Generating candidates for row {key_index + 1}/{key_length}...")
        row_candidates = generate_row_candidates(
            key_words,
            key_index,
            min_word_length,
            words_by_length
        )
        logging.info(f"  Found {len(row_candidates)} candidates for row {key_index + 1}")
        if not row_candidates:
            logging.warning(f"  No candidates found for row {key_index + 1}")
            return None
        all_row_candidates.append(row_candidates)
    
    # Find a set of rows that match in length
    logging.info("Finding matching rows...")
    result = find_matching_rows(all_row_candidates)
    if result:
        logging.info(f"Found solution with {len(result)} rows")
    else:
        logging.info("No matching rows found")
    return result


def drop_off_rows_to_cells(rows: list[DropOffRow]) -> list[Cell]:
    """Convert drop-off puzzle rows to Cell objects for rendering.

    Args:
        rows: List of DropOffRow objects

    Returns:
        List of Cell objects with appropriate bars set
    """
    cells = []

    for row_idx, row in enumerate(rows):
        col_idx = 0
        
        # Add cells for the words and dropped letters
        for word_idx, word in enumerate(row.words):
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
                col_idx += 1
    
    # Set bars
    # There should be bars at the bottom of all cells except in the columns with dropped letters
    # First, find which columns have the dropped letters
    dropped_letter_columns = set()
    
    # The dropped letters appear after each word except the last
    # Calculate their positions
    col_idx = 0
    for word_idx, word in enumerate(rows[0].words):
        col_idx += len(word)
        if word_idx < len(rows[0].dropped_letters):
            dropped_letter_columns.add(col_idx)
            col_idx += 1
    
    # Set bars for all cells
    for cell in cells:
        x, y = cell.position
        
        # Bar on the right if:
        # 1. This is the last cell in a row, OR
        # 2. This cell is immediately before a dropped letter column, OR
        # 3. This cell is in a dropped letter column
        max_x_in_row = max(c.position[0] for c in cells if c.position[1] == y)
        cell.barRight = (x == max_x_in_row) or (x + 1 in dropped_letter_columns) or (x in dropped_letter_columns)
        
        # Bar on the bottom if:
        # 1. This is the last row, OR
        # 2. This column is NOT a dropped letter column
        max_y = max(c.position[1] for c in cells)
        cell.barBottom = (y == max_y) or (x not in dropped_letter_columns)
    
    return cells
