import os, sys
os.environ["PYOPENGL_PLATFORM"]="egl"
import numpy as np, trimesh, pyrender
from PIL import Image, ImageDraw
m=trimesh.load(sys.argv[1],process=False,force="mesh"); m.visual=trimesh.visual.ColorVisuals(m,vertex_colors=[205,205,210,255])
lo,hi=m.bounds; L=hi[1]-lo[1]
mesh=pyrender.Mesh.from_trimesh(m,smooth=False); r=pyrender.OffscreenRenderer(900,900)
def look(eye,tgt,up=(0,1,0)):
    eye=np.asarray(eye,float); tgt=np.asarray(tgt,float); f=tgt-eye; f/=np.linalg.norm(f); s=np.cross(f,up); s/=np.linalg.norm(s); u=np.cross(s,f)
    T=np.eye(4); T[:3,0],T[:3,1],T[:3,2],T[:3,3]=s,u,-f,eye; return T
shots=[("thumb side, lower half",(1,0,0),0.3,0.22),("little-finger side, lower half",(-1,0,0),0.3,0.22),
       ("cuff edge, front",(0,0.3,1),0.08,0.16),("hoof cleft, front",(0,0,1),0.8,0.14),("hoof, little-finger side",(-1,0,0),0.8,0.14),("cuff opening from below",(0,-1,0.001),0.0,0.3)]
tiles=[]
for name,d,fy,mag in shots:
    tgt=np.array([(lo[0]+hi[0])/2, lo[1]+fy*L, (lo[2]+hi[2])/2]); d=np.array(d,float); d/=np.linalg.norm(d)
    up=(0,0,1) if abs(d[1])>0.9 else (0,1,0)
    sc=pyrender.Scene(bg_color=[.12,.12,.12,1],ambient_light=[.15,.15,.15]); sc.add(mesh)
    sc.add(pyrender.OrthographicCamera(xmag=mag,ymag=mag,znear=.01,zfar=10),pose=look(tgt+d*3,tgt,up))
    side=np.cross(d,[0,1,0]) if abs(d[1])<0.9 else np.array([1.,0,0])
    sc.add(pyrender.DirectionalLight(intensity=4),pose=look(tgt+(d+0.8*side+0.5*np.array([0,1,0]))*3,tgt,(0,0,1) if abs(d[1])>0.9 else (0,1,0)))
    col,_=r.render(sc); im=Image.fromarray(col[...,:3]).resize((450,450)); ImageDraw.Draw(im).text((8,8),name,fill=(255,120,200)); tiles.append(im)
sheet=Image.new("RGB",(1350,900))
for i,t in enumerate(tiles): sheet.paste(t,((i%3)*450,(i//3)*450))
sheet.save(sys.argv[2],quality=90)
