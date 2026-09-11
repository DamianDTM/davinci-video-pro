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
import diagnose
import intake


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
        w.confirm_brief(self.project, 'Usa el brief tecnico por defecto', source='default')

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

    def test_gemini_connection_commands_allow_setup_without_documents(self):
        client = SimpleNamespace(models=SimpleNamespace(list=lambda: [SimpleNamespace(name='models/offline-model')]),
                                 interactions=SimpleNamespace(create=lambda **kw: SimpleNamespace(output_text='OK', usage=None)))
        for command in ['models', 'check']:
            argv = ['gemini_video.py', '--project-dir', str(self.project), command]
            if command == 'check': argv += ['--model', 'offline-model']
            with patch.object(g, 'client_for', return_value=contextlib.nullcontext(client)) as connect, patch.object(g, 'read_key', return_value='OFFLINE_KEY'), patch.object(sys, 'argv', argv), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(g.main(), 0)
                connect.assert_called_once()
        with self.assertRaises(ValueError): w.require_production(self.project)

    def test_analysis_stops_before_client_without_both_documents(self):
        argv = ['gemini_video.py', '--project-dir', str(self.project), 'analyze', '--file', 'missing.mp4', '--output', 'unused.json']
        for has_script in (False, True):
            if has_script: w.use_default_script(self.project, 'No tengo guion')
            with patch.object(g, 'client_for') as client, patch.object(g, 'read_key') as key, patch.object(sys, 'argv', argv), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(g.main(), 1)
                client.assert_not_called(); key.assert_not_called()

    def test_sdk_does_not_retry_a_rate_limited_generation(self):
        problem = g.sdk_problem()
        if problem:
            self.skipTest(problem)
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
        self.assertEqual((self.project / w.DOCS[0]).read_text(encoding='utf-8'), creative.read_text(encoding='utf-8'))
        self.assertEqual((self.project / w.DOCS[1]).read_text(encoding='utf-8'), technical.read_text(encoding='utf-8'))
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
        path = self.project / '.mcp.json'
        path.write_text(json.dumps({'otherSetting': True, 'mcpServers': {'other': {'command': 'preserve'}}}))
        entry = self.root / 'entry.json'
        entry.write_text(json.dumps({'mcpServers': {'davinci-resolve': {'command': sys.executable, 'args': ['server.py']}}}))
        mcp.configure(self.project, entry)
        data = json.loads(path.read_text())
        self.assertTrue(data['otherSetting']); self.assertEqual(data['mcpServers']['other']['command'], 'preserve')
        self.assertEqual(mcp.configure(self.project, entry)['status'], 'already_configured')
        with self.assertRaises(ValueError): w.require_script(self.project)

    def test_omni_one_at_a_time_without_budget_and_explicit_retry(self):
        self.approve(); source = self.root / 'synthetic.mp4'; source.write_bytes(b'fixture')
        with self.assertRaises(ValueError): omni.reserve(self.project, 'scene', source, 'prompt')
        w.authorize_omni_next(self.project, 'Si, quiero escenas Omni')
        path, record = omni.reserve(self.project, 'scene', source, 'prompt one')
        with self.assertRaises(ValueError): omni.reserve(self.project, 'scene2', source, 'prompt two')
        with self.assertRaises(ValueError): w.authorize_omni_next(self.project, 'Otra', 'scene')
        record['status'] = 'completed'; w.write_json(path, record)
        with self.assertRaises(ValueError): w.authorize_omni_next(self.project, 'Otra')
        w.authorize_omni_next(self.project, 'He visto el video y coste, genera otro', 'scene')
        with self.assertRaises(ValueError): omni.reserve(self.project, 'scene2', source, 'prompt one')
        w.authorize_omni_next(self.project, 'Reintenta esa toma', 'scene', retry_of='scene')
        with self.assertRaises(ValueError): omni.reserve(self.project, 'scene', source, 'prompt one')
        omni.reserve(self.project, 'scene2', source, 'prompt one')
        with self.assertRaises(ValueError): omni.reserve(self.project, 'scene3', source, 'prompt three')
        self.assertEqual(len(w.omni_attempts(self.project)), 2)

    def test_old_omni_budget_does_not_authorize_a_batch(self):
        self.approve()
        state = w.read_state(self.project)
        state['omni_plan'] = {'max_attempts': 100, 'budget_usd': 100, 'confirmation': 'Old batch'}
        w.write_json(w.metadata(self.project) / 'project.json', state)
        with self.assertRaises(ValueError): omni.require_next_attempt(self.project)

    def test_omni_next_cli_requires_no_budget(self):
        self.approve()
        result = subprocess.run([sys.executable, str(w.__file__), '--project-dir', str(self.project),
                                 'omni-next', '--confirmation', 'Si, usar Omni'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'one_omni_attempt_authorized')

    def test_omni_costs_known_usage_and_unknowns(self):
        record = {'scene': 'test', 'model': 'gemini-omni-1.1-flash', 'resolution': '720p',
                  'status': 'completed', 'output_seconds': 4}
        cost = omni.estimate_cost(record)
        self.assertAlmostEqual(cost['estimated_subtotal_usd'], .40544)
        self.assertIsNone(cost['estimated_total_usd']); self.assertIsNone(cost['billed_usd'])
        usage = {'total_input_tokens': 1000, 'total_output_tokens': 23268,
                 'output_tokens_by_modality': [{'modality': 'video', 'tokens': 23168}, {'modality': 'text', 'tokens': 100}],
                 'total_thought_tokens': 0, 'total_cached_tokens': 0, 'total_tool_use_tokens': 0}
        record['usage'] = usage
        cost = omni.estimate_cost(record)
        self.assertAlmostEqual(cost['estimated_total_usd'], .40784)
        self.assertEqual(cost['status'], 'usage_estimate'); self.assertIsNone(cost['billed_usd'])
        usage['total_thought_tokens'] = 250
        self.assertIsNone(omni.estimate_cost(record)['estimated_total_usd'])
        record['model'] = 'unknown-model'
        self.assertIsNone(omni.estimate_cost(record)['estimated_subtotal_usd'])

    def test_omni_uncertain_cost_is_not_reported_as_free(self):
        self.approve()
        record = {'scene': 'uncertain', 'created_at': w.now(), 'model': 'gemini-omni-1.1-flash',
                  'resolution': '720p', 'status': 'failed_or_uncertain', 'usage': None}
        cost = omni.estimate_cost(record)
        self.assertIsNone(cost['estimated_subtotal_usd']); self.assertIsNone(cost['billed_usd'])
        w.write_json(w.metadata(self.project) / 'omni-attempts/uncertain.json', record)
        report = Path(omni.write_cost_report(self.project)).read_text(encoding='utf-8')
        self.assertIn('desconocido / pendiente', report)
        self.assertIn('intentos sin coste conocido: 1', report)
        with self.assertRaises(ValueError): w.authorize_omni_next(self.project, 'Sigue')
        w.authorize_omni_next(self.project, 'He revisado el fallo y coste desconocido, prueba otra toma', 'uncertain')
        self.assertTrue(omni.require_next_attempt(self.project))

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
        fake_types = SimpleNamespace(UploadFileConfig=lambda **kw: kw)
        with patch.object(g, 'types', fake_types), contextlib.redirect_stdout(io.StringIO()): g.analyze(client, args)
        self.assertEqual(calls, ['upload', 'delete'])
        report = json.loads(args.output.read_text()); self.assertEqual(report['script_sha256'], w.digest(self.project / w.DOCS[0]))
        args.output = self.root / 'failed.json'
        client.interactions.create = lambda **kw: SimpleNamespace(status='completed', output_text='{}', steps=[], usage=None)
        with patch.object(g, 'types', fake_types), contextlib.redirect_stdout(io.StringIO()), self.assertRaises(RuntimeError): g.analyze(client, args)
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
        self.approve(); w.authorize_omni_next(self.project, 'Autorizacion ficticia del test local')
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
        args = SimpleNamespace(project_dir=self.project, file=source, prompt_file=prompt, scene='scene1', upload_to_google=True, aspect_ratio='9:16')
        with patch.dict(sys.modules, {'gemini_video': g, 'av': fake_av}), patch.object(g, 'types', SimpleNamespace(UploadFileConfig=lambda **kw: kw)), patch.object(g, 'sdk_problem', return_value=None), patch.object(g, 'read_key', return_value='OFFLINE_KEY'), patch.object(g, 'client_for', return_value=fake_client):
            result = omni.generate(args)
            self.assertEqual(result['status'], 'completed_needs_review')
            self.assertAlmostEqual(result['cost']['estimated_subtotal_usd'], .40544)
            self.assertTrue(Path(result['cost_report']).is_file())
            self.assertEqual(events, ['upload', 'generate', 'delete'])
            args.scene = 'scene2'; prompt.write_text('A different four second camera angle showing the same plant and original timing.')
            with patch.object(g, 'read_key') as no_key, self.assertRaises(ValueError): omni.generate(args)
            no_key.assert_not_called()
            self.assertEqual(events, ['upload', 'generate', 'delete'])
            w.authorize_omni_next(self.project, 'Vi el resultado y coste, genera otra escena', 'scene1')
            fake_client.fail = True
            with self.assertRaises(RuntimeError): omni.generate(args)
        self.assertEqual(events, ['upload', 'generate', 'delete', 'upload', 'generate', 'delete'])
        failed = json.loads((w.metadata(self.project) / 'omni-attempts/scene2.json').read_text())
        self.assertTrue(failed['remote_input_deleted'])
        self.assertEqual(failed['status'], 'failed_or_uncertain')
        self.assertIsNone(failed['cost']['estimated_subtotal_usd'])
        with self.assertRaises(ValueError): omni.require_next_attempt(self.project)

    def test_new_project_text_uses_lf_on_all_platforms(self):
        for path in list(self.project.glob('*.md')) + [w.metadata(self.project) / 'project.json']:
            self.assertNotIn(b'\r', path.read_bytes(), path.name)

    def test_rollback_restores_exact_bytes_profiles_and_script_approval(self):
        self.approve()
        targets = [self.project / n for n in w.DOCS] + [self.profile / 'templates' / n for n in w.DOCS]
        for index, target in enumerate(targets):
            data = target.read_text(encoding='utf-8-sig').encode('utf-8')
            if index % 2 == 0: data = data.replace(b'\n', b'\r\n')
            if index < 2: data = b'\xef\xbb\xbf' + data
            target.write_bytes(data)
        w.confirm_script(self.project, 'Usa este guion')
        state_path = w.metadata(self.project) / 'project.json'
        state_path.write_bytes(state_path.read_bytes().replace(b'\n', b'\r\n'))
        targets.append(state_path)
        before = [p.read_bytes() for p in targets]
        c, t = self.candidates()
        w.stage_revision(self.project, c, t, 'Cambiar documentos y preferencias',
                         self.profile / 'templates' / w.DOCS[0], self.profile / 'templates' / w.DOCS[1])
        real = w.atomic
        def fail_state(path, content):
            if Path(path) == state_path: raise OSError('offline disk failure')
            return real(path, content)
        with patch.object(w, 'atomic', side_effect=fail_state), self.assertRaises(OSError):
            w.apply_revision(self.project, 'Confirmo')
        self.assertEqual(before, [p.read_bytes() for p in targets])
        self.assertTrue(w.require_script(self.project))
        history = next((w.metadata(self.project) / 'history').iterdir())
        for index, target in enumerate(targets[:-1]):
            self.assertEqual(before[index], (history / f'{index}-{target.name}').read_bytes())
        self.assertEqual(before[-1], (history / 'project-before.json').read_bytes())

    def test_incompatible_sdk_has_actionable_error_before_client(self):
        fake = SimpleNamespace(Client=unittest.mock.Mock())
        for version in ('1.74.0', '3.0.0'):
            with self.subTest(version=version), patch.object(g, 'genai', fake), patch.object(g.metadata, 'version', return_value=version):
                with self.assertRaisesRegex(RuntimeError, 'pip install google-genai==2.22.0'):
                    g.client_for('OFFLINE_KEY')
                fake.Client.assert_not_called()
        with patch.object(g.metadata, 'version', side_effect=g.metadata.PackageNotFoundError):
            self.assertIn('no instalado', g.sdk_problem())

    def test_missing_interactions_configuration_closes_client(self):
        client = SimpleNamespace(interactions=SimpleNamespace(), close=unittest.mock.Mock())
        fake = SimpleNamespace(Client=unittest.mock.Mock(return_value=client))
        fake_types = SimpleNamespace(HttpOptions=lambda **kw: kw, HttpRetryOptions=lambda **kw: kw)
        with patch.object(g, 'sdk_problem', return_value=None), patch.object(g, 'genai', fake), patch.object(g, 'types', fake_types):
            with self.assertRaisesRegex(RuntimeError, 'version del SDK'): g.client_for('OFFLINE_KEY')
        client.close.assert_called_once()

    def test_diagnostics_do_not_mistake_codex_for_claude(self):
        codex = self.root / 'codex'; codex.mkdir()
        (codex / 'config.toml').write_text('[mcp_servers.davinci-resolve]\ncommand="python"\n', encoding='utf-8')
        claude = self.root / 'claude.json'
        report = diagnose.inspect_clients('both', self.project, codex, claude)
        self.assertTrue(report['codex']['mcp_config_present'])
        self.assertFalse(report['claude-code']['mcp_config_present'])
        self.assertEqual(list(diagnose.inspect_clients('claude-code', self.project, codex, claude)), ['claude-code'])

    def test_diagnostics_read_claude_scopes_without_echoing_secrets(self):
        repo = self.root / 'mcp repo'; (repo / 'src').mkdir(parents=True)
        (repo / 'src/server.py').write_text('# offline fixture')
        entry = {'command': sys.executable, 'args': [str(repo / 'src/server.py')], 'env': {'TOKEN': 'OFFLINE_SECRET'}}
        claude = self.root / 'claude.json'
        claude.write_text(json.dumps({'mcpServers': {'resolve-user': entry}, 'projects': {
            str(self.project): {'mcpServers': {'resolve-local': entry}},
            str(self.root / 'other'): {'mcpServers': {'resolve-other': entry}}}}))
        (self.project / '.mcp.json').write_text(json.dumps({'mcpServers': {'resolve-project': entry}}))
        report = diagnose.inspect_clients('claude-code', self.project, self.root / 'codex', claude)
        servers = report['claude-code']['servers']
        self.assertEqual({s['scope'] for s in servers}, {'user', 'local', 'project'})
        self.assertTrue(all(s['repo_found'] for s in servers))
        self.assertNotIn('OFFLINE_SECRET', json.dumps(report))
        self.assertFalse(report['claude-code']['mcp_transport']['tested'])

    def test_resolve_probe_allows_setup_without_script(self):
        repo = self.root / 'probe repo'; (repo / 'src').mkdir(parents=True)
        (repo / 'src/server.py').write_text('# offline fixture')
        resolve = SimpleNamespace(GetVersionString=lambda: 'offline-version', GetProjectManager=lambda: SimpleNamespace(GetCurrentProject=lambda: object()))
        connection = unittest.mock.Mock(return_value=resolve)
        capture = io.StringIO()
        argv = ['diagnose.py', '--client', 'claude-code', '--repo', str(repo), '--check-connection']
        with patch.object(diagnose, 'key_present', return_value=False), patch.object(diagnose, 'windows_resolve', return_value={}), patch.object(sys, 'argv', argv), patch.dict(sys.modules, {'src.utils.resolve_bridge_client': SimpleNamespace(connect=connection)}), contextlib.redirect_stdout(capture):
            diagnose.main()
        self.assertTrue(json.loads(capture.getvalue())['connection']['connected'])
        connection.assert_called_once()

    def test_default_script_selection_enables_flow_without_second_confirmation(self):
        technical = (self.project / w.DOCS[1]).read_bytes()
        with self.assertRaises(ValueError): w.require_script(self.project)
        result = subprocess.run([sys.executable, str(SCRIPTS / 'workflow.py'), '--project-dir', str(self.project),
                                 'use-default-script', '--confirmation', 'Usa el guion por defecto'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        script = w.require_script(self.project)
        self.assertIn('Estructura narrativa', script.read_text(encoding='utf-8'))
        self.assertIn('Preferencias creativas del perfil', script.read_text(encoding='utf-8'))
        self.assertEqual(technical, (self.project / w.DOCS[1]).read_bytes())
        approval = w.read_state(self.project)['script_approval']
        self.assertEqual(approval['confirmation'], 'Usa el guion por defecto')
        self.assertEqual(approval['source'], 'default')
        self.assertIsNone(w.read_state(self.project)['omni_plan'])
        self.assertEqual(w.use_default_script(self.project, 'Usa el guion por defecto')['status'], 'default_already_selected')
        other = self.root / 'other video'; w.init_project(other, self.profile)
        with self.assertRaises(ValueError): w.require_script(other)

    def test_default_selection_preserves_own_script_and_needs_user_choice(self):
        before = (self.project / w.DOCS[0]).read_bytes()
        with self.assertRaises(ValueError): w.use_default_script(self.project, '')
        self.assertEqual(before, (self.project / w.DOCS[0]).read_bytes())
        self.approve(); before = (self.project / w.DOCS[0]).read_bytes()
        with self.assertRaises(ValueError): w.use_default_script(self.project, 'Usa el guion por defecto')
        self.assertEqual(before, (self.project / w.DOCS[0]).read_bytes())

    def test_default_preview_is_editable_and_selected_without_overwrite(self):
        paths = w.document_paths(self.project)
        preview = Path(paths['default_script_editable'])
        for value in paths.values():
            self.assertTrue(Path(value).is_absolute() and Path(value).exists())
        custom = preview.read_text(encoding='utf-8') + '\nPreferencia propia: tono documental y ejemplos de jardineria.\n'
        preview.write_bytes(custom.encode('utf-8'))
        w.document_paths(self.project)
        self.assertEqual(preview.read_text(encoding='utf-8'), custom)
        w.use_default_script(self.project, 'Hazlo con el de defecto')
        self.assertIn('tono documental', (self.project / w.DOCS[0]).read_text(encoding='utf-8'))
        with self.assertRaises(ValueError): w.require_production(self.project)
        w.confirm_brief(self.project, 'Usa el brief por defecto', 'default')
        self.assertTrue(w.require_production(self.project))

    def test_changed_brief_blocks_production_and_confirmed_revision_restores_it(self):
        self.approve()
        (self.project / w.DOCS[1]).write_text('Cambios tecnicos nuevos que requieren lectura y eleccion vigente.', encoding='utf-8')
        with self.assertRaises(ValueError): w.require_production(self.project)
        c, t = self.candidates(); w.stage_revision(self.project, c, t, 'Cambiar guion y criterio tecnico')
        w.apply_revision(self.project, 'Correcto, aplica el resumen')
        self.assertTrue(w.require_production(self.project))
        self.assertEqual(w.read_state(self.project)['brief_approval']['sha256'], w.digest(self.project / w.DOCS[1]))

    def test_providers_refuse_missing_brief_before_keys_or_generation(self):
        w.use_default_script(self.project, 'No tengo guion, usa el vuestro')
        with patch.object(images, 'read_key') as key, self.assertRaises(ValueError): images.generate(SimpleNamespace(project_dir=self.project))
        key.assert_not_called()
        with self.assertRaises(ValueError): omni.generate(SimpleNamespace(project_dir=self.project))
        argv = ['prepare_clip.py', '--project-dir', str(self.project), '--source', 'missing.mp4', '--output', 'unused.mp4', '--start', '0']
        clip = load('clip_gate_fixture', SCRIPTS / 'prepare_clip.py')
        with patch.object(sys, 'argv', argv), self.assertRaises(ValueError): clip.main()

    def test_intake_inventory_scopes_folder_without_selecting_or_uploading(self):
        media = self.root / 'media'; media.mkdir(); (media / 'sub').mkdir()
        (media / 'one.MP4').write_bytes(b'offline video')
        (media / 'voice.wav').write_bytes(b'offline audio')
        (media / 'notes.txt').write_text('private non-media fixture')
        (media / 'sub/two.mp4').write_bytes(b'other offline video')
        found = intake.inventory(media)
        self.assertEqual(len(found['files']), 2)
        self.assertEqual({x['kind'] for x in found['files']}, {'video', 'audio'})
        self.assertEqual(len(intake.inventory(media, True)['files']), 3)
        self.assertFalse((w.metadata(self.project) / 'intake.json').exists())

    def test_intake_tracks_exact_selected_files_and_multiple_outputs(self):
        self.approve()
        videos = []
        for name in ['one.mp4', 'two.mp4', 'unused.mp4']:
            path = self.root / name; path.write_bytes(b'offline fixture'); videos.append(str(path))
        answers = {'videos': videos[:2], 'output_count': 2, 'omni': False, 'images': 'provided',
                   'user_responses': ['Solo one y two, dos videos, sin Omni y con mis imagenes'],
                   'outputs': [{'id': 'video-01', 'purpose': 'Primera explicacion', 'videos': [videos[0]]},
                               {'id': 'video-02', 'purpose': 'Segunda explicacion', 'videos': [videos[1]]}]}
        result = intake.save_intake(self.project, answers)
        record = json.loads(Path(result['path']).read_text(encoding='utf-8'))
        self.assertEqual(record['output_count'], 2)
        self.assertFalse(record['omni'])
        self.assertNotIn(videos[2], record['videos'])
        self.assertIn('video-02', Path(result['summary']).read_text(encoding='utf-8'))
        answers['outputs'][1]['videos'] = [videos[2]]
        with self.assertRaises(ValueError): intake.save_intake(self.project, answers)
        self.assertEqual(record, json.loads(Path(result['path']).read_text(encoding='utf-8')))
        answers['output_count'] = 3
        with self.assertRaises(ValueError): intake.save_intake(self.project, answers)


if __name__ == '__main__':
    unittest.main(verbosity=2)
