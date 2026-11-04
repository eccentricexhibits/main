import sys, numpy as np, hashlib
B = sys.argv[1]; OUT = sys.argv[2]
A = B+'/DrasticMeasures-NewSong Project/Audio Files/'
sel = np.frombuffer(open(B+'/DrasticMeasures-Selections/Baby Dolls','rb').read(), '>i2').reshape(-1,2)
for c, side in enumerate('LR'):
    orig = np.frombuffer(open(A+f'Baby Dolls.{side}','rb').read(), '>i2')
    fixed = np.ascontiguousarray(sel[:,c]).astype('>i2')
    assert len(fixed) == len(orig)
    changed = np.sum(fixed != orig)
    blk = np.arange(131071, len(fixed), 131072)
    print(f'Baby Dolls.{side}: {changed} samples replaced; zeros at block ends before={int(np.sum(orig[blk]==0))} after={int(np.sum(fixed[blk]==0))}')
    open(OUT+f'/Baby Dolls.{side}','wb').write(fixed.tobytes())
    print('  md5', hashlib.md5(fixed.tobytes()).hexdigest())
