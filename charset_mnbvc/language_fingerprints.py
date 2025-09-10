import collections
import json
import math


class LanguageDetector:
    def __init__(self, fingerprint_path="language_fingerprints.json"):
        with open(fingerprint_path, "r", encoding="utf-8") as f:
            self.fingerprints = json.load(f)

    def _text_distribution(self, text, top_n=500):
        """计算文本字符频率分布"""
        counter = collections.Counter(text)
        most_common = counter.most_common(top_n)
        total = sum(freq for _, freq in most_common)
        return {char: freq / total for char, freq in most_common if char.strip()}

    def _cosine_similarity(self, dist1, dist2):
        """计算余弦相似度"""
        # 只保留两者都出现的字符
        common_chars = set(dist1.keys()) & set(dist2.keys())
        if not common_chars:
            return 0.0
        dot = sum(dist1[c] * dist2[c] for c in common_chars)
        norm1 = math.sqrt(sum(v * v for v in dist1.values()))
        norm2 = math.sqrt(sum(v * v for v in dist2.values()))
        return dot / (norm1 * norm2)

    def detect(self, text):
        """检测文本所属语种"""
        dist = self._text_distribution(text)
        scores = {}

        for lang, fp in self.fingerprints.items():
            sim = self._cosine_similarity(dist, fp["weights"])
            scores[lang] = sim

        # 找到最匹配的语种
        best_lang = max(scores, key=scores.get)
        return best_lang, scores[best_lang], scores
