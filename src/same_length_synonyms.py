import nltk
from nltk.corpus import wordnet

nltk.download('wordnet')

def normalize_word(word: str) -> str:
    return word.replace('_', '').replace('-', '').lower()

def synonyms_equal_length_for_all_words():
    results = {}

    all_words = set(wordnet.words())
    for word in all_words:
        normalized_word = normalize_word(word)
        word_length = len(normalized_word)
        synonyms = set()
        
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                lemma_name = lemma.name()
                normalized_lemma = normalize_word(lemma_name)
                if len(normalized_lemma) == word_length and normalized_lemma != normalized_word:
                    synonyms.add(lemma_name)
        
        if synonyms:
            results[word] = sorted(synonyms)

    return results

all_synonyms = synonyms_equal_length_for_all_words()

for i, (word, syns) in enumerate(all_synonyms.items()):
    print(word, ":", syns)
