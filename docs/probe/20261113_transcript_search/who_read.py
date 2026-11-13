"""Inputs only: for every transcript active after T0, its role (first prompt's head) and its tool calls after T0 whose
input names a transcript (8c5f8396, .jsonl, or the projects folder). Prints no tool result."""
import json,sys,glob,os,re
T0='2026-11-13T15:32:08.743Z'
base=os.path.expanduser('~/.claude/projects/-Users-chalshik-Projects-aftershock-artifacts/')
files=[f for f in glob.glob(base+'*.jsonl')+glob.glob(base+'*/subagents/*.jsonl') if '8c5f8396-cce6-43e6-b8a1-890bcd5373c5.jsonl' not in f and os.path.getmtime(f)>1763047928]
for f in sorted(files):
    role=None; calls=[]; last=None
    for l in open(f,errors='replace'):
        try: d=json.loads(l)
        except: continue
        ts=d.get('timestamp') or ''
        if ts: last=ts
        m=d.get('message')
        if not isinstance(m,dict): continue
        c=m.get('content')
        if role is None and d.get('type')=='user':
            t=c if isinstance(c,str) else ''.join(x.get('text','') for x in c if isinstance(x,dict)) if isinstance(c,list) else ''
            if t.strip(): role=re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',t))[:110]
        if isinstance(c,list) and ts>T0:
            for x in c:
                if isinstance(x,dict) and x.get('type')=='tool_use' and x.get('name') in ('Bash','Read','Grep','Glob'):
                    s=json.dumps(x.get('input'))
                    if re.search(r'8c5f8396|\.jsonl|\.claude/projects',s): calls.append((ts[11:19],x['name'],s))
    if last and last>T0:
        rel=f.replace(base,'')
        print(f"== {rel[:60]} last={last[11:19]} calls={len(calls)} role={role}")
        for c in calls: print('   ',c[0],c[1],c[2][:200])
