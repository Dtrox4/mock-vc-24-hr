import json
from pathlib import Path

TRACKED_WORDS_FILE = Path("tracked_words.json")

# Load from file or start fresh
if TRACKED_WORDS_FILE.exists():
    with open(TRACKED_WORDS_FILE, "r") as f:
        tracked_words = json.load(f)
else:
    tracked_words = {}

def save_words():
    with open(TRACKED_WORDS_FILE, "w") as f:
        json.dump(tracked_words, f, indent=4)

def increment_word_count(word):
    word = word.lower()
    if word in tracked_words:
        tracked_words[word] += 1
        save_words()

def add_word(word):
    word = word.lower()
    if word not in tracked_words:
        tracked_words[word] = 0
        save_words()
        return True
    return False

def remove_word(word):
    word = word.lower()
    if word in tracked_words:
        del tracked_words[word]
        save_words()
        return True
    return False

def get_word_count(word):
    return tracked_words.get(word.lower(), 0)

def get_tracked_words():
    return list(tracked_words.keys())
