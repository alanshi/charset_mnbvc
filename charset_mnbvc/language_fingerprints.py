"""Phrase-based language identification.

Replaces the previous character-unigram cosine detector with a two-stage model:

1. **Script gate** - fast, deterministic.  Counts characters per Unicode script,
   rejects text with no meaningful script, applies hard locks (kana => Japanese,
   Hangul => Korean) and narrows the candidate languages to those sharing the
   dominant scripts.  Single-candidate texts short-circuit without scoring.
2. **Phrase model** - presence-based multinomial Naive Bayes over script-prefixed
   word / phrase / n-gram features (see :mod:`charset_mnbvc.langid_tokenizer`).
   Confidence is a calibrated softmax posterior over the candidate languages.

Labels are BCP-47 language tags (``zh-Hans``, ``zh-Hant``, ``ja``, ``ko``, ``en``,
``fr`` ...).  ``Unknown`` is returned when the evidence is too weak.
"""

import json
import math
import os

from .langid_tokenizer import extract_features, script_counts

DEFAULT_FINGERPRINT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "language_fingerprints.json"
)

# Kana is unique to Japanese: any meaningful kana share locks the language.
_KANA_LOCK_RATIO = 0.05
# Hangul dominance locks Korean.
_HANGUL_LOCK_RATIO = 0.20


class LanguageDetector:
    def __init__(self, fingerprint_path=None, simplified_chars=None,
                 traditional_chars=None):
        # ``simplified_chars`` / ``traditional_chars`` are kept for backward
        # compatibility with the old character-based API and are ignored.
        path = fingerprint_path or DEFAULT_FINGERPRINT_PATH
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        self.meta = raw.get("meta", {})
        self.languages = raw.get("languages", {})

        self.floor = float(self.meta.get("floor", 1e-8))
        self.log_floor = math.log(self.floor)
        self.default_threshold = float(self.meta.get("threshold", 0.25))
        self.default_margin = float(self.meta.get("margin", 0.05))
        self.min_script_ratio = float(self.meta.get("min_script_ratio", 0.05))
        self.script_to_langs = self.meta.get("scripts", {})

        # Pre-compute log-probabilities once at load time.
        self._logp = {}
        for lang, data in self.languages.items():
            self._logp[lang] = {
                feature: math.log(prob)
                for feature, prob in data.get("features", {}).items()
                if prob > 0
            }

    # ------------------------------------------------------------------
    # Stage 1: script gate
    # ------------------------------------------------------------------
    def _candidates(self, counts):
        total = sum(counts.values())
        if total <= 0:
            return set()

        known = set(self.languages)
        kana = counts.get("kana", 0)
        han = counts.get("han", 0)

        # Hard locks first: kana can only be Japanese, Hangul dominance Korean.
        if kana and kana / float(kana + han or 1) >= _KANA_LOCK_RATIO:
            return {"ja"} & known
        if counts.get("hang", 0) / float(total) >= _HANGUL_LOCK_RATIO:
            return {"ko"} & known

        candidates = set()
        for script, count in counts.items():
            if count / float(total) >= self.min_script_ratio:
                candidates |= set(self.script_to_langs.get(script, ()))
        return candidates & known

    # ------------------------------------------------------------------
    # Stage 2: presence-based multinomial Naive Bayes
    # ------------------------------------------------------------------
    def _nb_scores(self, features, candidates):
        scores = {}
        for lang in candidates:
            logp = self._logp[lang]
            score = 0.0
            for feature in features:
                value = logp.get(feature)
                score += value if value is not None else self.log_floor
            scores[lang] = score
        return scores

    @staticmethod
    def _softmax(scores):
        top = max(scores.values())
        exps = {lang: math.exp(value - top) for lang, value in scores.items()}
        total = sum(exps.values())
        if total <= 0:
            n = len(scores)
            return {lang: 1.0 / n for lang in scores}
        return {lang: value / total for lang, value in exps.items()}

    # ------------------------------------------------------------------
    # Public API (unchanged signature / return shape)
    # ------------------------------------------------------------------
    def detect(self, text, confidence_threshold=None):
        """Detect the language of ``text``.

        Returns ``(label, confidence, scores)`` where ``scores`` maps every known
        language to a calibrated posterior (0.0 for non-candidates).
        """
        if not text or not text.strip():
            return "Unknown", 0.0, {}

        features = extract_features(text)
        if not features:
            return "Unknown", 0.0, {}

        candidates = self._candidates(script_counts(text))
        if not candidates:
            return "Unknown", 0.0, {}

        posterior = self._softmax(self._nb_scores(features, candidates))

        best = max(posterior, key=posterior.get)
        best_score = posterior[best]
        ordered = sorted(posterior.values(), reverse=True)
        margin = ordered[0] - ordered[1] if len(ordered) > 1 else 1.0

        threshold = (self.default_threshold if confidence_threshold is None
                     else float(confidence_threshold))

        all_scores = {lang: round(posterior.get(lang, 0.0), 6)
                      for lang in self.languages}

        if best_score < threshold or margin < self.default_margin:
            return "Unknown", round(best_score, 4), all_scores
        return best, round(best_score, 4), all_scores
