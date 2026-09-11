"""Offline functional checks. Never reads real credentials or calls a provider."""
import ast
import base64
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/davinci-video-pro/scripts'
sys.path.insert(0, str(SCRIPTS))
import workflow as w
import omni_video as omni
import openai_image as images
import configure_claude_mcp as mcp


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load('portable_installer', ROOT / 'install.py')
g = load('portable_gemini_v2', SCRIPTS / 'gemini_video.py')


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='davinci portable tests ')
        self.root = Path(self.tmp.name)
        self.project = self.root / 'video one'
        self.profile = self.root / 'shared profile'
        w.init_project(self.project, self.profile)

    def tearDown(self):
        # Explicit verified temporary tree created only by this test.
        assert self.root.resolve().parent == Path(tempfile.gettempdir()).resolve()
        assert self.root.name.startswith('davinci portable tests ')
        self.tmp.cleanup()

    def approve(self):
        (self.project / w.DOCS[0]).write_text('# Guion\nExplicar como regar una planta en tres pasos. Mostrar agua y tierra. Cerrar invitando a comentar.', encoding='utf-8')
        w.confirm_script(self.project, 'Usa este guion para editar el video.')

    def candidates(self):
        creative = self.root / 'creative.md'; technical = self.root / 'technical.md'
        creative.write_text('# Guion revisado\nExplicar como regar una planta con un primer plano de la tierra. Cerrar con invitacion a comentar.', encoding='utf-8')
        technical.write_text('# Brief revisado\nSubtitulos blancos con palabras clave azules, mantener pausas expresivas.', encoding='utf-8')
        return creative, technical

    def test_gate_requires_real_current_script(self):
        with self.assertRaises(ValueError): w.require_script(self.project)
        with self.assertRaises(ValueError): w.confirm_script(self.project, 'Si')
        self.approve(); self.assertTrue(w.require_script(self.project).is_file())
        (self.project / w.DOCS[0]).write_text('Cambio posterior que no ha sido confirmado por el usuario.', encoding='utf-8')
        with self.assertRaises(ValueError): w.require_script(self.project)

    def test_gemini_api_commands_stop_before_client_without_script(self):
        for command in ['models', 'check']:
            with patch.object(g, 'client_for') as client, patch.object(g, 'read_key') as key, patch.object(sys, 'argv', ['gemini_video.py', '--project-dir', str(self.project), command]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(g.main(), 1)
                client.assert_not_called(); key.assert_not_called()

    def test_sdk_does_not_retry_a_rate_limited_generation(self):
        import httpx
        sent = []
        def reject(client, request, **kwargs):
            sent.append(request.url.path)
            return httpx.Response(429, json={'error': {'code': 429, 'message': 'Offline quota fixture'}}, request=request)
        with patch.object(httpx.Client, 'send', reject):
            with g.client_for('OFFLINE_NOT_REAL') as client:
                with self.assertRaises(Exception) as raised:
                    client.interactions.create(model='offline-fixture', input='offline fixture', store=False)
        self.assertEqual(len(sent), 1, (sent, str(raised.exception)))

    def test_other_providers_block_before_reading_keys(self):
        with patch.object(images, 'read_key') as key:
            with self.assertRaises(ValueError): images.generate(SimpleNamespace(project_dir=self.project))
            key.assert_not_called()
        with self.assertRaises(ValueError): omni.generate(SimpleNamespace(project_dir=self.project))
        with self.assertRaises(ValueError): mcp.configure(self.project, self.root / 'absent.json')

    def test_revision_confirmation_and_profile_inheritance(self):
        self.approve(); creative, technical = self.candidates()
        with (self.project / 'ESTADO.md').open('a', encoding='utf-8') as log:
            log.write('\nDetalle de configuracion que debe conservarse.\n')
        before = [(self.project / name).read_bytes() for name in w.DOCS]
        pc = self.root / 'profile-creative.md'; pt = self.root / 'profile-tech.md'
        pc.write_text('# Plantilla\nPENDIENTE_DE_GUION\nPreferencia general: tono calmado, imagenes azules.', encoding='utf-8')
        pt.write_text('# Tecnico\nPalabras clave azules y pausas naturales.', encoding='utf-8')
        w.stage_revision(self.project, creative, technical, 'Cambiar encuadre del video; guardar enfasis azul para proximos videos.', pc, pt)
        self.assertEqual(before, [(self.project / name).read_bytes() for name in w.DOCS])
        with self.assertRaises(ValueError): w.apply_revision(self.project, '')
        result = w.apply_revision(self.project, 'Si, es correcto; guardalo para los siguientes videos.')
        self.assertTrue(result['profile_updated'])
        self.assertEqual((self.project / w.DOCS[0]).read_bytes(), creative.read_bytes())
        self.assertEqual((self.project / w.DOCS[1]).read_bytes(), technical.read_bytes())
        self.assertTrue(w.require_script(self.project))
        self.assertIn('Detalle de configuracion', (self.project / 'ESTADO.md').read_text(encoding='utf-8'))
        new = self.root / 'video two'; w.init_project(new, self.profile)
        self.assertIn('azules', (new / w.DOCS[1]).read_text())
        with self.assertRaises(ValueError): w.require_script(new)
        self.assertIsNone(w.read_state(new)['omni_plan'])
        self.assertTrue((new / 'AGENTS.md').exists() and (new / 'CLAUDE.md').exists())

    def test_stale_revision_does_not_overwrite_new_changes(self):
        self.approve(); c, t = self.candidates()
        w.stage_revision(self.project, c, t, 'Resumen original')
        (self.project / w.DOCS[1]).write_text('Cambio externo a conservar.', encoding='utf-8')
        with self.assertRaises(ValueError): w.apply_revision(self.project, 'Si')
        self.assertEqual((self.project / w.DOCS[1]).read_text(), 'Cambio externo a conservar.')

    def test_document_transaction_rolls_back(self):
        self.approve(); c, t = self.candidates()
        w.stage_revision(self.project, c, t, 'Cambiar ambos documentos')
        before = [(self.project / name).read_bytes() for name in w.DOCS]
        real = w.atomic; raised = False
        def fail_once(path, content):
            nonlocal raised
            if Path(path) == self.project / w.DOCS[1] and not raised:
                raised = True; raise OSError('simulated disk error')
            return real(path, content)
        with patch.object(w, 'atomic', side_effect=fail_once):
            with self.assertRaises(OSError): w.apply_revision(self.project, 'Confirmo')
        self.assertEqual(before, [(self.project / name).read_bytes() for name in w.DOCS])
        self.assertEqual(w.read_state(self.project)['revision'], 0)
        self.assertEqual(w.apply_revision(self.project, 'Confirmo')['revision'], 1)

    def test_installer_preserves_existing_changes_and_updates_with_backup(self):
        dest = self.root / 'skills'
        self.assertEqual(installer.install(dest)['status'], 'installed')
        self.assertEqual(installer.install(dest)['status'], 'already_installed')
        target = dest / 'davinci-video-pro/SKILL.md'; target.write_text('Personal customization', encoding='utf-8')
        with self.assertRaises(ValueError): installer.install(dest)
        result = installer.install(dest, update=True)
        self.assertEqual((Path(result['backup']) / 'SKILL.md').read_text(), 'Personal customization')
        self.assertTrue((self.profile / 'templates' / w.DOCS[0]).exists())

    def test_codex_and_claude_project_install_locations(self):
        result = subprocess.run([sys.executable, str(ROOT / 'install.py'), '--client', 'both', '--scope', 'project', '--project-dir', str(self.root / 'client project')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for folder in ['.agents', '.claude']:
            self.assertTrue((self.root / 'client project' / folder / 'skills/davinci-video-pro/SKILL.md').is_file())

    def test_mcp_merge_preserves_other_servers(self):
        self.approve(); path = self.project / '.mcp.json'
        path.write_text(json.dumps({'otherSetting': True, 'mcpServers': {'other': {'command': 'preserve'}}}))
        entry = self.root / 'entry.json'
        entry.write_text(json.dumps({'mcpServers': {'davinci-resolve': {'command': sys.executable, 'args': ['server.py']}}}))
        mcp.configure(self.project, entry)
        data = json.loads(path.read_text())
        self.assertTrue(data['otherSetting']); self.assertEqual(data['mcpServers']['other']['command'], 'preserve')
        self.assertEqual(mcp.configure(self.project, entry)['status'], 'already_configured')

    def test_omni_budget_and_duplicate_attempts(self):
        self.approve(); source = self.root / 'synthetic.mp4'; source.write_bytes(b'fixture')
        with self.assertRaises(ValueError): omni.reserve(self.project, 'scene', source, 'prompt', 0.5)
        w.set_omni_plan(self.project, 2, 1.0, 'Autorizo dos intentos con este presupuesto')
        omni.reserve(self.project, 'scene', source, 'prompt one', 0.6)
        with self.assertRaises(ValueError): omni.reserve(self.project, 'scene', source, 'prompt two', 0.2)
        with self.assertRaises(ValueError): omni.reserve(self.project, 'scene2', source, 'prompt one', 0.2)
        with self.assertRaises(ValueError): omni.reserve(self.project, 'scene2', source, 'prompt two', 0.6)
        self.assertEqual(len(list((w.metadata(self.project) / 'omni-attempts').glob('*.json'))), 1)

    def test_gemini_analysis_uses_script_and_cleans_remote_on_failure(self):
        self.approve(); source = self.root / 'fixture.mp4'; source.write_bytes(b'never uploaded')
        calls = []
        class Files:
            def upload(self, **kw): calls.append('upload'); return SimpleNamespace(name='files/fixture', uri='fixture', state=SimpleNamespace(name='ACTIVE'))
            def delete(self, **kw): calls.append('delete')
        valid = {key: [] for key in ['escenas', 'transcripcion', 'cortes_propuestos', 'palabras_clave', 'recursos_visuales', 'limitaciones']}
        valid.update(resumen='Fixture', duracion_estimada_segundos=4, idioma='es', observaciones_audio='Fixture')
        def request(**kw):
            self.assertIn('FUENTE PRINCIPAL', kw['input'][1]['text'])
            self.assertIn('regar una planta', kw['input'][1]['text'])
            return SimpleNamespace(status='completed', output_text=json.dumps(valid), steps=[], usage=None)
        client = SimpleNamespace(files=Files(), interactions=SimpleNamespace(create=request))
        args = SimpleNamespace(project_dir=self.project, file=source, output=self.root / 'analysis.json', script=None, model='fixture-model', processing='static', max_output_tokens=512, upload_to_google=True)
        with contextlib.redirect_stdout(io.StringIO()): g.analyze(client, args)
        self.assertEqual(calls, ['upload', 'delete'])
        report = json.loads(args.output.read_text()); self.assertEqual(report['script_sha256'], w.digest(self.project / w.DOCS[0]))
        args.output = self.root / 'failed.json'
        client.interactions.create = lambda **kw: SimpleNamespace(status='completed', output_text='{}', steps=[], usage=None)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(RuntimeError): g.analyze(client, args)
        self.assertEqual(calls, ['upload', 'delete', 'upload', 'delete'])

    def test_image_request_is_single_and_never_echoes_credentials(self):
        self.approve(); prompt = self.root / 'prompt.txt'; prompt.write_text('A unique clear illustration of watering a plant for this scene.')
        args = SimpleNamespace(project_dir=self.project, prompt_file=prompt, output=self.root / 'image.png', model='fixture-image-model', size='1024x1536', quality='medium', confirmation='Autorizo esta imagen y su coste', estimated_usd=0.1, max_usd=0.2)
        fake = io.BytesIO(json.dumps({'data': [{'b64_json': base64.b64encode(b'\x89PNG\r\n\x1a\nfixture').decode()}]}).encode())
        with patch.object(images, 'read_key', return_value='OFFLINE_NOT_A_REAL_KEY'), patch.object(images.urllib.request, 'urlopen', return_value=fake) as call:
            self.assertEqual(images.generate(args)['status'], 'completed_needs_review')
            self.assertEqual(call.call_count, 1)
            with self.assertRaises(ValueError): images.generate(args)
            self.assertEqual(call.call_count, 1)
        self.assertNotIn('OFFLINE_NOT_A_REAL_KEY', args.output.with_suffix('.request.json').read_text())

    def test_omni_success_and_failure_cleanup_without_real_service(self):
        self.approve(); w.set_omni_plan(self.project, 2, 2.0, 'Autorizacion ficticia del test local')
        source = self.root / 'fixture.mp4'; source.write_bytes(b'local fixture never sent')
        prompt = self.root / 'angle.txt'; prompt.write_text('A four second view of the same plant from a different camera angle.')
        events = []
        class Files:
            def upload(self, **kw): events.append('upload'); return SimpleNamespace(name='files/mock', uri='mock', state=SimpleNamespace(name='ACTIVE'))
            def delete(self, **kw): events.append('delete')
        class Client:
            def __init__(self):
                self.files = Files(); self.interactions = SimpleNamespace(create=self.request); self.fail = False
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def request(self, **kw):
                events.append('generate')
                self_check = kw['response_format']
                assert self_check['duration'] == '4s' and self_check['resolution'] == '720p'
                if self.fail: raise TimeoutError('Uncertain fake response')
                return SimpleNamespace(status='completed', id=None, usage=None, output_video=SimpleNamespace(data=base64.b64encode(b'\x00\x00\x00\x18ftypisom-fixture').decode()))
        fake_client = Client()
        fake_av = SimpleNamespace(time_base=1000000, open=lambda *a: contextlib.nullcontext(SimpleNamespace(streams=SimpleNamespace(video=[True]), duration=4000000)))
        args = SimpleNamespace(project_dir=self.project, file=source, prompt_file=prompt, scene='scene1', estimated_usd=0.5, upload_to_google=True, aspect_ratio='9:16')
        with patch.dict(sys.modules, {'gemini_video': g, 'av': fake_av}), patch.object(g, 'read_key', return_value='OFFLINE_KEY'), patch.object(g, 'client_for', return_value=fake_client):
            self.assertEqual(omni.generate(args)['status'], 'completed_needs_review')
            self.assertEqual(events, ['upload', 'generate', 'delete'])
            args.scene = 'scene2'; prompt.write_text('A different four second camera angle showing the same plant and original timing.')
            fake_client.fail = True
            with self.assertRaises(RuntimeError): omni.generate(args)
        self.assertEqual(events, ['upload', 'generate', 'delete', 'upload', 'generate', 'delete'])
        failed = json.loads((w.metadata(self.project) / 'omni-attempts/scene2.json').read_text())
        self.assertTrue(failed['remote_input_deleted'])
        self.assertEqual(failed['status'], 'failed_or_uncertain')


if __name__ == '__main__':
    unittest.main(verbosity=2)
