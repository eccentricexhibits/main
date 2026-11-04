import sys, re, struct, json
d = open(sys.argv[1],'rb').read()
hdr = list(re.finditer(rb'(?s)\x00\x03\x00\x00\x00\x64(.{8})(.{2})\x00\x01\x00\x01([\x01-\x3f])', d))
hdr = [m for m in hdr if 0x3b200 < m.start() < 0x3c000]
rows = []
for i, m in enumerate(hdr):
    nl = m.group(3)[0]; name = d[m.end():m.end()+nl].decode('mac_roman')
    q = d.find(b'\x4d\x50\x27\x96', m.end(), m.end()+120)
    s1, s2, st = struct.unpack('>III', d[q+4:q+16])
    # trailing block belongs to this record: find next '00 00 00 LL 00 00 00 02' before next header
    nxt = hdr[i+1].start() if i+1 < len(hdr) else m.end()+0x200
    blk = None
    for k in range(nxt-4, q, -1):
        if d[k-3:k+1] == b'\x00\x04\x00\x05' and d[k+1:k+3]==b'\x00\x03' or (k==nxt-4):
            pass
    # simpler: the block sits right before '00 04 00 05 00 03 00 00 00 64' of next record
    e = d.rfind(b"\x00\x04\x00\x05\x00\x03\x00\x00\x00\x64", 0, nxt+6) if i+1 < len(hdr) else -1
    if e > 0 and e > m.start():
        tempo = struct.unpack('>I', d[e-4:e])[0]
        j = d.rfind(b'\x00\x00\x00\x02', e-20, e-8)
        LL = d[j-1]; start = struct.unpack('>I', d[j+4:j+8])[0]; T = d[j+8:e-4]
    else: tempo = 0; LL=0; start=None; T=b''
    rows.append(dict(id=int.from_bytes(m.group(2),'big'), name=name, length=struct.unpack('>Q', m.group(1))[0], sync=s1, start_field=st, blk_start=start, bpm=round(360e6/tempo,2) if tempo else None, LL=LL, T=T.hex()))
for r in rows: print(r)
json.dump(rows, open(sys.argv[2],'w'), indent=1)
