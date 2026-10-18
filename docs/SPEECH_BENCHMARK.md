# Offline speech-quality evaluation

**Implemented:** local Python transcript WER/CER calculation and safe summary report.

**Not implemented by this tool:** downloading models, invoking a native recogniser, running microphone tests, measuring inference time or proving the app is offline. Models and privacy are verified separately.

## Why it exists

Clicky Bro already integrates on-device Parakeet on macOS and Windows. Before selecting a Whisper model or inference backend, compare predictions against the same reference transcripts. Avoid trusting vendor claims or judging quality on one sentence.

Store source recordings and predictions in a private, ignored location (for example the existing .local/evidence directory). **Do not commit user recordings, sensitive transcriptions or API keys.**

## Input contracts

A reference dataset is JSON with non-empty cases, each with a unique ID, language and manually verified reference:

~~~json
{
  "cases": [
    {"id": "en-au-001", "language": "en-AU", "reference": "Please open my calendar."},
    {"id": "ar-001", "language": "ar", "reference": "مرحباً بالعالم"}
  ]
}
~~~

A model's precomputed predictions use exactly those IDs:

~~~json
{
  "predictions": [
    {"id": "en-au-001", "text": "Please open my calendar."},
    {"id": "ar-001", "text": "مرحباً بالعالم"}
  ]
}
~~~

Use locally obtained transcription results for each engine. A missing or extra ID is an error, not a silently excluded example. Empty predictions are legitimate recogniser failures and count against that model.

## Run

~~~bash
python3 scripts/benchmark_speech.py \
  --dataset .local/evidence/speech/cases.json \
  --prediction parakeet=.local/evidence/speech/parakeet.json \
  --prediction whisper-small=.local/evidence/speech/whisper-small.json \
  --out .local/evidence/speech/metrics.json

python3 -m unittest tests/test_benchmark_speech.py -v
~~~

This command reads local files and computes metrics; it does not contact a provider or download weights. The output contains only aggregate counts, error rates, model labels and language labels, not the audio, reference text or predictions. The file is created mode 0600 and an existing report is never overwritten.

## Interpreting the report

- **WER** = Levenshtein word edits / number of reference words.
- **CER** = Levenshtein character edits / number of reference characters after word normalisation.
- Unicode NFKC + case folding are applied; punctuation is stripped and whitespace between words is normalised. These are **not** tests of punctuation quality or phonetic transcription fidelity.
- Multiple clips are micro-averaged by word/character count, not by independently averaging clip percentages. The report separates languages so improvements in English do not hide failures in another language.
- Small sets, non-native speakers, accents, code tokens and dictated punctuation should be measured separately where they matter.

Word error rates can exceed 100% when a recogniser inserts many words. This is mathematically valid.

## Required additional benchmarks

A complete ASR decision also needs the same recorded WAV/PCM input and hardware profile for every engine, first-result and final-result latency, real-time factor, peak RSS, CPU/GPU/power usage, memory pressure, long-take recovery, language detection and repeated cold/warm trials. For local-only claims, independently instrument network connections during audio recording **and** any transcript-polishing step.

Treat different engines' privacy, licence and device support separately. A successful transcript-only report is not proof of a working Whisper integration.
