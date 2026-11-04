import sys
d = open(sys.argv[1],'rb').read(); off = int(sys.argv[2],0); n = int(sys.argv[3],0)
for i in range(off, min(off+n, len(d)), 16):
    b = d[i:i+16]
    print(f'{i:08x}  ' + ' '.join(f'{x:02x}' for x in b).ljust(48) + '  ' + ''.join(chr(x) if 32<=x<127 else '.' for x in b))
