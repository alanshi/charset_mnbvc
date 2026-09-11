import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from charset_mnbvc import language_fingerprints

if __name__ == "__main__":
    # 默认加载随包分发的指纹文件 charset_mnbvc/data/language_fingerprints.json
    detector = language_fingerprints.LanguageDetector()

    # 测试：基于语料词组（词/词对/字 n-gram）区分语种，标签为 BCP-47
    samples = {
        "zh-Hans": "中华人民共和国是世界上人口最多的国家。",
        "zh-Hant": "中華人民共和國是世界上人口最多的國家。",
        "ja": "これは日本語の文です。",
        "ko": "안녕하세요 저는 한국 사람입니다.",
        "en": "This is an English sentence.",
        "fr": "Le président de la République française a annoncé une nouvelle réforme.",
        "de": "Der Präsident der Französischen Republik kündigte eine neue Reform an.",
        "ru": "Президент Французской Республики объявил о новой реформе.",
        "th": "เตรียมตัวให้พร้อมทั้งสภาพร่างกายและจิตใจก่อนบิน",
    }

    for expected, text in samples.items():
        lang, score, all_scores = detector.detect(text)
        flag = "OK" if lang == expected else "!!"
        print(f"[{flag}] 输入: {text}")
        print(f"      期望: {expected}, 预测语种: {lang}, 置信度: {score:.4f}")
        print(f"      所有分数: {all_scores}\n")
