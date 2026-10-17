#!/usr/bin/env python3
"""Per-producer action journal, factual heartbeat and tracked-process runner.
No simulation, no detached heartbeat daemon, no secrets in logs.
"""
from pathlib import Path
import argparse,codecs,datetime as dt,json,os,selectors,shlex,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[1]
AGENTS=('kinetic','scribble','axiom','parallax','glyphcraft','lithos')

def utc():return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
def redact(value):
    text=str(value)
    for key in ('CHATCODE_TOKEN','GITHUB_TOKEN','GH_TOKEN'):
        secret=os.environ.get(key)
        if secret:text=text.replace(secret,'[REDACTED]')
    return text

def home(agent,root=ROOT):
    if agent not in AGENTS:raise ValueError('Unknown producer identity')
    p=Path(root)/'agents'/agent;p.mkdir(parents=True,exist_ok=True);return p

def update_handoff(agent,state,root=ROOT):
    p=home(agent,root);journal=p/'events.jsonl'
    records=[json.loads(l) for l in journal.read_text().splitlines() if l.strip()] if journal.exists() else []
    lines=[f'# {agent} — LIVE HANDOFF / ACTION RECORD','',
      '> Public working memory. No token, cookie, password, auth header, private prompt or hidden chain-of-thought belongs here.','',
      '## Resume here','',f'- Updated: {state["updated_at"]}',f'- State: **{state["state"]}**',f'- Stage: {state["stage"]}',
      f'- Last observed activity: {state["observed_activity"]}',f'- Latest evidence/artifact: {state.get("artifact") or "not supplied"}',
      f'- Next concrete action: {state.get("next_action") or "see most recent action below"}',
      '- Source: your own agents/'+agent+'/ tree; never wait for another producer.',
      '- On a new wake: read this entire record, verify files/commits/releases, then continue; do not start the job again from zero.','',
      '## Every recorded action and discovery (append-only source = events.jsonl)','']
    for r in records:
        lines.extend([f'### {r["ts"]} — {r["kind"]}',f'- Action: {r["action"]}',f'- Result/discovery: {r["result"]}',
                      f'- Evidence: {r.get("artifact") or "none yet"}',f'- Next: {r.get("next_action") or "continue current stage"}',''])
    (p/'HANDOFF.md').write_text('\n'.join(lines)+'\n')

def event(agent,kind,action,result,*,stage='production',state='working',artifact='',next_action='',root=ROOT):
    if state not in ('working','process-running','checkpoint','blocked','delivered','stopped','failed','not-started'):raise ValueError('Invalid state')
    now=utc();r={'ts':now,'kind':kind,'action':redact(action),'result':redact(result),'artifact':redact(artifact),'next_action':redact(next_action)}
    p=home(agent,root)
    with (p/'events.jsonl').open('a') as f:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    status={'agent':agent,'updated_at':now,'state':state,'stage':redact(stage),'observed_activity':r['result'],'artifact':r['artifact'],'next_action':r['next_action'],'heartbeat_interval_seconds':300,'note':'Fresh timestamp is evidence of this observation, NOT a promise that an AI session continues after it stops.'}
    s=Path(root)/'status';s.mkdir(parents=True,exist_ok=True)
    (s/(agent+'.json')).write_text(json.dumps(status,indent=2,ensure_ascii=False)+'\n');update_handoff(agent,status,root)
    return status

def record_source_push(agent,root=ROOT):
    from release import append_row,now
    sha=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    identity=f'frameforge/{agent}/source/{sha}'
    row=f'| {now()} | {agent} | frameforge | `{sha[:12]}` | {identity}; [source](https://github.com/dreamer2664/frameforge/commit/{sha}) |'
    append_row('PUSHES.md',row,identity,f'{agent}: primary ledger of source checkpoint')

def publish(agent,root=ROOT):
    """Only this producer's own tree/status. Never stages someone else's files."""
    home(agent,root)
    env=dict(os.environ,GIT_TERMINAL_PROMPT='0')
    for args in (["add","--",f'agents/{agent}',f'status/{agent}.json'],):
        subprocess.run(['git','-C',str(root),*args],check=True,env=env)
    names=subprocess.check_output(['git','-C',str(root),'diff','--cached','--name-only','-z']).decode().split('\0')
    if any(n and not (n.startswith(f'agents/{agent}/') or n==f'status/{agent}.json') for n in names):
        raise RuntimeError('Foreign staged changes found; checkpoint refuses to commit another producer\'s work.')
    for key in ('CHATCODE_TOKEN','GITHUB_TOKEN','GH_TOKEN'):
        secret=env.get(key)
        if secret:
            match=subprocess.run(['git','-C',str(root),'grep','--cached','-F','-q','-f','-','--'],input=(secret+'\n').encode(),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            if match.returncode==0:raise RuntimeError('Live credential detected in staged/tracked content; refusing commit and push.')
    staged=subprocess.run(['git','-C',str(root),'diff','--cached','--quiet'],env=env)
    if staged.returncode:
        subprocess.run(['git','-C',str(root),'commit','-m',f'{agent}: checkpoint / factual heartbeat'],check=True,env=env)
    for _ in range(4):
        q=subprocess.run(['git','-C',str(root),'pull','--rebase','origin','main'],env=env,capture_output=True,text=True)
        if q.returncode:raise RuntimeError('Rebase requires inspection; preserve all changes. '+redact(q.stderr[-600:]))
        q=subprocess.run(['git','-C',str(root),'push','origin','HEAD:main'],env=env,capture_output=True,text=True)
        if q.returncode==0:
            try:record_source_push(agent,root)
            except Exception as exc:raise RuntimeError('SOURCE PUSH CONFIRMED, primary ledger sync pending: '+redact(exc)) from None
            return
        if not any(t in q.stderr.lower() for t in ('fetch first','non-fast-forward','rejected')):break
    raise RuntimeError('Checkpoint push not confirmed; keep working locally and retry, do not claim remote sync. '+redact(q.stderr[-600:]))

def run_tracked(agent,cmd,stage,*,interval=300,push=False,root=ROOT):
    if not cmd:raise ValueError('An actual command is required')
    p=home(agent,root);work=p/'work';work.mkdir(exist_ok=True)
    logfile=work/('process-'+str(time.time_ns())+'.log')
    event(agent,'command-start',shlex.join(cmd),'Launching actual child process; not yet proof of progress.',stage=stage,state='process-running',artifact=str(logfile),root=root)
    child_env={k:v for k,v in os.environ.items() if k not in ('CHATCODE_TOKEN','GITHUB_TOKEN','GH_TOKEN')}
    try:child=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=0,cwd=p,env=child_env)
    except OSError as exc:
        event(agent,'command-launch-failed',shlex.join(cmd),redact(exc),stage=stage,state='failed',next_action='Repair the command/runtime or switch backend; no child is running.',root=root)
        return 127
    sel=selectors.DefaultSelector();sel.register(child.stdout,selectors.EVENT_READ);last=time.monotonic();lines=0;bytes_seen=0;latest='No completed output line observed yet.';pending='';decoder=codecs.getincrementaldecoder('utf-8')('replace')
    try:
        with logfile.open('w') as out:
            while True:
                for key,_ in sel.select(timeout=min(1,interval)):
                    chunk=os.read(key.fileobj.fileno(),8192)
                    if chunk:
                        bytes_seen+=len(chunk);pending+=decoder.decode(chunk)
                        while '\n' in pending or '\r' in pending:
                            cuts=[i for i in (pending.find('\n'),pending.find('\r')) if i>=0];cut=min(cuts)
                            line=redact(pending[:cut+1]);pending=pending[cut+1:]
                            out.write(line);out.flush();print(line,end='',flush=True);lines+=1;latest=line.strip()[-500:]
                    else:
                        pending+=decoder.decode(b'',final=True)
                        if pending:
                            line=redact(pending);out.write(line);out.flush();print(line,flush=True);lines+=1;latest=line.strip()[-500:];pending=''
                        sel.unregister(child.stdout)
                if child.poll() is not None and not sel.get_map():break
                if time.monotonic()-last>=interval and child.poll() is None:
                    event(agent,'process-observation',shlex.join(cmd),f'Child PID {child.pid} exists; {lines} completed output lines / {bytes_seen} bytes observed. Latest: {latest}. Process liveness alone does not certify creative progress.',stage=stage,state='process-running',artifact=str(logfile),root=root)
                    if push:
                        try:publish(agent,root)
                        except Exception as e:print('Heartbeat sync pending:',redact(e),file=sys.stderr)
                    last=time.monotonic()
        rc=child.wait()
        event(agent,'command-end',shlex.join(cmd),f'Exit {rc}; {lines} lines. Last observed output: {latest}',stage=stage,state='checkpoint' if rc==0 else 'failed',artifact=str(logfile),next_action='Inspect output and continue production; command success is not film completion.',root=root)
        if push:
            try:publish(agent,root)
            except Exception as e:print('Final checkpoint sync pending:',redact(e),file=sys.stderr)
        return rc
    except BaseException:
        child.terminate()
        try:child.wait(timeout=8)
        except subprocess.TimeoutExpired:child.kill();child.wait()
        event(agent,'interrupted',shlex.join(cmd),'Wrapper interrupted; child terminated, NOT still working.',stage=stage,state='stopped',artifact=str(logfile),root=root)
        raise
    finally:sel.close();child.stdout.close()

def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='command',required=True)
    e=s.add_parser('event');e.add_argument('agent',choices=AGENTS);e.add_argument('--kind',default='action');e.add_argument('--action',required=True);e.add_argument('--result',required=True);e.add_argument('--stage',default='production');e.add_argument('--state',default='working');e.add_argument('--artifact',default='');e.add_argument('--next',default='');e.add_argument('--push',action='store_true')
    r=s.add_parser('run');r.add_argument('agent',choices=AGENTS);r.add_argument('--stage',required=True);r.add_argument('--push',action='store_true');r.add_argument('cmd',nargs='*')
    u=s.add_parser('publish');u.add_argument('agent',choices=AGENTS)
    raw=sys.argv[1:];child_args=None
    if raw and raw[0]=='run' and '--' in raw:
        divider=raw.index('--');child_args=raw[divider+1:];raw=raw[:divider]
    a=p.parse_args(raw)
    if a.command=='event':
        status=event(a.agent,a.kind,a.action,a.result,stage=a.stage,state=a.state,artifact=a.artifact,next_action=a.next)
        if a.push:publish(a.agent)
        print(json.dumps(status,indent=2))
    elif a.command=='publish':publish(a.agent)
    else:
        cmd=child_args if child_args is not None else a.cmd
        return run_tracked(a.agent,cmd,a.stage,push=a.push)
    return 0
if __name__=='__main__':sys.exit(main())
