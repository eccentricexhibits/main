import sys, os, numpy as np, wave
sys.path.insert(0, sys.argv[3]); from unmix import load, unmix
B, OUT = sys.argv[1], sys.argv[2]; AF = B+'/DrasticMeasures-NewSong Project/Audio Files/'; SEL = B+'/DrasticMeasures-Selections/'
def write(path, x):
    y = np.clip(np.round(x*32768), -32768, 32767).astype('<i2')
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(44100); w.writeframes(y.tobytes())
os.makedirs(OUT, exist_ok=True)
for song, mixf, voxf, start in (("I Believe", "I Believe.wav", "vox-IBelieve-9", 16860-76327), ("30's German Nightclub", "30'sGermanNightclub", "vox--11", -117228)):
    mix = load(SEL+mixf, 2); _, est, v = unmix(mix, load(AF+voxf,1)[:,0], start)
    # sanity: the modelled vocal must line up with the mix (correlation at lag 0 vs +-50 ms)
    c0 = np.corrcoef(est[:,0], mix[:,0])[0,1]; c1 = np.corrcoef(np.roll(est[:,0], 2205), mix[:,0])[0,1]
    print(f'{song}: modelled-vocal/mix correlation at alignment {c0:.3f} vs 50 ms off {c1:.3f}')
    for db in (+3, -3):
        g = 10**(db/20) - 1        # scale applied to the coherent vocal component
        out = mix + g*est
        print(f'   vocal {db:+d} dB: peak {20*np.log10(np.abs(out).max()):.2f} dBFS')
        write(os.path.join(OUT, f"{song} (vocal {'up' if db>0 else 'down'} 3 dB).wav"), out)
