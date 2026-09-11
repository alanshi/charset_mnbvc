"""Shared tokenizer / feature extractor for phrase-based language identification.

This module is the single source of truth for how text is turned into features.
It is imported by BOTH the offline fingerprint builder (``data/fingerprints_build.py``)
and the runtime detector (``charset_mnbvc/language_fingerprints.py``) so that the
two can never diverge.

Feature families (every feature carries a script prefix so one flat model can
score all languages):

* spaced scripts (Latin / Cyrillic / Greek / Arabic / Hebrew / Devanagari)
    - word unigram:  ``lat:the``, ``cyrl:что``
    - word bigram :  ``lat:of_the``  (adjacent words -> "词组")
* Hangul
    - word unigram:  ``hangw:안녕하세요``
    - syllable bigram: ``hang:안녕``
* Han (Chinese / Japanese kanji)
    - character bigram : ``han:人民``
    - character trigram: ``han3:人民共``
* Kana
    - character bigram : ``kana:です``
* Thai (unspaced)
    - character bigram : ``thai:กา``
* CJK punctuation (only counted when Han/Kana is present)
    - ``punct:「``, ``punct:。`` (note: ``ー`` U+30FC is a kana character, not punctuation)
"""

import re
from collections import Counter
from typing import Counter as CounterType
from typing import Iterator, Set

# ---------------------------------------------------------------------------
# Script definitions.  Ranges are disjoint; order is irrelevant for matching.
# ---------------------------------------------------------------------------
_SCRIPT_PATTERNS = [
    (
        "han",
        r"\u3005\u3006\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
        r"\U00020000-\U0002a6df\U0002a700-\U0002b73f"
        r"\U0002b740-\U0002b81f\U0002b820-\U0002ceaf"
        r"\U0002ceb0-\U0002ebef\U0002f800-\U0002fa1f"
        r"\U00030000-\U0003134f\U00031350-\U000323af",
    ),
    ("kana", r"\u3040-\u309f\u30a0-\u30ff\u31f0-\u31ff\uff66-\uff9f"),
    ("hang", r"\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f"),
    ("latn", r"A-Za-z\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u024f\u1e00-\u1eff"),
    ("cyrl", r"\u0400-\u052f\u2de0-\u2dff\ua640-\ua69f"),
    ("greek", r"\u0370-\u03ff\u1f00-\u1fff"),
    ("arab", r"\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\ufb50-\ufdff\ufe70-\ufeff"),
    ("hebr", r"\u0590-\u05ff"),
    ("thai", r"\u0e00-\u0e7f"),
    ("deva", r"\u0900-\u097f\ua8e0-\ua8ff"),
]

_MASTER = re.compile(
    "|".join("(?P<%s>[%s]+)" % (name, ranges) for name, ranges in _SCRIPT_PATTERNS)
)

# CJK punctuation that carries language signal (ja vs zh) once Han/Kana exists.
_CJK_PUNCT = re.compile(
    r"[\u3001\u3002\u300c\u300d\u300e\u300f\u3008-\u3011\u3014-\u301b"
    r"\uff01\uff1f\uff0c\uff0e\u2026\u2014]"
)

# Scripts whose runs behave like whitespace-delimited words.
_WORD_SCRIPTS = frozenset({"latn", "cyrl", "greek", "arab", "hebr", "deva"})

# Script names that the tokenizer knows about (used by the builder for metadata).
KNOWN_SCRIPTS = tuple(name for name, _ in _SCRIPT_PATTERNS)


def iter_features(text: str) -> Iterator[str]:
    """Yield script-prefixed features with multiplicity (may repeat)."""
    prev_word = {}
    punct_chars = []
    has_cjk = False

    for match in _MASTER.finditer(text):
        name = match.lastgroup
        run = match.group()

        if name in _WORD_SCRIPTS:
            word = run.lower()
            if len(word) >= 2:
                yield "%s:%s" % (name, word)
            previous = prev_word.get(name)
            if previous is not None:
                yield "%s:%s_%s" % (name, previous, word)
            prev_word[name] = word
        elif name == "hang":
            yield "hangw:%s" % run
            for i in range(len(run) - 1):
                yield "hang:%s" % run[i:i + 2]
            prev_word[name] = run
        elif name == "han":
            has_cjk = True
            for i in range(len(run) - 1):
                yield "han:%s" % run[i:i + 2]
            for i in range(len(run) - 2):
                yield "han3:%s" % run[i:i + 3]
        elif name == "kana":
            has_cjk = True
            for i in range(len(run) - 1):
                yield "kana:%s" % run[i:i + 2]
        elif name == "thai":
            for i in range(len(run) - 1):
                yield "thai:%s" % run[i:i + 2]

    if has_cjk:
        for ch in _CJK_PUNCT.findall(text):
            punct_chars.append(ch)
        for ch in set(punct_chars):
            yield "punct:%s" % ch


def extract_features(text: str) -> Set[str]:
    """Return the set of unique features present in ``text`` (presence model)."""
    return set(iter_features(text))


def count_features(text: str) -> CounterType:
    """Return a ``Counter`` of features in ``text`` (used by the builder)."""
    return Counter(iter_features(text))


def script_counts(text: str) -> CounterType:
    """Return per-script character counts for ``text``."""
    counts = Counter()
    for match in _MASTER.finditer(text):
        counts[match.lastgroup] += len(match.group())
    return counts
