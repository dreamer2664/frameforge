#!/usr/bin/env python3
"""Immutable small text/JSON/MD evidence → the sole primary storagecode archive.
Private kits are forbidden; only explicitly selected files in your own workspace.
"""
from pathlib import Path
import argparse,base64,json,os,re,sys,urllib.error
from release import ROOT,AGENTS,REPO,api,put_file,append_row,now

def archive(agent,run,files):
    own=(ROOT/'agents'/agent).resolve();folder=f'data/frameforge/{agent}/{run}';result=[]
    for item in files:
        file=Path(item).resolve()
        if not file.is_file() or not file.is_relative_to(own):raise ValueError('Only your own physical workspace files may be archived')
        if file.suffix.lower() not in ('.md','.json','.txt','.srt','.vtt','.csv') or file.stat().st_size>1024*1024:raise ValueError('Small evidence documents only; use a Release for large media')
        if any(p in ('.private','private') for p in file.parts) or file.name.startswith('.env'):raise ValueError('Protected path')
        data=file.read_bytes()
        if any(os.environ.get(k) and os.environ[k].encode() in data for k in ('CHATCODE_TOKEN','GITHUB_TOKEN','GH_TOKEN')):raise ValueError('Live credential found; archive refused')
        target=folder+'/'+file.relative_to(own).as_posix()
        try:old=api('GET','contents/'+target)
        except urllib.error.HTTPError as e:
            if e.code!=404:raise
            old=None
        if old and base64.b64decode(old['content'])!=data:raise ValueError('Immutable evidence path already holds different content; use a new run/revision, never overwrite')
        if not old:
            payload={'message':f'{agent}: preserve independent film evidence {run}','content':base64.b64encode(data).decode(),'branch':'main'}
            try:api('PUT','contents/'+target,payload)
            except urllib.error.HTTPError as exc:
                if exc.code not in (409,422):raise
                existing=api('GET','contents/'+target)
                if base64.b64decode(existing['content'])!=data:raise ValueError('Concurrent immutable evidence collision; use a new run without overwriting') from None
        result.append('https://github.com/'+REPO+'/blob/main/'+target)
    identity=f'frameforge/{agent}/evidence/{run}'
    append_row('data/INDEX.md',f'| {now()[:10]} | {agent} | [Frameforge evidence](https://github.com/{REPO}/tree/main/{folder}) | {identity} |',identity,f'{agent}: index complete own evidence/handoff')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('agent',choices=AGENTS);p.add_argument('--run',required=True);p.add_argument('--file',action='append',required=True);a=p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}',a.run):p.error('Safe immutable run identifier required')
    print(json.dumps({'archived':archive(a.agent,a.run,a.file)},indent=2))
