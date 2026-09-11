#!/usr/bin/env python3
"""Run 48 isolated, local-only Codex guidance trials. Requires existing Codex login.
Usage: python3.12 run_trials.py [--workers 3] [--limit N]
No provider keys are passed; Codex uses the existing account authentication.
"""
import argparse, concurrent.futures, hashlib, json, os, pathlib, shutil, signal, subprocess, time

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
ROOT = pathlib.Path('/private/tmp/pxt-skill-eval-20260906')
PYTHON = ROOT / 'venv/bin/python'
SCENARIOS = {
 'http-app': 'Build a local Pixeltable HTTP application in app.py with a docs table (doc_id Int, title String, body optional String), computed uppercase title and a deterministic 12-character excerpt. Provide an insert endpoint and a compute-only uppercase endpoint. Apply schema, start the managed local HTTP service, discover its URL, POST a sample, and verify returned computed fields and that compute-only does not insert. Record runnable commands and evidence.',
 'document-retrieval': 'Build a declarative document retrieval application in app.py. Create a small local text or HTML document fixture, store it as Document, split it into chunks with document_splitter, and index chunk text with a deterministic local embedding UDF (no downloads or provider calls). Insert the fixture and execute similarity retrieval with scores in descending order. Show the input remains stored and chunks are generated automatically. Record runnable commands and evidence.',
 'image-video': 'Build app.py declaring a video table and a frame view using the current video frame iterator. Generate a tiny local 2-second video with PyAV or ffmpeg, insert it, and verify automatically extracted frames and a computed resized image per frame. Reconstruct a video from frames in frame order using the Pixeltable aggregate. Do not install or call a vision model. Record runnable commands and evidence.',
 'audio': 'Build app.py declaring an audio table and an audio-split view using the current audio splitter. Generate a local 3-second WAV fixture with Python standard-library wave, use 1-second chunks, insert it, and verify chunk count, timestamps and valid audio output. No transcription model or provider calls. Record runnable commands and evidence.',
 'tool-calling': 'Demonstrate a stored Pixeltable tool-calling pipeline with a deterministic local tool that adds two integers, pxt.tools, and a supported provider invoke_tools adapter. Use a hand-built provider-shaped response fixture instead of making an LLM call, store it, compute tool output automatically on insert, and verify 2 + 3 returns 5. Use app.py declarative tables and current API signatures. Do not install heavy ML packages or call a provider. Record runnable commands and evidence.',
 'schema-evolution': 'Build app.py with a docs table (text String and a deterministic computed cleaned field). Apply it, insert text containing spaces, then change the existing computed expression to uppercase. Demonstrate what schema diff/update report and whether --allow-destructive permits the in-place expression change. Implement the supported migration without deleting the table or losing its stored text, verify the new computed result, and show a second diff is in sync. Record runnable commands and evidence.',
 'error-recovery': 'Build a Pixeltable notebook-style local pipeline with a stored computed UDF that deliberately fails for one row when a local marker file is absent. Insert two rows with on_error="ignore", inspect per-cell error type/message, create the marker file, and recompute only failed cells using the supported API. Verify both rows now have correct computed values and that the originally successful row was not recomputed. Record runnable commands and evidence.',
 'cloud-preparation': 'Prepare but DO NOT DEPLOY a Pixeltable Cloud app. Write app.py and a deployment.md runbook for the placeholder target pxt://exampleorg:evaldb. Include project configuration with an OpenAI secret binding, correct noninteractive provisioning/schema/service command order, API key setup, local versus hosted inspection, and authenticated hosted POST URL. Validate what can be checked locally without contacting Cloud. Do not use or request credentials; do not provision resources; clearly mark hosted behavior untested.'
}
COMMON = '''You are performing one independent Pixeltable application task. Work only in this fresh trial directory. Pixeltable 0.7.5 with serve dependencies is preinstalled. Python is {python}; pxt is on PATH. PIXELTABLE_HOME is already isolated for this trial. Use the supplied guidance as your starting point: read guidance/{entry}. You may follow its relative references and official documentation links. fetch_docs.py URL retrieves official documentation and records it. You may inspect installed package source and --help. Do not read other trial directories, the original skill repository, user memory, other installed skills, or other evaluation results. Do not install skills/MCP or modify global agent configuration. Setup dependencies are already supplied; focus on the requested task.

No paid provider calls, credentials, Cloud network operations, or large model downloads. Deterministic test fixtures and local services are allowed. Keep all scripts and outputs here. You have 240 seconds and at most 24 shell/tool calls; batch related checks. After testing, write result.json with fields: completed (boolean), checks (list of objects with name, passed, evidence), blockers (list), commands (list), documentation_urls (list). Do not claim unrun checks passed. Also summarize briefly in your final answer.

TASK: {task}
'''
FETCH = '''import sys,urllib.request,urllib.parse,json,pathlib,hashlib,datetime
url=sys.argv[1];host=urllib.parse.urlparse(url).hostname
assert host in {'pixeltable.com','www.pixeltable.com','docs.pixeltable.com','raw.githubusercontent.com','github.com'}, 'Official Pixeltable docs only'
if host in {'github.com','raw.githubusercontent.com'}: assert '/pixeltable/' in url
record={'url':url,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
try:
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'text/markdown,text/plain,*/*'})
 r=urllib.request.urlopen(req,timeout=20);b=r.read();record.update(status=r.status,sha256=hashlib.sha256(b).hexdigest());p=pathlib.Path('retrieved');p.mkdir(exist_ok=True);(p/(record['sha256']+'.txt')).write_bytes(b);print(b.decode(errors='replace'))
except Exception as e: record['error']=str(e);print(str(e))
with open('retrievals.jsonl','a') as f:f.write(json.dumps(record)+'\\n')
'''

def run_trial(spec):
 condition, scenario, repeat = spec
 trial_id=f'{scenario}__{condition}__{repeat}'
 trial=ROOT/'trials'/trial_id; trial.mkdir(parents=True,exist_ok=True)
 out=HERE/'trials'/trial_id;out.mkdir(parents=True,exist_ok=True)
 if (out/'execution.json').exists(): return json.loads((out/'execution.json').read_text())
 guidance=trial/'guidance';guidance.mkdir(exist_ok=True)
 if condition=='skill':
  shutil.copytree(REPO/'skills/pixeltable-skill',guidance,dirs_exist_ok=True);entry='SKILL.md'
 else:
  entry={'get-started':'get-started.md','llms':'llms.txt'}[condition]
  shutil.copy2(HERE/'evidence'/entry,guidance/entry)
 (trial/'fetch_docs.py').write_text(FETCH)
 prompt=COMMON.format(python=PYTHON,entry=entry,task=SCENARIOS[scenario]);(out/'prompt.txt').write_text(prompt)
 env={k:v for k,v in os.environ.items() if not k.startswith('CODEX_') and not any(x in k.upper() for x in ['API_KEY','ACCESS_KEY','SECRET','TOKEN','CREDENTIAL'])}
 env.update(PATH=str(PYTHON.parent)+os.pathsep+env.get('PATH',''),PIXELTABLE_HOME=str(trial/'catalog'),PIXELTABLE_ENABLE_TELEMETRY='false',PYTHONUNBUFFERED='1')
 args=['codex','exec','--ignore-user-config','--ignore-rules','--skip-git-repo-check','-C',str(trial),'--enable','skip_host_skill_discovery','--disable','plugins','--disable','hooks','--disable','memories','--disable','apps','--disable','multi_agent','-c','project_doc_max_bytes=0','-c','model_reasoning_effort="medium"','-c','approval_policy="never"','-s','danger-full-access','-m','gpt-6-astra','--json','-o',str(trial/'final.txt'),'-']
 start=time.monotonic();status='completed';calls=0
 with open(out/'events.jsonl','w') as stdout,open(out/'stderr.txt','w') as stderr:
  p=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=stdout,stderr=stderr,env=env,start_new_session=True,text=True)
  p.stdin.write(prompt);p.stdin.close()
  while p.poll() is None:
   time.sleep(1)
   calls=sum(1 for line in (out/'events.jsonl').read_text().splitlines() if '"type":"item.started"' in line and any(x in line for x in ['"command_execution"','"mcp_tool_call"','"web_search"']))
   if time.monotonic()-start>240 or calls>24:
    status='timeout' if time.monotonic()-start>240 else 'tool_limit';os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=5)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
    break
 result={'id':trial_id,'condition':condition,'scenario':scenario,'repeat':repeat,'status':status,'exit_code':p.returncode,'elapsed_seconds':round(time.monotonic()-start,2),'tool_calls':calls,'model':'gpt-6-astra','reasoning_effort':'medium','limit_seconds':240,'tool_limit':24,'command':args}
 for f in trial.rglob('*'):
  if f.is_file() and not any(x in f.relative_to(trial).parts for x in ['catalog','__pycache__','.git','guidance']) and f.stat().st_size<2_000_000:
   dest=out/'artifacts'/f.relative_to(trial);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
 (out/'execution.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ['id','status','elapsed_seconds','tool_calls']}),flush=True)
 return result

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=3);parser.add_argument('--limit',type=int);args=parser.parse_args()
 specs=[(c,s,r) for s in SCENARIOS for r in [1,2] for c in ['skill','get-started','llms']]
 (HERE/'evidence'/'trial-protocol.json').write_text(json.dumps({'scenarios':SCENARIOS,'conditions':['skill','get-started','llms'],'repetitions':2,'seconds':240,'tool_limit':24,'workers':args.workers,'model':'gpt-6-astra','reasoning':'medium'},indent=2))
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool: results=list(pool.map(run_trial,specs[:args.limit]))
 (HERE/'evidence'/'trial-executions.json').write_text(json.dumps(results,indent=2))
