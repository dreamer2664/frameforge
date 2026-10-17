#!/usr/bin/env python3
"""Publish ONLY your own final media to storagecode, with immutable hashes.
Then archive your HANDOFF + receipts and append primary INDEX/PUSHES rows.
Never uploads the private stamped brief. No credential appears in a URL.
"""
from pathlib import Path
import argparse,base64,datetime,hashlib,http.client,json,mimetypes,os,re,subprocess,sys,urllib.error,urllib.parse,urllib.request

ROOT=Path(__file__).resolve().parents[1];REPO='dreamer2664/storagecode';AGENTS=('kinetic','scribble','axiom','parallax','glyphcraft','lithos')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
def token():
    value=os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN') or os.environ.get('CHATCODE_TOKEN')
    if not value:raise RuntimeError('Source your PRIVATE env; never paste a token into the command line.')
    return value

def api(method,path,data=None):
    body=json.dumps(data).encode() if data is not None else None
    req=urllib.request.Request('https://api.github.com/repos/'+REPO+'/'+path.lstrip('/'),data=body,method=method,headers={'Authorization':'Bearer '+token(),'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','Content-Type':'application/json','User-Agent':'frameforge-publisher'})
    with urllib.request.urlopen(req,timeout=180) as r:return json.load(r)

def put_file(path,content,message):
    for _ in range(6):
        try:old=api('GET','contents/'+urllib.parse.quote(path,safe='/'))
        except urllib.error.HTTPError as e:
            if e.code!=404:raise
            old=None
        payload={'message':message,'content':base64.b64encode(content).decode(),'branch':'main'}
        if old:payload['sha']=old['sha']
        try:return api('PUT','contents/'+urllib.parse.quote(path,safe='/'),payload)
        except urllib.error.HTTPError as e:
            if e.code not in (409,422):raise
    raise RuntimeError('Concurrent storage write: bounded retries exhausted, preserve local receipt and retry later.')

def append_row(path,row,identity,message):
    for _ in range(6):
        old=api('GET','contents/'+urllib.parse.quote(path,safe='/'));text=base64.b64decode(old['content']).decode()
        if identity in text:return {'already_present':True,'sha':old['sha']}
        payload={'message':message,'content':base64.b64encode((text.rstrip()+'\n'+row+'\n').encode()).decode(),'sha':old['sha'],'branch':'main'}
        try:return api('PUT','contents/'+urllib.parse.quote(path,safe='/'),payload)
        except urllib.error.HTTPError as e:
            if e.code not in (409,422):raise
    raise RuntimeError('Append conflict; do not overwrite the ledger or drop someone else\'s rows.')

def own_file(agent,path):
    file=Path(path).resolve();own=(ROOT/'agents'/agent).resolve()
    if not file.is_file() or not file.is_relative_to(own):raise ValueError('Only files physically inside your own agents/<name>/ tree may be uploaded.')
    if any(p in ('.private','private') for p in file.parts) or file.name.startswith('.env'):raise ValueError('Protected/private path')
    if file.suffix.lower() not in ('.mp4','.png','.jpg','.jpeg','.srt','.vtt','.json','.txt','.pdf'):raise ValueError('Unexpected media/sidecar type; private MDs and code archives are not uploadable assets here.')
    # Scan only the explicitly selected file for the known live credentials, while hashing it.
    secrets=[os.environ[k].encode() for k in ('CHATCODE_TOKEN','GITHUB_TOKEN','GH_TOKEN') if os.environ.get(k)];keep=max(map(len,secrets),default=1)-1;tail=b'';h=hashlib.sha256()
    with file.open('rb') as src:
        for block in iter(lambda:src.read(1024*1024),b''):
            h.update(block);data=tail+block
            if any(s in data for s in secrets):raise ValueError('Known credential in selected file; upload refused.')
            tail=data[-keep:] if keep else b''
    return file,h.hexdigest()

def upload(release,file,digest):
    existing=next((a for a in release['assets'] if a['name']==file.name),None)
    if existing:
        if existing.get('digest')!='sha256:'+digest:raise ValueError('Existing same-name asset lacks matching digest; never overwrite immutable evidence.')
        return existing
    url=release['upload_url'].split('{')[0];parts=urllib.parse.urlsplit(url)
    if parts.scheme!='https' or parts.hostname!='uploads.github.com':raise ValueError('Unexpected upload host')
    conn=http.client.HTTPSConnection(parts.hostname,timeout=900);target=parts.path+'?'+urllib.parse.urlencode({'name':file.name})
    conn.putrequest('POST',target);conn.putheader('Authorization','Bearer '+token());conn.putheader('Accept','application/vnd.github+json');conn.putheader('User-Agent','frameforge-publisher');conn.putheader('Content-Type',mimetypes.guess_type(file.name)[0] or 'application/octet-stream');conn.putheader('Content-Length',str(file.stat().st_size));conn.endheaders()
    with file.open('rb') as src:
        for block in iter(lambda:src.read(1024*1024),b''):conn.send(block)
    response=conn.getresponse();body=response.read();conn.close()
    if response.status!=201:raise RuntimeError('Asset upload HTTP '+str(response.status)+'; keep local file and inspect API error without exposing auth headers.')
    result=json.loads(body)
    if result['size']!=file.stat().st_size:raise RuntimeError('Remote asset byte count mismatch')
    if result.get('digest') and result['digest']!='sha256:'+digest:raise RuntimeError('Remote asset digest mismatch')
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('agent',choices=AGENTS);p.add_argument('--video',required=True);p.add_argument('--asset',action='append',default=[]);p.add_argument('--title',required=True);p.add_argument('--revision',required=True);a=p.parse_args()
    if not re.fullmatch(r'r\d{2,3}',a.revision):p.error('--revision must look like r01')
    video,digest=own_file(a.agent,a.video)
    if video.suffix.lower()!='.mp4':p.error('--video requires MP4')
    files=[(video,digest)]+[own_file(a.agent,s) for s in a.asset];tag=f'frameforge/{a.agent}/{a.revision}-{digest[:12]}'
    code_sha=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    try:release=api('GET','releases/tags/'+urllib.parse.quote(tag,safe=''))
    except urllib.error.HTTPError as e:
        if e.code!=404:raise
        release=api('POST','releases',{'tag_name':tag,'name':f'{a.agent} — {a.title} ({a.revision})','body':f'Independent Frameforge commission; NOT an accepted old-campaign film.\nVideo SHA256: `{digest}`\nCode: dreamer2664/frameforge@{code_sha}\nSee uploaded QC and visual-review evidence. Publication is not a human artistic approval.','draft':False,'prerelease':False})
    assets=[]
    for file,sha in files:
        uploaded=upload(release,file,sha);assets.append({'name':file.name,'bytes':file.stat().st_size,'sha256':sha,'url':uploaded['browser_download_url'],'remote_digest':uploaded.get('digest'),'remote_size':uploaded['size']})
    receipt={'agent':a.agent,'published_at':now(),'revision':a.revision,'code_sha':code_sha,'release':release['html_url'],'tag':tag,'assets':assets,'acceptance':'Published candidate; refer to actual reviews. Not an old-campaign acceptance.'}
    evidence=ROOT/'agents'/a.agent/'evidence';evidence.mkdir(parents=True,exist_ok=True);local=evidence/f'{a.revision}-publication.json';local.write_text(json.dumps(receipt,indent=2)+'\n')
    folder=f'data/frameforge/{a.agent}/{a.revision}-{digest[:12]}'
    put_file(folder+'/publication.json',local.read_bytes(),f'{a.agent}: archive actual media receipt {digest[:12]}')
    log=ROOT/'agents'/a.agent/'HANDOFF.md'
    if log.exists():
        text=log.read_text()
        if any(os.environ.get(k) and os.environ[k] in text for k in ('CHATCODE_TOKEN','GITHUB_TOKEN','GH_TOKEN')):raise ValueError('Credential in HANDOFF; archive refused')
        put_file(folder+'/HANDOFF.md',text.encode(),f'{a.agent}: durable action/handoff record')
    identity=f'frameforge/{a.agent}/{a.revision}-{digest[:12]}'
    append_row('data/INDEX.md',f'| {now()[:10]} | {a.agent} | [Frameforge {a.revision}]({folder.removeprefix("data/")}/publication.json) | {identity}; [media]({release["html_url"]}); SHA256 {digest} |',identity,f'{a.agent}: index independent film media')
    append_row('PUSHES.md',f'| {now()} | {a.agent} | frameforge | `{code_sha[:12]}` | {identity}; [primary media]({release["html_url"]}) |',identity,f'{a.agent}: record film source publication')
    receipt['primary_archive']='https://github.com/'+REPO+'/tree/main/'+folder;local.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));return 0
if __name__=='__main__':sys.exit(main())
