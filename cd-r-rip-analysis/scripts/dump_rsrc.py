import sys, re
sys.path.insert(0, sys.argv[1]); from appledouble import parse_ad, parse_rsrc
r = parse_rsrc(parse_ad(sys.argv[2])[2])
for t, items in r.items():
    if t in ('STR ','colm'): continue
    for rid, name, data in items:
        strs = [s.decode('mac_roman') for s in re.findall(rb'[\x20-\x7e\x80-\xff]{4,}', data)]
        print(t, rid, repr(name), len(data), strs[:8])
