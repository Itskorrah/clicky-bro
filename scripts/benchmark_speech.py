#!/usr/bin/env python3
"""Offline WER/CER evaluator for speech transcripts. Never invokes a provider.

Dataset JSON: {"cases":[{"id":"demo-en","language":"en-AU","reference":"hello world"}]}
Prediction JSON: {"predictions":[{"id":"demo-en","text":"hello world"}]}
Command: python scripts/benchmark_speech.py --dataset cases.json \
  --prediction parakeet=parakeet.json --prediction whisper=whisper.json \
  --out .local/evidence/speech-metrics.json
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sys
import unicodedata

ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
WORD = re.compile(r"\w+", re.UNICODE)


def words(text: str) -> list[str]:
    return WORD.findall(unicodedata.normalize("NFKC", text).casefold())


def characters(text: str) -> list[str]:
    return list(" ".join(words(text)))


def edit_distance(reference: list[str], hypothesis: list[str]) -> int:
    """Levenshtein distance using O(min(n,m)) space."""
    if len(reference) < len(hypothesis):
        reference, hypothesis = hypothesis, reference
    previous = list(range(len(hypothesis) + 1))
    for i, actual in enumerate(reference, 1):
        current = [i]
        for j, predicted in enumerate(hypothesis, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + (actual != predicted)))
        previous = current
    return previous[-1]


@dataclass(frozen=True)
class Counts:
    word_errors: int = 0
    ref_words: int = 0
    char_errors: int = 0
    ref_chars: int = 0
    cases: int = 0

    def add(self, other: "Counts") -> "Counts":
        return Counts(self.word_errors + other.word_errors, self.ref_words + other.ref_words,
                      self.char_errors + other.char_errors, self.ref_chars + other.ref_chars,
                      self.cases + other.cases)

    def metrics(self) -> dict:
        return {"cases": self.cases, "reference_words": self.ref_words,
                "word_errors": self.word_errors, "wer": round(self.word_errors / self.ref_words, 6),
                "reference_characters": self.ref_chars, "character_errors": self.char_errors,
                "cer": round(self.char_errors / self.ref_chars, 6)}


def load_cases(location: Path) -> dict[str, tuple[str, str]]:
    raw = json.loads(location.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("cases"), list) or not raw["cases"]:
        raise ValueError("Dataset must contain a non-empty cases list")
    cases: dict[str, tuple[str, str]] = {}
    for item in raw["cases"]:
        if not isinstance(item, dict):
            raise ValueError("Every case must be an object")
        identifier, reference, language = item.get("id"), item.get("reference"), item.get("language")
        if not isinstance(identifier, str) or not ID.fullmatch(identifier) or identifier in cases:
            raise ValueError("Case IDs must be unique simple identifiers")
        if not isinstance(reference, str) or not words(reference):
            raise ValueError("Every reference must contain spoken text")
        if not isinstance(language, str) or not 1 <= len(language) <= 40:
            raise ValueError("Every case requires a language label")
        cases[identifier] = (language, reference)
    return cases


def load_predictions(location: Path, expected: set[str]) -> dict[str, str]:
    raw = json.loads(location.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("predictions"), list):
        raise ValueError("Predictions must contain a predictions list")
    predictions: dict[str, str] = {}
    for item in raw["predictions"]:
        if not isinstance(item, dict):
            raise ValueError("Each prediction must be an object")
        identifier, transcript = item.get("id"), item.get("text")
        if not isinstance(identifier, str) or identifier in predictions or not isinstance(transcript, str):
            raise ValueError("Predictions require unique IDs and text")
        predictions[identifier] = transcript
    if set(predictions) != expected:
        raise ValueError("Prediction IDs must match dataset exactly; no missing/extra cases")
    return predictions


def evaluate(cases: dict[str, tuple[str, str]], predictions: dict[str, str]) -> dict:
    if set(cases) != set(predictions):
        raise ValueError("Dataset and predictions differ")
    overall = Counts()
    by_language: dict[str, Counts] = defaultdict(Counts)
    for identifier, (language, reference) in cases.items():
        actual_words, predicted_words = words(reference), words(predictions[identifier])
        actual_chars, predicted_chars = characters(reference), characters(predictions[identifier])
        if not actual_words or not actual_chars:
            raise ValueError("Dataset has an empty reference")
        count = Counts(edit_distance(actual_words, predicted_words), len(actual_words),
                       edit_distance(actual_chars, predicted_chars), len(actual_chars), 1)
        overall = overall.add(count)
        by_language[language] = by_language[language].add(count)
    return {"overall": overall.metrics(),
            "by_language": {language: by_language[language].metrics()
                            for language in sorted(by_language)}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--prediction", required=True, action="append", metavar="MODEL=FILE",
                        help="Existing local transcript JSON; no model is started")
    parser.add_argument("--out", type=Path, help="Write metadata-only JSON, refuse overwrite")
    args = parser.parse_args(argv)
    try:
        cases = load_cases(args.dataset)
        reports = {}
        for source in args.prediction:
            label, marker, filename = source.partition("=")
            if not marker or not ID.fullmatch(label) or label in reports:
                raise ValueError("Each --prediction needs a distinct simple MODEL=FILE")
            reports[label] = evaluate(cases, load_predictions(Path(filename), set(cases)))
        report = {"schema": 1, "normalisation": "Unicode NFKC casefold; punctuation stripped; words separated by spaces",
                  "sample_count": len(cases), "models": reports,
                  "limits": "Transcript-only accuracy, not native inference, latency or privacy certification"}
        if args.out:
            location = args.out.resolve()
            location.parent.mkdir(parents=True, exist_ok=True)
            descriptor = os.open(location, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(report, stream, indent=2, ensure_ascii=False)
                stream.write("\n")
        else:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"speech benchmark error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
