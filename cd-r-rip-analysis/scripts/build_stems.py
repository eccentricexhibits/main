import sys, os, numpy as np, wave
B, OUT = sys.argv[1], sys.argv[2]; AF = B+'/DrasticMeasures-NewSong Project/Audio Files/'; SEL = B+'/DrasticMeasures-Selections/'
SR = 44100
def load(p, ch): return np.frombuffer(open(p,'rb').read(), '>i2').reshape(-1, ch)
def write(path, x):
    if x.ndim == 1: x = x[:, None]
    with wave.open(path, 'wb') as w:
        w.setnchannels(x.shape[1]); w.setsampwidth(2); w.setframerate(SR); w.writeframes(x.astype('<i2').tobytes())
songs = {
  "I Believe": [("00 Full mix (CD master)", SEL+"I Believe.wav", 2, 0, "time stamps + audio, exact"),
                ("01 Lead vocal - take 9 (the one in the mix)", AF+"vox-IBelieve-9", 1, 16860-76327, "time stamps + audio, sample-exact"),
                ("02 Alternate vocal - take 8 (not in the mix)", AF+"vox-IBelieve-8", 1, int(round(-5.18*SR)), "audio alignment vs mix and take 9, +-10 ms")],
  "30's German Nightclub": [("00 Full mix (CD master)", SEL+"30'sGermanNightclub", 2, 0, "exact"),
                ("01 Lead vocal - vox-11 (the one in the mix)", AF+"vox--11", 1, -117228, "time stamps + audio, sample-exact"),
                ("02 Alternate opening line - vox-10", AF+"vox--10", 1, int(round(0.60*SR)), "audio alignment vs mix, +-10 ms")],
}
for song, parts in songs.items():
    d = os.path.join(OUT, f'{song} - aligned stems'); os.makedirs(d, exist_ok=True)
    origin = min(off for *_, off, _ in parts); end = max(off + len(load(p, ch)) for _, p, ch, off, _ in parts)
    n = end - origin
    lines = [f'{song}: all files start at the same instant and have the same length ({n/SR:.2f} s). Import them at 0 in any DAW.', '']
    for name, p, ch, off, how in parts:
        x = load(p, ch); y = np.zeros((n, ch), np.int16); s = off - origin; y[s:s+len(x)] = x
        write(os.path.join(d, name + '.wav'), y if ch == 2 else y[:, 0])
        lines.append(f'{name}: starts {s/SR:7.3f} s into the timeline (offset vs mix {off/SR:+.3f} s) - placement from {how}')
    open(os.path.join(d, 'README.txt'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
