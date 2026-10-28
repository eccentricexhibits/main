# Original demo song for Patchbay: 16 bars, 104 BPM, A minor. Format 1 SMF.
import struct, base64, sys
TPB = 480
def vlq(n):
    out = [n & 0x7F]; n >>= 7
    while n: out.append((n & 0x7F) | 0x80); n >>= 7
    return bytes(reversed(out))
def track(events, name):
    # events: list of (tick, bytes)
    ev = [(0, b'\xff\x03' + vlq(len(name)) + name.encode())] + events
    ev.sort(key=lambda e: (e[0], 0 if e[1][0] & 0xF0 == 0x80 else 1))
    data = b''; last = 0
    for t, b in ev:
        data += vlq(t - last) + b; last = t
    data += vlq(0) + b'\xff\x2f\x00'
    return b'MTrk' + struct.pack('>I', len(data)) + data
def note(evs, ch, t, dur, key, vel):
    evs.append((t, bytes([0x90 | ch, key, vel])))
    evs.append((t + dur, bytes([0x80 | ch, key, 0])))
def prog(ch, p): return (0, bytes([0xC0 | ch, p]))
def cc(ch, t, c, v): return (t, bytes([0xB0 | ch, c, v]))
BAR = TPB * 4; BARS = 16
# Am - F - C - G, twice; then Dm - F - Am - E, then Am F C G
chords = [
 ('A',[57,60,64]),('F',[53,57,60]),('C',[52,55,60]),('G',[55,59,62]),
 ('A',[57,60,64]),('F',[53,57,60]),('C',[52,55,60]),('G',[55,59,62]),
 ('D',[50,53,57]),('F',[53,57,60]),('A',[52,57,60]),('E',[52,56,59]),
 ('A',[57,60,64]),('F',[53,57,60]),('C',[52,55,60]),('G',[55,59,62]),
]
roots = {'A':45,'F':41,'C':48,'G':43,'D':38,'E':40}
conductor = [(0, b'\xff\x51\x03' + (60000000 // 104).to_bytes(3, 'big')),
             (0, b'\xff\x58\x04\x04\x02\x18\x08')]
piano=[prog(0,0),cc(0,0,7,100),cc(0,0,10,54),cc(0,0,91,50)]
strings=[prog(1,48),cc(1,0,7,78),cc(1,0,10,76),cc(1,0,91,80)]
bass=[prog(2,33),cc(2,0,7,108),cc(2,0,10,64),cc(2,0,91,20)]
pad=[prog(3,89),cc(3,0,7,64),cc(3,0,10,40),cc(3,0,91,90)]
lead=[prog(4,81),cc(4,0,7,82),cc(4,0,10,88),cc(4,0,91,60)]
drums=[cc(9,0,7,104),cc(9,0,91,30)]
for i,(r,ch) in enumerate(chords):
    t0 = i*BAR
    # piano: broken-chord eighths
    pat = [0,1,2,1,0,1,2,1]
    for k,idx in enumerate(pat):
        n = ch[idx] + (12 if k in (2,6) else 0)
        note(piano,0,t0+k*TPB//2,TPB//2-20,n,84 if k%2==0 else 68)
    # strings enter bar 5
    if i>=4:
        for n in ch: note(strings,1,t0,BAR-10,n+12,70)
    # pad whole song, low
    for n in ch: note(pad,3,t0,BAR-10,n,56)
    # bass: root pattern
    root = roots[r]
    for k,(off,dur,d) in enumerate([(0,TPB*3//2,0),(TPB*3//2,TPB//2,0),(TPB*2,TPB,7),(TPB*3,TPB,12)]):
        if i>=2: note(bass,2,t0+off,dur-20,root+d,96 if k==0 else 80)
    # drums from bar 3
    if i>=2:
        for b in range(4):
            note(drums,9,t0+b*TPB,TPB//4,36 if b in (0,2) else 38,110 if b in (0,2) else 96)
            for e in range(2):
                note(drums,9,t0+b*TPB+e*TPB//2,TPB//4,42,80 if e==0 else 60)
        if i%4==3: note(drums,9,t0+BAR-TPB//2,TPB//4,46,90)
        if i in (8,12): note(drums,9,t0,TPB,49,100)
melody = { # bar: [(beat_in_eighths, len_in_eighths, key)]
 8:[(0,2,69),(2,2,72),(4,3,74),(7,1,72)], 9:[(0,3,69),(3,1,72),(4,4,77)],
 10:[(0,2,76),(2,2,72),(4,2,69),(6,2,72)], 11:[(0,6,71),(6,2,68)],
 12:[(0,2,69),(2,2,72),(4,3,76),(7,1,74)], 13:[(0,3,72),(3,1,74),(4,4,77)],
 14:[(0,2,76),(2,2,74),(4,2,72),(6,2,67)], 15:[(0,8,69)],
}
for bar,ns in melody.items():
    for s,l,k in ns: note(lead,4,bar*BAR+s*TPB//2,l*TPB//2-30,k,92)
# final chord
END = BARS*BAR
note(piano,0,END,BAR*2,45,90); note(piano,0,END,BAR*2,57,80); note(piano,0,END,BAR*2,64,76)
note(strings,1,END,BAR*2,69,70); note(strings,1,END,BAR*2,72,70); note(strings,1,END,BAR*2,76,70)
note(bass,2,END,BAR*2,33,96); note(drums,9,END,TPB,49,110); note(drums,9,END,TPB,36,110)
note(pad,3,END,BAR*2,57,56); note(pad,3,END,BAR*2,64,56)
tracks=[track(conductor,'Night Drive (Patchbay demo)'),track(piano,'Piano'),track(strings,'Strings'),
        track(bass,'Bass'),track(pad,'Warm Pad'),track(lead,'Lead Synth'),track(drums,'Drums')]
smf=b'MThd'+struct.pack('>IHHH',6,1,len(tracks),TPB)+b''.join(tracks)
open(sys.argv[1],'wb').write(smf)
print(len(smf), base64.b64encode(smf).decode()[:60])
