# Copilot:

def find_similar_words(target_length, letter1, letter2, position, exact_one_diff=False):
    import nltk
    from nltk.corpus import wordnet as wn

    nltk.download('wordnet')

    # Get all words of the target length
    words = [word for word in wn.words() if len(word) == target_length]

    similar_pairs = []

    for word in words:
        if word[position] == letter1 and word != letter1:
            for candidate in words:
                if candidate[position] == letter2 and candidate != word:
                    if exact_one_diff:
                        # Check if they differ by exactly one letter
                        diff_count = sum(1 for a, b in zip(word, candidate) if a != b)
                        if diff_count == 1:
                            similar_pairs.append((word, candidate))
                    else:
                        # Check semantic similarity
                        syn1 = wn.synsets(word)
                        syn2 = wn.synsets(candidate)
                        if syn1 and syn2:
                            similarity = syn1[0].wup_similarity(syn2[0])
                            if similarity is not None and similarity > 0.5:  # Threshold for similarity
                                similar_pairs.append((word, candidate))

    return similar_pairs

# ChatGPT:

from collections import defaultdict
from sentence_transformers import SentenceTransformer, util

def load_words(file_path):
    """Load words from a file into a list."""
    with open(file_path, "r", encoding="utf-8") as f:
        return [w.strip().lower() for w in f if w.strip().isalpha()]

def letter_pairs_fast(words, letter_a, letter_b, one_letter_diff=True, similarity_threshold=0.6):
    """Efficiently find semantically similar word pairs with letter swaps."""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    results = []
    
    # Group by word length
    words_by_len = defaultdict(list)
    for w in words:
        words_by_len[len(w)].append(w)
    
    for length, group in words_by_len.items():
        if one_letter_diff:
            # Generate wildcard patterns for each position
            patterns = defaultdict(list)
            for word in group:
                for i in range(length):
                    patterns[word[:i] + "*" + word[i+1:]].append((word, i))
            
            # Compare only words sharing the same wildcard pattern
            for bucket in patterns.values():
                for i in range(len(bucket)):
                    for j in range(i+1, len(bucket)):
                        w1, pos1 = bucket[i]
                        w2, pos2 = bucket[j]
                        if pos1 != pos2:
                            continue
                        a, b = w1[pos1], w2[pos2]
                        if not ((a == letter_a and b == letter_b) or (a == letter_b and b == letter_a)):
                            continue
                        sim = util.cos_sim(
                            model.encode(w1, convert_to_tensor=True),
                            model.encode(w2, convert_to_tensor=True)
                        ).item()
                        if sim >= similarity_threshold:
                            results.append((w1, w2, round(sim, 3)))
        else:
            # Compare words with same length where letters match except at chosen letter positions
            for i in range(length):
                bucket = [w for w in group if w[i] in (letter_a, letter_b)]
                for x in range(len(bucket)):
                    for y in range(x+1, len(bucket)):
                        w1 = bucket[x]
                        w2 = bucket[y]
                        if not ((w1[i] == letter_a and w2[i] == letter_b) or (w1[i] == letter_b and w2[i] == letter_a)):
                            continue
                        sim = util.cos_sim(
                            model.encode(w1, convert_to_tensor=True),
                            model.encode(w2, convert_to_tensor=True)
                        ).item()
                        if sim >= similarity_threshold:
                            results.append((w1, w2, round(sim, 3)))

    return sorted(results, key=lambda x: -x[2])

if __name__ == "__main__":
    words = load_words("words.txt")
    results = letter_pairs_fast(words, letter_a="p", letter_b="s", one_letter_diff=False, similarity_threshold=0.6)
    for w1, w2, sim in results:
        print(f"{w1} — {w2} (similarity: {sim})")
