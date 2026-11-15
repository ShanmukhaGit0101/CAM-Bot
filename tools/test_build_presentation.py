"""Presentation provenance: protect sealed inputs and the measured-time boundary."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tools import build_presentation as presentation


class PresentationEvidenceTests(unittest.TestCase):
    def test_replay_is_actual_first_trial_and_metric_excludes_initial_home(self):
        stats,replay,_,_=presentation.collect()
        raw=[json.loads(line) for line in (presentation.CAPTURE/'raw/trials.events.jsonl').read_text().splitlines()]
        source=[r for r in raw if r['trial_id']==replay['trial_id']]
        for event in replay['events']:
            self.assertTrue(any(row['monotonic_elapsed_s']==event['t'] and
                                row['action']==event['action'] and row['result']==event['result']
                                for row in source))
        start=next(r['t'] for r in replay['events'] if r['action']=='S1_APPROACH' and r['result']=='STEP_STARTED')
        end=next(r['t'] for r in replay['events'] if r['action']=='HOME_END' and r['result']=='STEP_COMPLETED')
        self.assertAlmostEqual(end-start,19.585576359)
        self.assertAlmostEqual(stats['mean_s'],19.579116666)
        self.assertGreater(replay['events'][-1]['t'],end-start)
        self.assertEqual(replay['events'][-1]['workpiece'],'FINISHED_AT_S5')

    def test_modified_capture_is_rejected_before_deck_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            capture=Path(directory)
            (capture/'raw_analysis').mkdir();(capture/'raw').mkdir()
            shutil.copy2(presentation.CAPTURE/'raw_analysis/metrics.json',capture/'raw_analysis/metrics.json')
            for name in ('trials.csv','trials.events.jsonl'):
                shutil.copy2(presentation.CAPTURE/'raw'/name,capture/'raw'/name)
            with (capture/'raw/trials.csv').open('a') as stream:stream.write('changed\n')
            with patch.object(presentation,'CAPTURE',capture):
                with self.assertRaisesRegex(ValueError,'raw input differs'):
                    presentation.collect()

    def test_existing_output_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileExistsError):presentation.main(Path(directory))


if __name__=='__main__':unittest.main()
