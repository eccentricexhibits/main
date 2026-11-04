#!/bin/bash
# usage: remaster.sh in.wav out.wav   (target -14 LUFS integrated, -1 dBTP)
in="$1"; out="$2"; T=-14
meas(){ ffmpeg -nostdin -hide_banner -i "$1" -af loudnorm=I=$T:TP=-1:print_format=json -f null - 2>&1 | python3 -I -c 'import sys,json; t=sys.stdin.read(); j=json.loads(t[t.rindex("{"):]); print(j["input_i"], j["input_tp"])'; }
read I TP < <(meas "$in")
g=$(python3 -I -c "print(round($T - $I, 2))")
render(){ ffmpeg -nostdin -loglevel error -y -i "$in" -af "highpass=f=20:poles=2,volume=${1}dB,aresample=176400,alimiter=limit=0.871:attack=1:release=60:level=disabled:asc=1,aresample=44100:dither_method=triangular" -c:a pcm_s16le "$out"; }
render $g
read I2 TP2 < <(meas "$out")
# limiting can pull loudness down slightly: one correction pass
g2=$(python3 -I -c "print(round($g + ($T - $I2), 2))")
if python3 -I -c "import sys; sys.exit(0 if abs($T - $I2) > 0.2 else 1)"; then render $g2; read I2 TP2 < <(meas "$out"); g=$g2; fi
printf '%-45s in %6.2f LUFS %6.2f dBTP | gain %+5.2f dB | out %6.2f LUFS %6.2f dBTP\n' "$(basename "$in")" $I $TP $g $I2 $TP2
