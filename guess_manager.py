# guess_manager.py
import json
import random
from difflib import SequenceMatcher

class GuessManager:
    def __init__(self, memes_path="memes.json", fuzzy_threshold=0.70):
        self.memes_path = memes_path
        self.fuzzy_threshold = fuzzy_threshold
        self.memes = self._load_memes()
        self.current = {}  # channel_id -> meme dict

    def _load_memes(self):
        with open(self.memes_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def start_game(self, channel_id):
        """Start a meme round in a channel: choose a random meme and store it."""
        meme = random.choice(self.memes)
        self.current[channel_id] = meme
        return meme

    def reveal_answer(self, channel_id):
        meme = self.current.get(channel_id)
        return meme["answers"] if meme else None

    def end_game(self, channel_id):
        self.current.pop(channel_id, None)

    def _similarity(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def check_guess(self, channel_id, guess_text):
        """
        Returns (is_correct: bool, matched_answer: str or None).
        Uses:
         - exact substring/keyword matching (case-insensitive)
         - fallback fuzzy similarity on whole guess vs answer strings
        """
        meme = self.current.get(channel_id)
        if not meme:
            return False, None

        guess = guess_text.lower().strip()

        # 1) keyword/substring match
        for ans in meme.get("answers", []):
            a = ans.lower().strip()
            if a == "": 
                continue
            # exact or contained keywords
            if a in guess or guess in a:
                return True, ans

            # split answer into words and check word presence
            for token in a.split():
                if token and token in guess:
                    return True, ans

        # 2) fuzzy match on whole strings (guess vs each answer)
        best = (0.0, None)
        for ans in meme.get("answers", []):
            ratio = self._similarity(guess, ans.lower())
            if ratio > best[0]:
                best = (ratio, ans)
        if best[0] >= self.fuzzy_threshold:
            return True, best[1]

        return False, None
