import sys, numpy as np, cv2
from PIL import Image
from rembg import remove, new_session
src,out=sys.argv[1],sys.argv[2]; x0,y0,x1,y1=map(int,sys.argv[3:7])
im=Image.open(src).convert("RGB"); W,H=im.size
c=im.crop((x0,y0,x1,y1))
a=np.asarray(remove(c,session=new_session("birefnet-general")).getchannel("A"))>128
n,lab,st,_=cv2.connectedComponentsWithStats(a.astype(np.uint8)); big=1+np.argmax(st[1:,4])
full=np.zeros((H,W),bool); full[y0:y1,x0:x1]=lab==big
np.save(out,full); print(out, full.sum())
