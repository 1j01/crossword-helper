import json
import logging

def load_words(score_filter: float | None = None) -> tuple[list[str], dict[int, list[str]]]:
    """Load words from a word database JSON file, optionally filtering on word quality."""

    # with open('data/ridyhew-3fbbc4-word-list.txt', 'r', encoding='utf-8') as f:
    # 	words = f.read().splitlines()

    # words_by_length = defaultdict(list)
    # for word in words:
    #     words_by_length[len(word)].append(word)

    # worddb.json structure: { words: {[length]: [[word, score], ...], ...} }
    with open('data/worddb.json', 'r', encoding='utf-8') as f:
        worddb = json.load(f)
        words_by_length: dict[int, list[str]] = {}
        all_quality_scores = [score for length, words_of_length in worddb['words'].items() for word, score in words_of_length]
        logging.info(f"Quality scores: min {min(all_quality_scores)}, max {max(all_quality_scores)}, mean {sum(all_quality_scores) / len(all_quality_scores):.4f}")
        for length, words_of_length in worddb['words'].items():
            words_by_length[int(length)] = [word for word, score in words_of_length if score_filter is None or score >= score_filter]
        words = [word for sublist in words_by_length.values() for word in sublist]

    logging.info(f"Loaded {len(words)} words from worddb.json")
    logging.info(f"First 10 words: {words[:10]}")
    logging.info(f"Last 10 words: {words[-10:]}")

    return words, words_by_length

