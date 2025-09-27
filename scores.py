# scores.py
import json
import os

class ScoreManager:
    def __init__(self, path="scores.json"):
        self.path = path
        self.scores = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return {}
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.scores, f, indent=2)

    def add_point(self, user_id, points=1):
        uid = str(user_id)
        self.scores[uid] = self.scores.get(uid, 0) + points
        self._save()
        return self.scores[uid]

    def get_score(self, user_id):
        return self.scores.get(str(user_id), 0)

    def top(self, n=10):
        # returns list of tuples [(user_id_str, points), ...] sorted desc
        items = sorted(self.scores.items(), key=lambda kv: kv[1], reverse=True)
        return items[:n]

class LocalScoreManager:
    def __init__(self, path="local_scores.json"):
        self.path = path
        self.scores = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return {}
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.scores, f, indent=2)

    def add_point(self, guild_id, user_id, points=1):
        gid = str(guild_id)
        uid = str(user_id)
        if gid not in self.scores:
            self.scores[gid] = {}
        self.scores[gid][uid] = self.scores[gid].get(uid, 0) + points
        self._save()
        return self.scores[gid][uid]

    def top(self, guild_id, n=10):
        gid = str(guild_id)
        if gid not in self.scores:
            return []
        items = sorted(self.scores[gid].items(), key=lambda kv: kv[1], reverse=True)
        return items[:n]
