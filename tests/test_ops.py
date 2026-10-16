"""Offline safety/behaviour tests. Fixtures are NOT commissioned films."""
from pathlib import Path
import contextlib,io,json,os,re,subprocess,sys,tempfile,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'ops'))
import field
import release
from media_qc import check,RANGES
from visualize import sample_times
from render_dashboard import render as render_dashboard

class JournalTests(unittest.TestCase):
    def test_identity_is_fenced(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):field.home('../axiom',t)
    def test_actions_failures_and_next_survive(self):
        with tempfile.TemporaryDirectory() as t:
            field.event('kinetic','failure','Render r01','Missing glyph; cause confirmed: font not loaded',state='failed',root=t)
            field.event('kinetic','fix','Wait for document.fonts.ready','Glyph restored; actual frame opened',next_action='Export r02',artifact='evidence/frame.png',root=t)
            text=(Path(t)/'agents/kinetic/HANDOFF.md').read_text();self.assertIn('Missing glyph',text);self.assertIn('Glyph restored',text);self.assertIn('Export r02',text)
            self.assertEqual(len((Path(t)/'agents/kinetic/events.jsonl').read_text().splitlines()),2)
    def test_known_credentials_are_redacted(self):
        with tempfile.TemporaryDirectory() as t,patch.dict(os.environ,{'GITHUB_TOKEN':'unit-test-not-a-live-key'}):
            field.event('scribble','test','unit-test-not-a-live-key','unit-test-not-a-live-key',root=t)
            self.assertNotIn('unit-test-not-a-live-key',(Path(t)/'agents/scribble/HANDOFF.md').read_text())
    def test_child_has_no_inherited_crew_key(self):
        with tempfile.TemporaryDirectory() as t,patch.dict(os.environ,{'GITHUB_TOKEN':'unit-test-not-a-live-key'}),contextlib.redirect_stdout(io.StringIO()):
            rc=field.run_tracked('axiom',[sys.executable,'-c','import os;print("CLEAN" if "GITHUB_TOKEN" not in os.environ else "LEAK")'],'runtime-test',root=t)
            self.assertEqual(rc,0);text=(Path(t)/'agents/axiom/HANDOFF.md').read_text();self.assertIn('Last observed output: CLEAN',text)
    def test_silent_partial_line_child_still_observed(self):
        with tempfile.TemporaryDirectory() as t,contextlib.redirect_stdout(io.StringIO()):
            rc=field.run_tracked('kinetic',[sys.executable,'-c','import time;print("partial",end="",flush=True);time.sleep(.18)'],'runtime-test',interval=.04,root=t)
            self.assertEqual(rc,0);records=[json.loads(x) for x in (Path(t)/'agents/kinetic/events.jsonl').read_text().splitlines()];self.assertTrue(any(x['kind']=='process-observation' for x in records))
            self.assertEqual(json.loads((Path(t)/'status/kinetic.json').read_text())['state'],'checkpoint')
    def test_nonzero_child_is_failure_not_delivery(self):
        with tempfile.TemporaryDirectory() as t,contextlib.redirect_stdout(io.StringIO()):
            rc=field.run_tracked('axiom',[sys.executable,'-c','raise SystemExit(7)'],'runtime-test',root=t)
            self.assertEqual(rc,7);self.assertEqual(json.loads((Path(t)/'status/axiom.json').read_text())['state'],'failed')
    def test_missing_command_does_not_leave_running(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(field.run_tracked('scribble',['/this-command-does-not-exist'],'runtime-test',root=t),127)
            self.assertEqual(json.loads((Path(t)/'status/scribble.json').read_text())['state'],'failed')

class GitTests(unittest.TestCase):
    def setup_repos(self,t):
        t=Path(t);bare=t/'origin.git';first=t/'first';second=t/'second'
        self.git(None,'init','--bare','--initial-branch=main',str(bare));self.git(None,'clone',str(bare),str(first));self.identity(first)
        (first/'README.md').write_text('Fixture only\n');self.git(first,'add','.');self.git(first,'commit','-m','fixture');self.git(first,'push','origin','main')
        self.git(None,'clone',str(bare),str(second));self.identity(second);return first,second
    def identity(self,p):self.git(p,'config','user.name','fixture');self.git(p,'config','user.email','fixture@example.invalid')
    def git(self,p,*args):
        return subprocess.check_output(['git',*(['-C',str(p)] if p else []),*args],stderr=subprocess.DEVNULL).decode()
    def test_parallel_independent_workspaces_rebase_without_loss(self):
        with tempfile.TemporaryDirectory() as t,patch.object(field,'record_source_push'),contextlib.redirect_stdout(io.StringIO()):
            a,b=self.setup_repos(t);field.event('kinetic','test','A','A',root=a);field.event('axiom','test','B','B',root=b)
            field.publish('kinetic',a);field.publish('axiom',b);self.git(a,'pull','--rebase','origin','main')
            self.assertTrue((a/'agents/kinetic/HANDOFF.md').exists());self.assertTrue((a/'agents/axiom/HANDOFF.md').exists())
    def test_foreign_staged_changes_refused(self):
        with tempfile.TemporaryDirectory() as t,patch.object(field,'record_source_push'):
            a,_=self.setup_repos(t);(a/'README.md').write_text('Foreign staged edit');self.git(a,'add','README.md');field.event('kinetic','test','A','A',root=a)
            with self.assertRaisesRegex(RuntimeError,'Foreign staged'):field.publish('kinetic',a)
    def test_credential_in_own_tracked_file_refused(self):
        with tempfile.TemporaryDirectory() as t,patch.object(field,'record_source_push'),patch.dict(os.environ,{'GITHUB_TOKEN':'unit-test-not-a-live-key'}):
            a,_=self.setup_repos(t);p=field.home('kinetic',a);(p/'oops.txt').write_text('unit-test-not-a-live-key');field.event('kinetic','test','A','A',root=a)
            with self.assertRaisesRegex(RuntimeError,'Live credential'):field.publish('kinetic',a)

class PublicationSafetyTests(unittest.TestCase):
    def test_foreign_folder_and_md_upload_refused(self):
        with tempfile.TemporaryDirectory() as t,patch.object(release,'ROOT',Path(t)):
            p=Path(t)/'agents/axiom';p.mkdir(parents=True);f=p/'video.mp4';f.write_bytes(b'fixture')
            with self.assertRaises(ValueError):release.own_file('kinetic',f)
            f=p/'PRIVATE.md';f.write_text('not for release')
            with self.assertRaises(ValueError):release.own_file('axiom',f)
    def test_credential_split_across_read_blocks_refused(self):
        with tempfile.TemporaryDirectory() as t,patch.object(release,'ROOT',Path(t)),patch.dict(os.environ,{'GITHUB_TOKEN':'unit-test-not-a-live-key'}):
            p=Path(t)/'agents/axiom';p.mkdir(parents=True);f=p/'video.mp4';f.write_bytes(b'x'*(1024*1024-10)+b'unit-test-not-a-live-key')
            with self.assertRaisesRegex(ValueError,'credential'):release.own_file('axiom',f)
    def test_symlink_to_other_agent_refused(self):
        with tempfile.TemporaryDirectory() as t,patch.object(release,'ROOT',Path(t)):
            a=Path(t)/'agents/axiom';b=Path(t)/'agents/kinetic';a.mkdir(parents=True);b.mkdir();(b/'video.mp4').write_bytes(b'fixture');(a/'link.mp4').symlink_to(b/'video.mp4')
            with self.assertRaises(ValueError):release.own_file('axiom',a/'link.mp4')

class InspectionTests(unittest.TestCase):
    def test_final_samples_are_chronological_and_unique(self):
        values=sample_times(9.076,3);self.assertEqual(values,sorted(set(values)));self.assertTrue(all(0<=v<9.076 for v in values))
    def test_bad_sampling_interval_refused(self):
        with self.assertRaises(ValueError):sample_times(1,0)

class CharterTests(unittest.TestCase):
    def test_all_briefs_are_substantial_clean_and_independent(self):
        for agent in field.AGENTS:
            text=(ROOT/'briefs'/(agent.upper()+'.md')).read_text();self.assertGreater(len(text.split()),3000);self.assertIn('Do not ask the Director',text);self.assertIn('HANDOFF.md',text);self.assertIn('every five minutes',text);self.assertEqual(text.count('CHATCODE_TOKEN=PENDING-ISSUE'),1);self.assertEqual(text.count('GITHUB_TOKEN=PENDING-ISSUE'),1);self.assertNotIn('@@',text)
    def test_embedded_credential_bootstrap_is_executable_and_private(self):
        text=(ROOT/'briefs/KINETIC.md').read_text();code=text.split("python3 - <<'PY'\n",1)[1].split('\nPY\n',1)[0]
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);kit=p/'private-kit.md';kit.write_text(text.replace('CHATCODE_TOKEN=PENDING-ISSUE','CHATCODE_TOKEN=unit-test-chat-key').replace('GITHUB_TOKEN=PENDING-ISSUE','GITHUB_TOKEN=unit-test-git-key'))
            with patch.dict(os.environ,{'HOME':t,'FRAMEFORGE_KIT':str(kit),'FRAMEFORGE_AGENT':'kinetic'}):exec(compile(code,'brief-bootstrap','exec'),{})
            self.assertEqual((p/'.private/kinetic.env').stat().st_mode&0o777,0o600);self.assertEqual((p/'.private/frameforge-askpass.sh').stat().st_mode&0o777,0o700)
            out=subprocess.check_output([str(p/'.private/frameforge-askpass.sh'),'Username for GitHub']);self.assertEqual(out.strip(),b'x-access-token')
    def test_qc_cannot_certify_artistic_approval(self):
        text=(ROOT/'ops/media_qc.py').read_text();self.assertIn('TECHNICAL ONLY',text);self.assertIn('Full decode failed',text)

class SuccessorCommissionTests(unittest.TestCase):
    def test_roles_are_enabled_in_journal_release_and_qc(self):
        for agent in ('parallax','glyphcraft'):
            self.assertIn(agent,field.AGENTS)
            self.assertIn(agent,release.AGENTS)
            self.assertEqual(RANGES[agent],(35,55))
            with tempfile.TemporaryDirectory() as t:
                s=field.event(agent,'commissioner-setup','Prepared an open successor slot','No agent session or film exists; task remains open and unclaimed.',state='not-started',root=t)
                self.assertEqual(s['state'],'not-started')
                self.assertTrue((Path(t)/'agents'/agent/'HANDOFF.md').is_file())
                self.assertEqual(json.loads((Path(t)/'status'/f'{agent}.json').read_text())['state'],'not-started')
    def test_dashboard_snapshots_and_fetches_all_five_slots(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for agent in ('kinetic','scribble','axiom','parallax','glyphcraft'):
                folder=root/'status';folder.mkdir(exist_ok=True)
                (folder/f'{agent}.json').write_text(json.dumps({'agent':agent,'updated_at':'2026-10-16T00:00:00Z','state':'not-started','stage':'commissioned','observed_activity':'Prepared only','artifact':'','next_action':'Wait for a real wake'}))
            path=render_dashboard(root);html=Path(path).read_text()
            for agent in ('kinetic','scribble','axiom','parallax','glyphcraft'):
                self.assertIn(agent,html)
            self.assertIn('five public status files',html)
            self.assertIn('Kinetic successor / spatial typography',html)
            self.assertIn('Kinetic successor / living letterforms',html)

if __name__=='__main__':unittest.main()
