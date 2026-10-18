"""Regression tests for no-network, transcript-only quality measurements."""
import json
import pathlib
import stat
import tempfile
import unittest
from scripts import benchmark_speech as b


class SpeechBenchmarks(unittest.TestCase):
    def test_unicode_and_punctuation(self):
        self.assertEqual(b.words('HELLO, world!'), ['hello', 'world'])
        self.assertEqual(b.words('مرحباً بالعالم'), ['مرحبا', 'بالعالم'])
        self.assertEqual(b.words('ＡＢＣ'), ['abc'])

    def test_perfect_score_and_substitution(self):
        cases = {'first': ('en-AU', 'Hello world')}
        self.assertEqual(b.evaluate(cases, {'first': 'HELLO, world!'})['overall']['wer'], 0)
        self.assertEqual(b.evaluate(cases, {'first': 'Hello there'})['overall']['wer'], 0.5)

    def test_insertions_deletions_and_empty_hypothesis(self):
        self.assertEqual(b.edit_distance(['a', 'b'], ['a']), 1)
        self.assertEqual(b.edit_distance(['a'], ['a', 'b']), 1)
        self.assertEqual(b.evaluate({'a': ('en', 'one two')}, {'a': ''})['overall']['wer'], 1)

    def test_micro_aggregation_and_language_groups(self):
        cases = {'a': ('en', 'one two three four'), 'b': ('en', 'five'), 'c': ('ar', 'مرحبا')}
        predictions = {'a': 'one two three four', 'b': 'no', 'c': 'مرحبا'}
        metrics = b.evaluate(cases, predictions)
        self.assertEqual(metrics['overall']['word_errors'], 1)
        self.assertAlmostEqual(metrics['overall']['wer'], 1/6, places=5)
        self.assertEqual(metrics['by_language']['en']['cases'], 2)
        self.assertEqual(metrics['by_language']['ar']['wer'], 0)

    def test_dataset_requires_unique_nonempty_references(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)/'d.json'
            p.write_text(json.dumps({'cases': [{'id':'one', 'language':'en', 'reference':'hello'},
                                                {'id':'one', 'language':'en', 'reference':'hello'}]}))
            with self.assertRaisesRegex(ValueError, 'unique'): b.load_cases(p)
            p.write_text(json.dumps({'cases': [{'id':'empty', 'language':'en', 'reference': '...'}]}))
            with self.assertRaisesRegex(ValueError, 'spoken'): b.load_cases(p)

    def test_prediction_mismatch_and_duplicates_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'p.json'
            p.write_text(json.dumps({'predictions':[{'id':'a','text':'hi'},{'id':'a','text':'hi'}]}))
            with self.assertRaisesRegex(ValueError,'unique'): b.load_predictions(p, {'a'})
            p.write_text(json.dumps({'predictions':[{'id':'a','text':'hi'}]}))
            with self.assertRaisesRegex(ValueError,'exactly'): b.load_predictions(p, {'b'})

    def test_report_has_no_transcript_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            (root/'dataset.json').write_text(json.dumps({'cases':[{'id':'test','language':'en','reference':'secret alpha'}]}))
            (root/'pred.json').write_text(json.dumps({'predictions':[{'id':'test','text':'secret alpha'}]}))
            args=['--dataset', str(root/'dataset.json'), '--prediction', f"parakeet={root/'pred.json'}", '--out', str(root/'report.json')]
            self.assertEqual(b.main(args),0)
            report=(root/'report.json').read_text()
            self.assertNotIn('secret alpha',report)
            self.assertIn('"wer": 0.0',report)
            self.assertEqual(stat.S_IMODE((root/'report.json').stat().st_mode),0o600)
            self.assertEqual(b.main(args),1)


if __name__=='__main__':
    unittest.main()
