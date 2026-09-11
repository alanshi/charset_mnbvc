# -*- coding: utf-8 -*-
"""Tests for the phrase-based language detector.

Run with::

    python -m unittest tests.test_language_fingerprints -v
"""

import unittest

from charset_mnbvc.language_fingerprints import LanguageDetector

# Representative sentences, distinct from the build corpus sample.
GOLDEN = {
    "zh-Hans": "中华人民共和国是世界上人口最多的国家。",
    "zh-Hant": "中華人民共和國是世界上人口最多的國家。",
    "ja": "これは日本語の文です。東京大学の研究者が新しい技術を開発した。",
    "ko": "안녕하세요 저는 한국 사람입니다.",
    "en": "The president of the French Republic announced a new reform.",
    "fr": "Le président de la République française a annoncé une nouvelle réforme.",
    "de": "Der Präsident der Französischen Republik kündigte eine neue Reform an.",
    "es": "El presidente de la República Francesa anunció una nueva reforma.",
    "it": "Il presidente della Repubblica francese ha annunciato una nuova riforma.",
    "pt": "O presidente da República Francesa anunciou uma nova reforma.",
    "id": "Presiden Republik Prancis mengumumkan reformasi baru.",
    "vi": "Tổng thống Cộng hòa Pháp đã công bố một cải cách mới.",
    "tr": "Fransa Cumhuriyeti Cumhurbaşkanı yeni bir reform duyurdu.",
    "ru": "Президент Французской Республики объявил о новой реформе.",
    "th": "เตรียมตัวให้พร้อมทั้งสภาพร่างกายและจิตใจก่อนบิน",
}

LEGACY_LABELS = {
    "Simplified_Chinese", "Traditional_Chinese", "Chinese_Simplified",
    "Chinese_Traditional", "Chinese_Mixed", "Japanese_Hiragana",
    "Japanese_Katakana", "Korean_Hangul", "Latin", "Cyrillic",
}


class TestLanguageDetector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.detector = LanguageDetector()

    def test_golden_languages(self):
        for expected, text in GOLDEN.items():
            with self.subTest(lang=expected):
                label, score, _ = self.detector.detect(text)
                self.assertEqual(label, expected)
                self.assertGreater(score, 0.5)

    def test_traditional_chinese_regression(self):
        """Regression: traditional text used to be forced to Chinese_Simplified."""
        label, _, _ = self.detector.detect(
            "中華人民共和國是世界上人口最多的國家。")
        self.assertEqual(label, "zh-Hant")

    def test_simplified_traditional_are_distinguished(self):
        simp, _, _ = self.detector.detect("这是一个简体中文的句子，软件和网络。")
        trad, _, _ = self.detector.detect("這是一個繁體中文的句子，軟體和網路。")
        self.assertEqual(simp, "zh-Hans")
        self.assertEqual(trad, "zh-Hant")

    def test_unknown_inputs(self):
        for text in ("", "   ", "\n\t", "。！？…", "12345 67890", "!@#$%^&*()"):
            with self.subTest(text=text):
                label, score, scores = self.detector.detect(text)
                self.assertEqual(label, "Unknown")
                self.assertEqual(score, 0.0)
                self.assertEqual(scores, {})

    def test_return_shape(self):
        label, score, scores = self.detector.detect(GOLDEN["en"])
        self.assertIsInstance(label, str)
        self.assertIsInstance(score, float)
        self.assertIsInstance(scores, dict)

    def test_scores_are_bounded_posteriors(self):
        _, _, scores = self.detector.detect(GOLDEN["fr"])
        self.assertEqual(set(scores), set(self.detector.languages))
        for value in scores.values():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)
        self.assertAlmostEqual(sum(scores.values()), 1.0, places=4)

    def test_no_legacy_labels_leak(self):
        for text in GOLDEN.values():
            label, _, _ = self.detector.detect(text)
            self.assertNotIn(label, LEGACY_LABELS)

    def test_deterministic(self):
        text = GOLDEN["de"]
        first = self.detector.detect(text)
        second = self.detector.detect(text)
        self.assertEqual(first, second)

    def test_confidence_threshold_override(self):
        # A very high threshold must force Unknown even for clean input.
        label, _, _ = self.detector.detect(GOLDEN["en"], confidence_threshold=1.1)
        self.assertEqual(label, "Unknown")


if __name__ == "__main__":
    unittest.main()
