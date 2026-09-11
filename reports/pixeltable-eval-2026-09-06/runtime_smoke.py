"""Run with isolated PIXELTABLE_HOME and Pixeltable 0.7.5; no provider calls."""
import json, os, pathlib, re, subprocess, sys, time, traceback, wave
import numpy as np
import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.serving import FastAPIRouter
from fastapi import FastAPI
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parent
WORK=pathlib.Path('/private/tmp/pxt-skill-eval-20260906/runtime-project')
WORK.mkdir(exist_ok=True)
results=[]
def test(name, fn):
    start=time.monotonic()
    try: results.append(dict(name=name,status='pass',detail=fn(),elapsed=time.monotonic()-start))
    except Exception as e: results.append(dict(name=name,status='error',error=repr(e),traceback=traceback.format_exc(),elapsed=time.monotonic()-start))
    print(json.dumps(results[-1],default=str),flush=True)
def cli(*args):
    r=subprocess.run([str(pathlib.Path(sys.executable).parent/'pxt'),*args],cwd=WORK,text=True,capture_output=True)
    return dict(args=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
def setup():
    pxt.create_dir('runtime_eval',if_exists='ignore')
    return pxt.__version__
test('initialize',setup)
# Exact main application example extracted from tracked skill.
skill=(ROOT.parents[1]/'skills/pixeltable-skill/SKILL.md').read_text()
app=re.search(r'```python\n(import pixeltable as pxt\nimport pixeltable.functions as pxtf.*?)```',skill,re.S).group(1)
(WORK/'app.py').write_text(app)
sys.path.insert(0,str(WORK))
test('cli_init',lambda:cli('init','--help'))
test('cli_schema_check',lambda:cli('schema','check','app.py'))
test('cli_schema_update',lambda:cli('schema','update','app.py','runtime_eval'))
def http():
    import app as example
    example.ingest.bind('runtime_eval')
    api=FastAPI(); api.include_router(example.ingest)
    with TestClient(api) as c:
        a=c.post('/docs',json={'doc_id':1,'title':'Pixeltable runtime evaluation','body':None})
        b=c.post('/titles',json={'title':'hello'})
        assert a.status_code==200,(a.status_code,a.text)
        assert b.status_code==200,(b.status_code,b.text)
        return {'insert':a.json(),'compute':b.json(),'rows':pxt.get_table('runtime_eval.docs').count()}
test('main_example_http_post',http)
def bad_update():
    import app as example
    try: FastAPIRouter(name='bad').add_update_route(example.Docs,path='/update',match_columns=['doc_id'])
    except TypeError as e: return {'expected_rejection':str(e)}
    raise AssertionError('unexpected acceptance')
test('update_route_match_columns_rejection',bad_update)
def list_untyped():
    from pixeltable.functions.json import list_iterator
    t=pxt.create_table('runtime_eval.tags',{'tags':pxt.Json},if_exists='ignore')
    try: pxt.create_view('runtime_eval.items',t,iterator=list_iterator(t.tags),if_exists='ignore')
    except Exception as e: return {'expected_rejection':str(e)}
    raise AssertionError('unexpected acceptance')
test('list_iterator_untyped_rejection',list_untyped)
@pxt.udf
def deterministic_embed(text:str)->pxt.Array[(3,),pxt.Float]:
    return np.array([float(text.count('cat')),float(text.count('dog')),1.],dtype=np.float32)
def embedding():
    t=pxt.create_table('runtime_eval.search',{'body':pxt.String},if_exists='ignore')
    t.add_embedding_index('body',embedding=deterministic_embed.using(),if_exists='ignore')
    t.insert([{'body':'cat cat'},{'body':'dog dog'}])
    sim=t.body.similarity(string='cat')
    rows=t.select(t.body,score=sim).order_by(sim,asc=False).collect().to_dicts()
    assert rows[0]['body']=='cat cat',rows
    return rows
test('local_embedding_and_similarity',embedding)
@pxt.udf
def unstable(value:int)->int:
    if not (WORK/'allow-recompute').exists(): raise ValueError('intentional evaluation fixture failure')
    return value*2
def recovery():
    t=pxt.create_table('runtime_eval.failures',{'value':pxt.Int},if_exists='ignore')
    t.add_computed_column(summary=unstable(t.value),if_exists='ignore')
    t.insert(value=4,on_error='ignore')
    before=t.select(t.summary.errortype,t.summary.errormsg).collect().to_dicts()
    (WORK/'allow-recompute').write_text('yes')
    status=t.recompute_columns('summary',errors_only=True)
    after=t.select(t.summary).collect().to_dicts()
    assert after[0]['summary']==8,after
    return {'before':before,'after':after,'status':str(status)}
test('errors_only_recompute',recovery)
def audio():
    from pixeltable.functions.audio import audio_splitter
    path=WORK/'tone.wav'
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000);w.writeframes(np.zeros(16000*2,dtype=np.int16).tobytes())
    t=pxt.create_table('runtime_eval.audio_input',{'audio':pxt.Audio},if_exists='ignore')
    v=pxt.create_view('runtime_eval.audio_segments',t,iterator=audio_splitter(audio=t.audio,duration=1.0),if_exists='ignore')
    t.insert(audio=str(path))
    return v.select(v.pos,v.segment_start,v.segment_end).collect().to_dicts()
test('audio_splitter_fixture',audio)
def video():
    import av
    from pixeltable.functions.video import frame_iterator
    path=WORK/'video.mp4'
    with av.open(str(path),'w') as out:
        stream=out.add_stream('mpeg4',rate=2);stream.width=32;stream.height=32;stream.pix_fmt='yuv420p'
        for i in range(4):
            f=av.VideoFrame.from_ndarray(np.full((32,32,3),i*40,dtype=np.uint8),format='rgb24')
            for packet in stream.encode(f):out.mux(packet)
        for packet in stream.encode():out.mux(packet)
    t=pxt.create_table('runtime_eval.video_input',{'video':pxt.Video},if_exists='ignore')
    v=pxt.create_view('runtime_eval.frames',t,iterator=frame_iterator(t.video,fps=1.0),if_exists='ignore')
    t.insert(video=str(path))
    return v.select(v.pos,time=v.frame_attrs.time).collect().to_dicts()
test('frame_iterator_fixture',video)
def document():
    from pixeltable.functions.document import document_splitter
    path=WORK/'document.txt';path.write_text('Pixeltable is a table.\n\nComputed columns process rows.')
    t=pxt.create_table('runtime_eval.document_input',{'doc':pxt.Document},if_exists='ignore')
    v=pxt.create_view('runtime_eval.chunks',t,iterator=document_splitter(t.doc,separators='token_limit',limit=300),if_exists='ignore')
    t.insert(doc=str(path))
    return v.select(v.text).collect().to_dicts()
test('document_token_limit_fixture',document)
def migration():
    (WORK/'changed.py').write_text(app.replace('pxtf.string.upper(title)','pxtf.string.lower(title)'))
    return cli('schema','update','changed.py','runtime_eval','--allow-destructive','-f')
test('computed_expression_migration',migration)
(ROOT/'evidence/runtime-results.json').write_text(json.dumps(results,indent=2,default=str))
