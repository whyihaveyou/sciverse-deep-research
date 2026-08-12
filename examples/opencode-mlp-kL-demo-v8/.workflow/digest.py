import json, sys

for path in sys.argv[1:]:
    print("="*70)
    print("FILE:", path)
    try:
        txt=open(path).read()
    except Exception as e:
        print("ERR", e); continue
    i=txt.find('{')
    if i<0:
        print("no json"); continue
    data=json.loads(txt[i:])
    if 'hits' in data:
        res=data['hits']
        for h in res:
            ab=(h.get('abstract') or '')
            import re
            ab=re.sub('<[^>]+>',' ',ab)
            print("SEM|", h.get('citation_count','-'), "|", h.get('publication_published_year',''), "|", (h.get('author') or '')[:40], "|", h.get('publication_venue_name_unified','')[:40])
            print("   T>", (h.get('title') or '')[:130])
            print("   D>", h.get('doc_id','')[:26])
    else:
        res=data.get('results',[])
        seen=set()
        for r in res:
            mt=r.get('metadata_type','')
            if mt not in ('papers','paper'):
                continue
            uid=r.get('unique_id','')
            t=r.get('title','')
            aus=", ".join(a.get('name','') for a in (r.get('author') or [])[:3])
            print("P|", r.get('metadata_type',''), "|", r.get('publication_published_year',''), "|", aus[:50], "|", r.get('publication_venue_name_unified','')[:42])
            print("   U>", uid)
            print("   T>", t[:130])
