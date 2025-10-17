import collections
import json
import math
import re

class LanguageDetector:
    def __init__(self, fingerprint_path="language_fingerprints.json",
                 simplified_chars=None, traditional_chars=None):

        with open(fingerprint_path, "r", encoding="utf-8") as f:
            raw_fp = json.load(f)

        # 过滤掉 Unknown / Other 类别
        self.fingerprints = {
            k: v for k, v in raw_fp.items()
            if k.lower() not in ("unknown", "other")
        }

        self.simplified_chars = simplified_chars or set()
        self.traditional_chars = traditional_chars or set()

    def _is_meaningful(self, ch):
        """只保留语言文字，不要标点符号"""
        cp = ord(ch)
        # 中文、日文、韩文、希腊、阿拉伯、拉丁、西里尔等
        valid = (
            0x4E00 <= cp <= 0x9FFF or
            0x3400 <= cp <= 0x4DBF or
            0x3040 <= cp <= 0x30FF or
            0xAC00 <= cp <= 0xD7AF or
            0x0400 <= cp <= 0x052F or
            0x0370 <= cp <= 0x03FF or
            0x0000 <= cp <= 0x02AF or
            0x0600 <= cp <= 0x06FF or
            0x0590 <= cp <= 0x05FF or
            0x0900 <= cp <= 0x097F or
            0x0E00 <= cp <= 0x0E7F
        )
        return valid and re.match(r'\w', ch)

    def _text_distribution(self, text, top_n=500):
        chars = [ch for ch in text if self._is_meaningful(ch)]
        if not chars:
            return {}
        counter = collections.Counter(chars)
        most_common = counter.most_common(top_n)
        total = sum(freq for _, freq in most_common)
        return {ch: freq / total for ch, freq in most_common}

    def _cosine_similarity(self, dist1, dist2):
        all_chars = set(dist1) | set(dist2)
        dot = sum(dist1.get(c, 0) * dist2.get(c, 0) for c in all_chars)
        norm1 = math.sqrt(sum(v * v for v in dist1.values()))
        norm2 = math.sqrt(sum(v * v for v in dist2.values()))
        return dot / (norm1 * norm2 + 1e-9)

    def _cjk_ratio(self, text):
        total = len(text)
        cjk = sum(0x4E00 <= ord(ch) <= 0x9FFF for ch in text)
        return cjk / total if total else 0

    def _estimate_chinese_variant(self, text):
        simp = trad = 0
        for ch in text:
            if ch in self.simplified_chars:
                simp += 1
            elif ch in self.traditional_chars:
                trad += 1
        if simp + trad == 0:
            return "Chinese_Mixed"
        if simp > trad * 1.3:
            return "Chinese_Simplified"
        elif trad > simp * 1.3:
            return "Chinese_Traditional"
        return "Chinese_Mixed"

    # ------------------------------
    # 主检测逻辑
    # ------------------------------
    def detect(self, text, confidence_threshold=0.12):
        if not text.strip():
            return "Unknown", 0.0, {}

        dist = self._text_distribution(text)
        if not dist:
            return "Unknown", 0.0, {}

        scores = {}
        for lang, fp in self.fingerprints.items():
            sim = self._cosine_similarity(dist, fp["weights"])

            # 对中文系语言增强置信度
            if "Chinese" in lang or "CJK" in lang:
                sim *= 1.4
            scores[lang] = sim

        if not scores:
            return "Unknown", 0.0, {}

        best_lang = max(scores, key=scores.get)
        best_score = scores[best_lang]

        # ---- CJK 特殊增强 ----
        cjk_ratio = self._cjk_ratio(text)
        if cjk_ratio > 0.4 and any(k in best_lang for k in ["Chinese", "CJK"]):
            best_score *= (1 + 0.6 * cjk_ratio)

        # ---- 简繁体细分 ----
        if "Chinese" in best_lang or "CJK" in best_lang:
            zh_variant = self._estimate_chinese_variant(text)
            if zh_variant != "Chinese_Mixed":
                best_lang = zh_variant
                best_score *= 1.05

        # ---- Unknown 抑制策略 ----
        # 如果中文比例高，直接判定为中文
        if cjk_ratio > 0.6 and best_score < confidence_threshold:
            best_lang = "Chinese_Simplified"
            best_score = 0.88

        # 如果最高分太低，也宁可返回置信度低的语言，而不是 Unknown
        if best_score < confidence_threshold:
            best_lang = best_lang or "Chinese_Simplified"

        return best_lang, round(best_score, 4), scores
