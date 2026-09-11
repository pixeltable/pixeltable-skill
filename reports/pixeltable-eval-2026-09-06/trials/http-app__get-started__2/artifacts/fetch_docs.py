import sys,urllib.request,urllib.parse,json,pathlib,hashlib,datetime
url=sys.argv[1];host=urllib.parse.urlparse(url).hostname
assert host in {'pixeltable.com','www.pixeltable.com','docs.pixeltable.com','raw.githubusercontent.com','github.com'}, 'Official Pixeltable docs only'
if host in {'github.com','raw.githubusercontent.com'}: assert '/pixeltable/' in url
record={'url':url,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
try:
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'text/markdown,text/plain,*/*'})
 r=urllib.request.urlopen(req,timeout=20);b=r.read();record.update(status=r.status,sha256=hashlib.sha256(b).hexdigest());p=pathlib.Path('retrieved');p.mkdir(exist_ok=True);(p/(record['sha256']+'.txt')).write_bytes(b);print(b.decode(errors='replace'))
except Exception as e: record['error']=str(e);print(str(e))
with open('retrievals.jsonl','a') as f:f.write(json.dumps(record)+'\n')
