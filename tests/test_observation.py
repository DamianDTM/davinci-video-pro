"""Offline contracts for neutral observation and bounded retries. No real keys/network."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'skills/davinci-video-pro/scripts'))
import gemini_video as g
import workflow as w


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='davinci-observation-test-')
        self.root = Path(self.temp.name)
        self.project = self.root/'project'
        w.init_project(self.project, self.root/'profile')
        (self.project/w.DOCS[0]).write_text('# Guion\nSECRET_EXPECTED_LINE: a phrase the speaker may never have said.', encoding='utf-8')
        (self.project/w.DOCS[1]).write_text('# Brief\nSECRET_KNOWN_DEFECT: incorrect alleged repetition at A4.', encoding='utf-8')
        w.confirm_script(self.project, 'Use my script')
        w.confirm_brief(self.project, 'Use my brief')
        self.source = self.root/'SECRET_FILENAME_DEFECT.mp4'
        self.source.write_bytes(b'OFFLINE_ONLY')
        self.args = SimpleNamespace(project_dir=self.project, file=self.source, output=self.root/'result.json',
                                    command='verify', script=None, model='fixture', processing='static',
                                    max_output_tokens=1024, upload_to_google=True, max_attempts=1)
        self.result = {'idioma': 'es', 'transcripcion': [{'inicio_segundos': 0, 'fin_segundos': 2, 'texto': 'yo yo pienso'}],
                       'observaciones_audio': 'Repeticion audible.', 'incidencias': [], 'limitaciones': []}
        self.requests, self.uploads, self.deleted = [], [], []
        def upload(**kwargs):
            self.uploads.append(kwargs)
            return SimpleNamespace(name='files/offline', uri='offline:opaque', state=SimpleNamespace(name='ACTIVE'))
        def request(**kwargs):
            self.requests.append(kwargs)
            return SimpleNamespace(status='completed', output_text=json.dumps(self.result), usage=None, steps=[])
        self.client = SimpleNamespace(files=SimpleNamespace(upload=upload, delete=lambda **kw: self.deleted.append(kw)),
                                      interactions=SimpleNamespace(create=request))

    def tearDown(self):
        assert self.root.resolve().parent == Path(tempfile.gettempdir()).resolve()
        assert self.root.name.startswith('davinci-observation-test-')
        self.temp.cleanup()

    def run_observation(self):
        with patch.object(g, 'types', SimpleNamespace(UploadFileConfig=lambda **kw: kw)), contextlib.redirect_stdout(io.StringIO()):
            g.analyze(self.client, self.args)

    def test_neutral_request_excludes_script_brief_expected_answer_and_filename(self):
        self.run_observation()
        request = json.dumps(self.requests)
        for secret in ['SECRET_EXPECTED_LINE', 'SECRET_KNOWN_DEFECT', 'SECRET_FILENAME_DEFECT', 'FUENTE PRINCIPAL']:
            self.assertNotIn(secret, request)
            self.assertNotIn(secret, self.uploads[0]['config']['display_name'])
        report = json.loads(self.args.output.read_text())
        self.assertFalse(report['editorial_context_sent'])
        self.assertTrue(report['ai_review_required'])
        self.assertEqual(report['analysis']['transcripcion'][0]['texto'], 'yo yo pienso')
        self.assertEqual(len(self.deleted), 1)

    def test_analysis_keeps_creative_requirements(self):
        self.args.command = 'analyze'
        self.result = {'resumen': 'test', 'duracion_estimada_segundos': 2, 'idioma': 'es', 'escenas': [],
                       'transcripcion': [], 'cortes_propuestos': [], 'palabras_clave': [],
                       'recursos_visuales': [], 'observaciones_audio': '', 'limitaciones': []}
        self.run_observation()
        request = json.dumps(self.requests)
        self.assertIn('SECRET_EXPECTED_LINE', request)
        self.assertIn('SECRET_KNOWN_DEFECT', request)

    def test_neutral_cli_still_blocks_before_client_without_current_brief(self):
        (self.project/w.DOCS[1]).write_text('Changed without approval')
        args = ['gemini_video.py', '--project-dir', str(self.project), 'verify', '--file', str(self.source),
                '--output', str(self.args.output), '--upload-to-google']
        with patch.object(sys, 'argv', args), patch.object(g, 'read_key') as key, patch.object(g, 'client_for') as client, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(g.main(), 1)
        key.assert_not_called(); client.assert_not_called()

    def test_invalid_temporal_response_never_becomes_report_and_remote_is_deleted(self):
        self.result['transcripcion'][0]['fin_segundos'] = -1
        with self.assertRaises(RuntimeError): self.run_observation()
        self.assertFalse(self.args.output.exists())
        self.assertEqual(len(self.deleted), 1)
        self.assertTrue(self.args.output.with_suffix('.attempts.json').exists())

    def test_changed_brief_during_request_invalidates_observation(self):
        original = self.client.interactions.create
        def mutate(**kwargs):
            response = original(**kwargs)
            (self.project/w.DOCS[1]).write_text('Changed during the API request')
            return response
        self.client.interactions.create = mutate
        with self.assertRaises(ValueError): self.run_observation()
        self.assertFalse(self.args.output.exists())
        self.assertEqual(len(self.deleted), 1)

    def test_attempt_log_io_failure_does_not_skip_remote_cleanup(self):
        real_open = Path.open
        def opened(path, *args, **kwargs):
            if str(path).endswith('.attempts.json'): raise OSError('offline write failure')
            return real_open(path, *args, **kwargs)
        with patch.object(Path, 'open', opened), contextlib.redirect_stderr(io.StringIO()):
            self.run_observation()
        self.assertEqual(len(self.deleted), 1)

    def test_backoff_is_bounded_and_classifies_errors(self):
        class ServiceError(Exception):
            def __init__(self, status): self.status_code = status
        for status, expected in [(500, 3), (502, 3), (503, 3), (504, 3), (400, 1), (401, 1), (403, 1), (429, 1)]:
            with self.subTest(status=status):
                attempt_log, waits, calls = [], [], []
                def fail(**kw): calls.append(1); raise ServiceError(status)
                client = SimpleNamespace(interactions=SimpleNamespace(create=fail))
                with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(ServiceError):
                    g.request_observation(client, {}, 3, attempt_log, sleep=waits.append)
                self.assertEqual(len(calls), expected)
                self.assertEqual(len(attempt_log), expected)
                self.assertEqual(len(waits), expected-1)
                self.assertFalse(attempt_log[-1]['will_retry'])
        for failure in (TimeoutError('unknown completion'), RuntimeError('unknown failure')):
            with self.subTest(failure=type(failure).__name__):
                log = []
                client = SimpleNamespace(interactions=SimpleNamespace(create=lambda **kw: (_ for _ in ()).throw(failure)))
                with self.assertRaises(type(failure)): g.request_observation(client, {}, 3, log, sleep=lambda d: None)
                self.assertEqual(len(log), 1)

    def test_transient_failure_reuses_upload_and_records_success(self):
        original = self.client.interactions.create
        calls = []
        class Offline500(Exception): status_code = 500
        def first_fails(**kw):
            calls.append(1)
            if len(calls) == 1: raise Offline500()
            return original(**kw)
        self.client.interactions.create = first_fails
        self.args.max_attempts = 2
        # Override only the local wrapper's wait, not client_for/Omni retry settings.
        original_wrapper = g.request_observation
        with patch.object(g, 'request_observation', side_effect=lambda c,r,m,a: original_wrapper(c,r,m,a,sleep=lambda d: None)):
            self.run_observation()
        self.assertEqual(len(self.uploads), 1)
        self.assertEqual(len(self.deleted), 1)
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(json.loads(self.args.output.read_text())['attempts']), 2)


if __name__ == '__main__': unittest.main()
