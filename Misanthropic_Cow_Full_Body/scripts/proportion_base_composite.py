"""Proportion base: body from shoot 4 (standing front) + head from shoot 3 (same session/camera), on white."""
import sys, os, numpy as np, cv2
from PIL import Image, ImageOps
O, OUT = sys.argv[1], sys.argv[2]
def load(i): return np.asarray(ImageOps.exif_transpose(Image.open(f"{O}/Cow - Original Photo Shoot ({i} of 8).jpg")).convert('RGB')).astype(np.float32)
def wb(a, box, target=232):
    H,W,_ = a.shape; x0,y0,x1,y1 = box
    m = np.median(a[int(y0*H):int(y1*H), int(x0*W):int(x1*W)].reshape(-1,3),0)
    return np.clip(a*(target/m),0,255)
def lab(a): return cv2.cvtColor((a/255).astype(np.float32), cv2.COLOR_RGB2LAB)
def bg_field(L, bg_boxes, deg=3):
    H,W,_ = L.shape; pts=[]; vals=[]
    for x0,y0,x1,y1 in bg_boxes:
        ys,xs = np.mgrid[int(y0*H):int(y1*H):12, int(x0*W):int(x1*W):12]
        pts.append(np.c_[xs.ravel()/W, ys.ravel()/H]); vals.append(L[ys.ravel(), xs.ravel()])
    P = np.vstack(pts); V = np.vstack(vals)
    def feats(x,y): return np.stack([x**i*y**j for i in range(deg+1) for j in range(deg+1-i)],-1)
    A = feats(P[:,0],P[:,1]); coef,*_ = np.linalg.lstsq(A, V, rcond=None)
    Y,X = np.mgrid[0:H,0:W]; F = feats(X/W, Y/H) @ coef
    return F
def segment(a, bg_boxes, fg_boxes, keep_box, t_bg=9, t_fg=22, scale=0.5):
    L = lab(a); F = bg_field(L, bg_boxes); d = np.linalg.norm(L-F, axis=2)
    H,W,_ = a.shape
    mask = np.full((H,W), cv2.GC_PR_FGD, np.uint8)
    mask[d<t_fg] = cv2.GC_PR_BGD; mask[d<t_bg] = cv2.GC_BGD
    for x0,y0,x1,y1 in fg_boxes: mask[int(y0*H):int(y1*H), int(x0*W):int(x1*W)] = cv2.GC_FGD
    x0,y0,x1,y1 = keep_box; out = np.ones((H,W),bool); out[int(y0*H):int(y1*H), int(x0*W):int(x1*W)] = False; mask[out] = cv2.GC_BGD
    sm = cv2.resize(mask, (int(W*scale), int(H*scale)), interpolation=cv2.INTER_NEAREST)
    si = cv2.resize(a.astype(np.uint8), (int(W*scale), int(H*scale)), interpolation=cv2.INTER_AREA)
    bgd = np.zeros((1,65)); fgd = np.zeros((1,65))
    cv2.grabCut(cv2.cvtColor(si, cv2.COLOR_RGB2BGR), sm, None, bgd, fgd, 5, cv2.GC_INIT_WITH_MASK)
    m = ((sm==cv2.GC_FGD)|(sm==cv2.GC_PR_FGD)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5,5),np.uint8))
    n, lab_, st, _ = cv2.connectedComponentsWithStats(m)
    if n>1: m = (lab_==1+np.argmax(st[1:,cv2.CC_STAT_AREA])).astype(np.uint8)
    # fill holes
    inv = (1-m).astype(np.uint8); n, lab_, st, _ = cv2.connectedComponentsWithStats(inv)
    for k in range(1,n):
        x,y,w,h,area = st[k]
        if x>0 and y>0 and x+w<m.shape[1] and y+h<m.shape[0] and area < 0.01*m.size: m[lab_==k]=1
    m = cv2.resize(m.astype(np.float32), (W,H)); m = cv2.GaussianBlur(m,(0,0),1.2)
    return np.clip(m,0,1), d

b = wb(load(4), (0.19,0.27,0.24,0.33))
H,W,_ = b.shape
bm, d4 = segment(b,
    bg_boxes=[(0.62,0.0,1.0,0.88),(0.0,0.24,0.13,0.80),(0.53,0.20,0.62,0.80),(0.32,0.62,0.36,0.80),(0.0,0.0,0.03,0.25)],
    fg_boxes=[(0.24,0.03,0.48,0.33),(0.21,0.45,0.29,0.78),(0.39,0.45,0.46,0.78),(0.20,0.36,0.46,0.42),(0.17,0.84,0.29,0.90),(0.37,0.82,0.48,0.88)],
    keep_box=(0.0,0.0,0.62,0.93))
Y,X = np.mgrid[0:H,0:W]/np.array([H,W]).reshape(2,1,1)
arms = ((X<0.152)&(Y<0.235)) | ((X>0.507)&(Y<0.16)) | ((X>0.28)&(X<0.40)&(Y<0.012))
bm = bm*(1-cv2.GaussianBlur(arms.astype(np.float32),(0,0),3))

h3 = wb(load(3), (0.48,0.125,0.54,0.145))
hm, _ = segment(h3,
    bg_boxes=[(0.0,0.0,0.36,0.30),(0.76,0.0,1.0,0.30),(0.36,0.0,0.76,0.09)],
    fg_boxes=[(0.47,0.16,0.57,0.27),(0.46,0.13,0.56,0.15)],
    keep_box=(0.36,0.09,0.76,0.31))
s = 0.91
h3s = cv2.resize(h3, None, fx=s, fy=s, interpolation=cv2.INTER_AREA); hms = cv2.resize(hm, None, fx=s, fy=s)
top = 560; CH, CW = H+top, W
canvas = np.full((CH,CW,3), 255, np.float32)
canvas[top:] = b*bm[...,None] + 255*(1-bm[...,None])
dx = int(0.355*W - 0.54*W*s); dy = int(top + 0.025*H - 0.30*H*s) + 25
hh, hw = hms.shape
ys0, xs0 = max(0,dy), max(0,dx); ys1, xs1 = min(CH, dy+hh), min(CW, dx+hw)
sm = hms[ys0-dy:ys1-dy, xs0-dx:xs1-dx][...,None]; sub = h3s[ys0-dy:ys1-dy, xs0-dx:xs1-dx]
canvas[ys0:ys1, xs0:xs1] = sub*sm + canvas[ys0:ys1, xs0:xs1]*(1-sm)
im = Image.fromarray(canvas.astype(np.uint8))
a = np.asarray(im).astype(int); ys,xs = np.where((a<235).any(2))
im = im.crop((max(xs.min()-80,0), max(ys.min()-60,0), min(xs.max()+80,CW), min(ys.max()+40,CH)))
im.save(os.path.join(OUT,"composite_raw.png")); print(im.size)
Image.fromarray((bm*255).astype(np.uint8)).resize((W//4,H//4)).save(os.path.join(OUT,"mask4.png"))

# --- despill: magenta backdrop fringe near the cut edge -> white ---
a = np.asarray(im).astype(np.float32)
hsv = cv2.cvtColor(a.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
white = (a>245).all(2).astype(np.uint8)
near = cv2.dilate(white, np.ones((13,13),np.uint8)).astype(bool)
mag = (hsv[...,0]>140)&(hsv[...,0]<178)&(hsv[...,1]>45)&(hsv[...,2]>90)
a[near & mag] = 255
im2 = Image.fromarray(a.astype(np.uint8))
# 2:3 portrait, figure ~86% of height, centred, white
Wc, Hc = 1024, 1536
sc = Hc*0.86/im2.height
fig = im2.resize((round(im2.width*sc), round(im2.height*sc)), Image.LANCZOS)
can = Image.new("RGB",(Wc,Hc),(255,255,255)); can.paste(fig, ((Wc-fig.width)//2, int(Hc*0.95)-fig.height))
can.save(os.path.join(OUT,"PROPORTION_BASE_original_wearer.png"))
print("fig", fig.size)
