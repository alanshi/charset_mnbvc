"""Build phrase-based language fingerprints from a parallel multilingual corpus.

The reference corpus is a JSONL file where every line contains the *same*
content translated into many languages, one field per language, e.g.::

    {"zh_text": "...", "cht_text": "...", "en_text": "...", "ja_text": "...",
     "扩展字段": "{\"other_texts\": {\"tr\": \"...\"}}", ...}

Field name -> language mapping is declared in ``FIELD_TO_LABEL``.  Features are
extracted with the *shared* tokenizer (``charset_mnbvc.langid_tokenizer``) so the
fingerprints are guaranteed to match what the runtime detector extracts.

Usage::

    python data/fingerprints_build.py \
        --corpus data_pack/Genshin_AnimeGameData.jsonl \
        --out charset_mnbvc/data/language_fingerprints.json \
        --max-lines 15000

The output is a JSON document::

    {
      "meta": {
        "schema": 2, "built_at": ..., "corpus": ..., "max_lines": ...,
        "top_k": ..., "floor": ..., "threshold": ..., "margin": ...,
        "min_script_ratio": ...,
        "languages": [...], "scripts": {"latn": [...], "han": [...], ...}
      },
      "languages": {
        "de": {"total": <int>, "features": {"lat:der": <p>, ...}},
        ...
      }
    }
"""

import argparse
import collections
import json
import os
import sys
import time

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from charset_mnbvc.langid_tokenizer import count_features  # noqa: E402

# Field name -> BCP-47 label.
FIELD_TO_LABEL = {
    "ar_text": "ar",
    "cht_text": "zh-Hant",
    "de_text": "de",
    "en_text": "en",
    "eo_text": "eo",
    "es_text": "es",
    "fr_text": "fr",
    "he_text": "he",
    "id_text": "id",
    "it_text": "it",
    "ja_text": "ja",
    "ko_text": "ko",
    "nl_text": "nl",
    "pt_text": "pt",
    "ru_text": "ru",
    "sv_text": "sv",
    "th_text": "th",
    "vi_text": "vi",
    "zh_text": "zh-Hans",
}

# Languages nested inside the "扩展字段" -> "other_texts" object.
OTHER_LABELS = {"tr": "tr"}

# Primary script(s) used by each language; written into meta so the runtime
# script gate is fully data-driven.
LANG_SCRIPTS = {
    "ar": ["arab"],
    "de": ["latn"],
    "en": ["latn"],
    "eo": ["latn"],
    "es": ["latn"],
    "fr": ["latn"],
    "he": ["hebr"],
    "id": ["latn"],
    "it": ["latn"],
    "ja": ["han", "kana"],
    "ko": ["hang"],
    "nl": ["latn"],
    "pt": ["latn"],
    "ru": ["cyrl"],
    "sv": ["latn"],
    "th": ["thai"],
    "tr": ["latn"],
    "vi": ["latn"],
    "zh-Hans": ["han"],
    "zh-Hant": ["han"],
}

EXT_FIELD = "扩展字段"

# Drop singleton features every this many lines to bound memory while streaming.
_PRUNE_EVERY = 3000


def build(corpus_path, output_path, max_lines, top_k, floor, threshold,
          margin, min_script_ratio, prune):
    counters = collections.defaultdict(collections.Counter)
    lines = 0

    with open(corpus_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            if lines >= max_lines:
                break
            lines += 1
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                obj = json.loads(raw_line)
            except ValueError:
                continue

            for field, label in FIELD_TO_LABEL.items():
                text = obj.get(field)
                if text:
                    counters[label].update(count_features(text))

            ext = obj.get(EXT_FIELD)
            if ext:
                try:
                    nested = json.loads(ext)
                except (ValueError, TypeError):
                    nested = {}
                for key, value in (nested.get("other_texts") or {}).items():
                    label = OTHER_LABELS.get(key)
                    if label and isinstance(value, str) and value:
                        counters[label].update(count_features(value))

            if prune and lines % _PRUNE_EVERY == 0:
                for label, counter in list(counters.items()):
                    if len(counter) > 100000:
                        counters[label] = collections.Counter(
                            {k: v for k, v in counter.items() if v > 1}
                        )
                print("  ...processed %d lines" % lines, flush=True)

    languages = {}
    scripts = collections.defaultdict(set)
    for label, counter in counters.items():
        if not counter:
            continue
        total = sum(counter.values())
        features = {
            feature: round(count / float(total), 9)
            for feature, count in counter.most_common(top_k)
        }
        languages[label] = {"total": total, "features": features}
        for script in LANG_SCRIPTS.get(label, []):
            scripts[script].add(label)

    meta = {
        "schema": 2,
        "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "corpus": os.path.basename(corpus_path),
        "max_lines": lines,
        "top_k": top_k,
        "floor": floor,
        "threshold": threshold,
        "margin": margin,
        "min_script_ratio": min_script_ratio,
        "languages": sorted(languages.keys()),
        "scripts": {name: sorted(langs) for name, langs in sorted(scripts.items())},
    }

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "languages": languages}, f,
                  ensure_ascii=False, separators=(",", ":"))

    size_mb = os.path.getsize(output_path) / (1024.0 * 1024.0)
    print("Built fingerprints from %d lines -> %s (%.2f MB)"
          % (lines, output_path, size_mb))
    print("Languages: %s" % ", ".join(meta["languages"]))
    for label in meta["languages"]:
        print("  %-8s features=%d total=%d"
              % (label, len(languages[label]["features"]), languages[label]["total"]))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        default=os.path.join(_REPO_ROOT, "data_pack", "Genshin_AnimeGameData.jsonl"),
        help="parallel multilingual JSONL corpus",
    )
    parser.add_argument(
        "--out",
        default=os.path.join(_REPO_ROOT, "charset_mnbvc", "data",
                             "language_fingerprints.json"),
        help="output fingerprint JSON path",
    )
    parser.add_argument("--max-lines", type=int, default=15000,
                        help="maximum corpus lines to read (sampling)")
    parser.add_argument("--top-k", type=int, default=10000,
                        help="features kept per language")
    parser.add_argument("--floor", type=float, default=1e-8,
                        help="OOV probability floor for scoring")
    parser.add_argument("--threshold", type=float, default=0.25,
                        help="default posterior threshold for Unknown")
    parser.add_argument("--margin", type=float, default=0.10,
                        help="default best-vs-second margin for Unknown")
    parser.add_argument("--min-script-ratio", type=float, default=0.05,
                        help="minimum script share to activate a script family")
    parser.add_argument("--no-prune", action="store_true",
                        help="disable periodic singleton pruning")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    build(
        corpus_path=args.corpus,
        output_path=args.out,
        max_lines=args.max_lines,
        top_k=args.top_k,
        floor=args.floor,
        threshold=args.threshold,
        margin=args.margin,
        min_script_ratio=args.min_script_ratio,
        prune=not args.no_prune,
    )


if __name__ == "__main__":
    main()
