import collections
import json

# -----------------------------
# 定义 Unicode 范围 -> 语言映射
# -----------------------------
LANGUAGE_RANGES = {
    "Latin": [
        (0x0000, 0x007F),
        (0x0080, 0x00FF),
        (0x0100, 0x017F),
        (0x0180, 0x024F),
        (0x1E00, 0x1EFF),
    ],
    "CJK": [
        (0x4E00, 0x9FFF),
        (0x3400, 0x4DBF),
        (0x20000, 0x2A6DF),
        (0x2A700, 0x2B73F),
        (0x2B740, 0x2B81F),
        (0x2B820, 0x2CEAF),
        (0x2CEB0, 0x2EBEF),
        (0x30000, 0x3134F),
    ],
    "Japanese_Hiragana": [(0x3040, 0x309F)],
    "Japanese_Katakana": [
        (0x30A0, 0x30FF),
        (0x31F0, 0x31FF),
        (0xFF65, 0xFF9F),
    ],
    "Korean_Hangul": [
        (0xAC00, 0xD7A3),
        (0x1100, 0x11FF),
        (0x3130, 0x318F),
    ],
    "Cyrillic": [
        (0x0400, 0x04FF),
        (0x0500, 0x052F),
        (0x2DE0, 0x2DFF),
        (0xA640, 0xA69F),
    ],
    "Greek": [
        (0x0370, 0x03FF),
        (0x1F00, 0x1FFF),
    ],
    "Arabic": [
        (0x0600, 0x06FF),
        (0x0750, 0x077F),
        (0x08A0, 0x08FF),
        (0xFB50, 0xFDFF),
        (0xFE70, 0xFEFF),
    ],
    "Hebrew": [(0x0590, 0x05FF)],
    "Devanagari": [
        (0x0900, 0x097F),
        (0xA8E0, 0xA8FF),
    ],
    "Thai": [(0x0E00, 0x0E7F)],
    "Tibetan": [(0x0F00, 0x0FFF)],
    "Georgian": [
        (0x10A0, 0x10FF),
        (0x2D00, 0x2D2F),
    ],
    "Armenian": [(0x0530, 0x058F)],
}


# -----------------------------
# 简繁体参考表
# -----------------------------


def load_opencc_sets(st_file="STCharacters.txt", ts_file="TSCharacters.txt"):
    simplified_chars = set()
    traditional_chars = set()

    # 简体 -> 繁体
    with open(st_file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                s, t = parts
                simplified_chars.add(s)
                traditional_chars.add(t)

    # 反向补充（防止漏字）
    with open(ts_file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                t, s = parts
                simplified_chars.add(s)
                traditional_chars.add(t)

    print(f"✅ Loaded {len(simplified_chars)} simplified and {len(traditional_chars)} traditional chars.")
    return simplified_chars, traditional_chars


opencc_sets = load_opencc_sets(
    "data/STCharacters.txt",
    "data/TSCharacters.txt"
)

SIMPLIFIED_CHARS = opencc_sets[0]
TRADITIONAL_CHARS = opencc_sets[1]


def detect_language(char):
    """检测字符所属语言类别"""
    codepoint = ord(char)
    for lang, ranges in LANGUAGE_RANGES.items():
        for start, end in ranges:
            if start <= codepoint <= end:
                return lang
    return "Other"


def classify_chinese_char(char):
    """根据字符判断简繁体"""
    if char in SIMPLIFIED_CHARS:
        return "Simplified_Chinese"
    elif char in TRADITIONAL_CHARS:
        return "Traditional_Chinese"
    else:
        return "Chinese_Unknown"


def build_fingerprints(file_path, top_n=500, encoding="utf-8", output_json="language_fingerprints.json"):
    """
    从混合语料中提取各语种（含简体/繁体）的高频字符指纹
    """
    with open(file_path, "r", encoding=encoding) as f:
        text = f.read()

    counter = collections.Counter(text)
    lang_counters = {}

    for char, freq in counter.items():
        if char.strip() == "":
            continue
        lang = detect_language(char)

        # 如果是CJK区域，再判断简繁体
        if lang == "CJK":
            sub_lang = classify_chinese_char(char)
            lang = sub_lang if sub_lang != "Chinese_Unknown" else "CJK"

        if lang not in lang_counters:
            lang_counters[lang] = collections.Counter()
        lang_counters[lang][char] += freq

    fingerprints = {}
    for lang, cnt in lang_counters.items():
        most_common = cnt.most_common(top_n)
        total = sum(freq for _, freq in most_common)
        fingerprints[lang] = {
            "ordered": [char for char, _ in most_common],
            "weights": {char: round(freq / total, 6) for char, freq in most_common}
        }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(fingerprints, f, ensure_ascii=False, indent=2)

    print(f"指纹已生成 ✅ -> {output_json}")
    print("包含语种:", ", ".join(sorted(fingerprints.keys())))


if __name__ == "__main__":
    build_fingerprints(
        "/Users/alan/Downloads/Genshin_AnimeGameData.jsonl",
        top_n=1000,
        output_json="language_fingerprints.json"
    )
