import struct, sys, os

def parse_ad(path):
    d = open(path, 'rb').read()
    magic, ver = struct.unpack('>II', d[:8])
    assert magic == 0x00051607, hex(magic)
    n = struct.unpack('>H', d[24:26])[0]
    ents = {}
    for i in range(n):
        eid, off, ln = struct.unpack('>III', d[26+12*i:38+12*i])
        ents[eid] = d[off:off+ln]
    return ents

def parse_rsrc(r):
    if len(r) < 16: return {}
    doff, moff, dlen, mlen = struct.unpack('>IIII', r[:16])
    m = r[moff:moff+mlen]
    tl_off, nl_off = struct.unpack('>HH', m[24:28])
    tl = m[tl_off:]
    ntypes = struct.unpack('>H', tl[:2])[0] + 1
    out = {}
    for i in range(ntypes):
        t, cnt, ref = struct.unpack('>4sHH', tl[2+8*i:10+8*i])
        for j in range(cnt+1):
            rid, noff, attr_off = struct.unpack('>hHI', tl[ref+12*j:ref+12*j+8])
            doff_r = attr_off & 0xFFFFFF
            name = None
            if noff != 0xFFFF:
                p = nl_off + noff; ln = m[p]; name = m[p+1:p+1+ln].decode('mac_roman')
            p = doff + doff_r
            ln = struct.unpack('>I', r[p:p+4])[0]
            out.setdefault(t.decode('mac_roman'), []).append((rid, name, r[p+4:p+4+ln]))
    return out

if __name__ == '__main__':
    for path in sys.argv[1:]:
        e = parse_ad(path)
        fi = e.get(9, b'')
        tc = (fi[:4].decode('mac_roman','replace'), fi[4:8].decode('mac_roman','replace')) if fi else None
        try: rs = parse_rsrc(e.get(2, b''))
        except Exception as ex: rs = {'ERR': [str(ex)]}
        summ = {}
        for rid, name, data in rs.get('STR ', []):
            summ[name] = data[1:1+data[0]].decode('mac_roman')
        types = {k: len(v) for k, v in rs.items()}
        print(os.path.basename(path)[2:], 'ents', {k:len(v) for k,v in e.items()}, '| type/creator', tc, '| STR', summ, '| rsrc', types)
