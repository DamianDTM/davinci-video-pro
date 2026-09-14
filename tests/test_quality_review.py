"""Real synthetic media fixtures plus review-gate invariants, entirely local."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'skills/davinci-video-pro/scripts'))
import quality_review as q
import workflow as w

MEDIA_AVAILABLE = all(importlib.util.find_spec(n) for n in ('av', 'numpy', 'PIL', 'imageio_ffmpeg'))


class PlanTests(unittest.TestCase):
    def test_real_destination_gap_and_intentional_overlap(self):
        self.assertEqual(q.gaps([{'start': 0, 'end': 30}, {'start': 31, 'end': 90}], 90), [[30, 31]])
        self.assertEqual(q.gaps([{'start': 0, 'end': 35}, {'start': 30, 'end': 90}], 90), [])
        self.assertEqual(q.gaps([], 90), [[0, 90]])

    def test_plan_rejects_invalid_ranges_and_fractional_cut_indices(self):
        base = {'version': 1, 'expected': {'frames': 90, 'width': 160, 'height': 90, 'fps': '30/1', 'audio': True}, 'cuts': [30]}
        for cuts in [[30, 30], [90], [0], [3.5], [True]]:
            candidate = copy.deepcopy(base); candidate['cuts'] = cuts
            with self.subTest(cuts=cuts), self.assertRaises(ValueError): q.validate_plan(candidate)
        for fps in ['0/1', 'nan', 'inf', True]:
            candidate = copy.deepcopy(base); candidate['expected']['fps'] = fps
            with self.subTest(fps=fps), self.assertRaises(ValueError): q.validate_plan(candidate)


@unittest.skipUnless(MEDIA_AVAILABLE, 'Media QA requires requirements-media.txt; this skip is not a passing media test.')
class MediaTests(unittest.TestCase):
    def setUp(self):
        import imageio_ffmpeg
        self.temp = tempfile.TemporaryDirectory(prefix='davinci-media-qa-test-')
        self.root = Path(self.temp.name)
        self.project = self.root/'project'
        w.init_project(self.project, self.root/'profile')
        w.use_default_script(self.project, 'Usa el guion por defecto')
        w.confirm_brief(self.project, 'Usa el brief por defecto')
        self.ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        self.source = self.root/'fixture.mp4'
        self.srt = self.root/'fixture.srt'
        self.srt.write_text('1\n00:00:00,100 --> 00:00:01,000\nTexto de prueba\n\n2\n00:00:01,100 --> 00:00:02,900\nSolo prueba sintetica\n', encoding='utf-8')
        self.plan = {'version': 1, 'expected': {'frames': 90, 'fps': '30/1', 'width': 160, 'height': 90, 'audio': True, 'speech': False},
                     'cuts': [30, 60], 'primary_video_spans': [{'start': 0, 'end': 30}, {'start': 30, 'end': 60}, {'start': 60, 'end': 90}]}
        self.plan_file = self.root/'plan.json'
        self.folder = self.root/'qa'

    def tearDown(self):
        assert self.root.resolve().parent == Path(tempfile.gettempdir()).resolve()
        assert self.root.name.startswith('davinci-media-qa-test-')
        self.temp.cleanup()

    def fixture(self, black=False, audio=True, rate='30'):
        args = ['-loglevel', 'error', '-n', '-f', 'lavfi', '-i', f'testsrc2=size=160x90:rate={rate}:duration=3.01']
        if audio: args += ['-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000:duration=3.01']
        if black: args += ['-vf', "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='eq(n,30)'"]
        args += ['-frames:v', '90', '-c:v', 'libx264', '-pix_fmt', 'yuv420p']
        if audio: args += ['-c:a', 'aac', '-shortest']
        q.ffmpeg_run(self.ffmpeg, [*args, str(self.source)])

    def scan(self, neutral_report=None):
        self.plan_file.write_text(json.dumps(self.plan), encoding='utf-8')
        return q.scan(self.project, self.source, self.plan_file, self.folder, self.srt, neutral_report=neutral_report)

    def neutral_fixture(self, mode='verify'):
        path = self.root/'neutral.json'
        q.create_json(path, {'mode': mode, 'editorial_context_sent': mode != 'verify',
                            'source_path': str(self.source), 'source_sha256': w.digest(self.source),
                            'analysis': {'idioma': 'none', 'transcripcion': [], 'incidencias': [],
                                         'observaciones_audio': 'Synthetic tone only.', 'limitaciones': ['Offline fixture, no API called.']}})
        return path

    def simulated_review(self, report):
        """Contract fixture only, not an actual AI review or certification of media quality."""
        path = self.folder/'AI-REVIEW.json'
        value = q.load(path)
        value.update(agent='UNIT_TEST_ONLY', model='SIMULATED_REVIEW', viewed_entire_video=True, listened_entire_audio=True)
        warnings = {f['id'] for f in report['findings'] if f['severity'] == 'warning'}
        for record in value['items']:
            record.update(verdict='intentional' if record['id'] in warnings else 'pass',
                          observation='Synthetic contract fixture; not a human or AI perceptual approval.', evidence=[str(self.source)])
        path.write_text(json.dumps(value), encoding='utf-8')
        return path

    def test_valid_media_creates_evidence_but_never_autoapproves(self):
        self.fixture(); report = self.scan()
        self.assertEqual(report['measured']['frames'], 90)
        self.assertEqual(report['status'], 'needs_ai_review')
        self.assertEqual(report['findings'], [])
        self.assertIsNotNone(report['measured']['audio']['integrated_lufs'])
        self.assertTrue((self.folder/'cut-30.mp4').is_file())
        self.assertTrue((self.folder/'frame-00000029.png').is_file())
        review_file = self.folder/'AI-REVIEW.json'
        with self.assertRaises(ValueError): q.gate(self.project, self.folder/'report.json', review_file, self.source)
        self.simulated_review(report)
        self.assertEqual(q.gate(self.project, self.folder/'report.json', review_file, self.source)['status'], 'agent_review_recorded')

    def test_one_black_frame_and_one_frame_timeline_gap_are_found(self):
        self.fixture(black=True)
        self.plan['primary_video_spans'][1]['start'] = 31
        report = self.scan()
        findings = {f['kind']: f for f in report['findings']}
        self.assertEqual(findings['black_frames']['detail']['ranges'], [[30, 31]])
        self.assertEqual(findings['timeline_gaps']['detail']['ranges'], [[30, 31]])

    def test_wrong_frame_count_missing_audio_and_missing_readback_block_gate(self):
        self.fixture(audio=False)
        self.plan['expected']['frames'] = 91
        self.plan.pop('primary_video_spans')
        report = self.scan()
        self.assertEqual(report['status'], 'blocked')
        self.assertEqual({f['kind'] for f in report['findings']}, {'frame_count', 'audio_streams', 'timeline_not_measured'})
        review = self.simulated_review(report)
        with self.assertRaises(ValueError): q.gate(self.project, self.folder/'report.json', review, self.source)

    def test_media_evidence_or_brief_change_invalidates_review(self):
        self.fixture(); report = self.scan(); review = self.simulated_review(report)
        for path in [self.source, self.srt, Path(report['artifacts'][0]['path']), self.project/w.DOCS[1]]:
            before = path.read_bytes()
            path.write_bytes(before+b'changed')
            with self.subTest(path=path.name), self.assertRaises(ValueError):
                q.gate(self.project, self.folder/'report.json', review, self.source)
            path.write_bytes(before)
        self.assertEqual(q.gate(self.project, self.folder/'report.json', review, self.source)['status'], 'agent_review_recorded')

    def test_unreviewed_cut_or_wrong_report_or_unbound_evidence_is_rejected(self):
        self.fixture(); report = self.scan(); review_path = self.simulated_review(report)
        baseline = q.load(review_path)
        wrong = []
        value = copy.deepcopy(baseline); value['items'].pop(); wrong.append(value)
        value = copy.deepcopy(baseline); value['report_sha256'] = 'old'; wrong.append(value)
        value = copy.deepcopy(baseline); value['viewed_entire_video'] = False; wrong.append(value)
        value = copy.deepcopy(baseline); value['items'][0]['verdict'] = 'pending'; wrong.append(value)
        value = copy.deepcopy(baseline); value['items'][0]['evidence'] = ['invented.mp4']; wrong.append(value)
        for value in wrong:
            review_path.write_text(json.dumps(value), encoding='utf-8')
            with self.assertRaises(ValueError): q.gate(self.project, self.folder/'report.json', review_path, self.source)

    def test_srt_outside_media_is_a_blocker(self):
        self.fixture()
        self.srt.write_text('1\n00:00:00,100 --> 00:00:04,000\nToo long\n', encoding='utf-8')
        report = self.scan()
        self.assertTrue(any(f['kind'] == 'subtitles_structure' and f['severity'] == 'blocker' for f in report['findings']))

    def test_fractional_fps_uses_real_frame_timestamps(self):
        self.fixture(rate='30000/1001')
        self.plan['expected']['fps'] = '30000/1001'
        report = self.scan()
        self.assertEqual(report['measured']['fps'], '30000/1001')
        self.assertFalse(any(f['kind'] == 'timestamps' for f in report['findings']))

    def test_corrupt_media_cannot_produce_a_ready_report(self):
        self.source.write_bytes(b'not a media file')
        with self.assertRaises(Exception): self.scan()
        self.assertFalse((self.folder/'report.json').exists())
        self.assertTrue((self.folder/'FAILED.json').exists())

    def test_speech_needs_neutral_gemini_evidence_then_agent_review(self):
        self.fixture(); self.plan['expected']['speech'] = True
        report = self.scan()
        self.assertTrue(any(f['kind'] == 'neutral_review_missing' for f in report['findings']))
        self.folder = self.root/'qa-neutral'
        report = self.scan(self.neutral_fixture())
        self.assertEqual(report['status'], 'needs_ai_review')
        with self.assertRaises(ValueError):
            q.gate(self.project, self.folder/'report.json', self.folder/'AI-REVIEW.json', self.source)
        self.assertIn('gemini-and-agent', {i['id'] for i in report['review_items']})

    def test_creative_analysis_cannot_pass_for_neutral_verification(self):
        self.fixture(); self.plan['expected']['speech'] = True
        report = self.scan(self.neutral_fixture(mode='analyze'))
        self.assertTrue(any(f['kind'] == 'neutral_review_invalid' for f in report['findings']))

    def test_visual_remux_reuses_neutral_but_changed_audio_does_not(self):
        self.fixture(); self.plan['expected']['speech'] = True
        neutral = self.neutral_fixture()
        original = self.source
        self.source = self.root/'visual-only.mp4'
        q.ffmpeg_run(self.ffmpeg, ['-loglevel', 'error', '-n', '-i', str(original), '-c', 'copy', '-metadata', 'comment=visual revision', str(self.source)])
        self.assertNotEqual(w.digest(original), w.digest(self.source))
        self.assertEqual(self.scan(neutral)['status'], 'needs_ai_review')
        self.source = self.root/'changed-voice.mp4'
        self.folder = self.root/'qa-changed-audio'
        q.ffmpeg_run(self.ffmpeg, ['-loglevel', 'error', '-n', '-i', str(original), '-c:v', 'copy', '-af', 'volume=0.5', '-c:a', 'aac', str(self.source)])
        report = self.scan(neutral)
        self.assertTrue(any(f['kind'] == 'neutral_review_invalid' for f in report['findings']))

    def test_identical_pcm_with_shifted_audio_timing_is_not_a_visual_only_revision(self):
        self.fixture()
        shifted = self.root/'shifted.mp4'
        q.ffmpeg_run(self.ffmpeg, ['-loglevel', 'error', '-n', '-i', str(self.source), '-itsoffset', '0.25',
                                  '-i', str(self.source), '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', str(shifted)])
        before = q.audio_fingerprint(self.ffmpeg, self.source)
        after = q.audio_fingerprint(self.ffmpeg, shifted)
        self.assertNotEqual(before, after)


if __name__ == '__main__': unittest.main()
