// Software rasterizer used for review renders and the dance video.
// Orthographic projection; positions arrive already in camera space (x right, y up, z toward viewer).
#include <algorithm>
#include <cmath>
#include <cstdint>
static inline void nrm(float*n){float l=std::sqrt(n[0]*n[0]+n[1]*n[1]+n[2]*n[2]);if(l<1e-12f)l=1e-12f;for(int j=0;j<3;j++)n[j]/=l;}
static inline float dot3(const float*a,const float*b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
static void sample(const uint8_t*im,int w,int h,float u,float v,float*out){
 if(w==0){out[0]=out[1]=out[2]=1;return;}
 u-=std::floor(u);v-=std::floor(v);
 float x=u*w-.5f,y=v*h-.5f;int a=(int)std::floor(x),b=(int)std::floor(y);float fx=x-a,fy=y-b;
 int a1=((a%w)+w)%w,b1=((b%h)+h)%h,c1=(a1+1)%w,d1=(b1+1)%h;
 for(int j=0;j<3;j++)out[j]=((1-fy)*((1-fx)*im[(b1*w+a1)*3+j]+fx*im[(b1*w+c1)*3+j])+fy*((1-fx)*im[(d1*w+a1)*3+j]+fx*im[(d1*w+c1)*3+j]))/255.f;
}
extern "C" void raster(int nv,const float*pos,const float*normal,const float*uv,const float*uvn,const float*ao,
 int nf,const int32_t*faces,int w,int h,float scale,float cx,float cy,
 const uint8_t*tex,int tw,int th,const uint8_t*ntex,int nw,int nh,float nscale,
 const float*factor,float rough,float sheen,int clay,float*depth,float*rgb){
 const float key[3]={-.42f,.58f,.70f},fill[3]={.72f,.12f,.68f},rim[3]={.2f,.35f,-.9f};
 float kn[3]={key[0],key[1],key[2]},fn[3]={fill[0],fill[1],fill[2]},rn[3]={rim[0],rim[1],rim[2]};nrm(kn);nrm(fn);nrm(rn);
 for(int k=0;k<nf;k++){
  int id[3]={faces[k*3],faces[k*3+1],faces[k*3+2]};float sx[3],sy[3];
  for(int j=0;j<3;j++){sx[j]=cx+pos[id[j]*3]*scale;sy[j]=cy-pos[id[j]*3+1]*scale;}
  float det=(sy[1]-sy[2])*(sx[0]-sx[2])+(sx[2]-sx[1])*(sy[0]-sy[2]);if(std::fabs(det)<1e-9f)continue;
  int x0=std::max(0,(int)std::floor(std::min({sx[0],sx[1],sx[2]}))),x1=std::min(w-1,(int)std::ceil(std::max({sx[0],sx[1],sx[2]})));
  int y0=std::max(0,(int)std::floor(std::min({sy[0],sy[1],sy[2]}))),y1=std::min(h-1,(int)std::ceil(std::max({sy[0],sy[1],sy[2]})));
  if(x0>x1||y0>y1)continue;
  float T[3]={1,0,0},B[3]={0,1,0};bool hasT=false;
  if(nw&&uvn){float du1=uvn[id[1]*2]-uvn[id[0]*2],dv1=uvn[id[1]*2+1]-uvn[id[0]*2+1],du2=uvn[id[2]*2]-uvn[id[0]*2],dv2=uvn[id[2]*2+1]-uvn[id[0]*2+1],ud=du1*dv2-du2*dv1;
   if(std::fabs(ud)>1e-14f){for(int j=0;j<3;j++){float e1=pos[id[1]*3+j]-pos[id[0]*3+j],e2=pos[id[2]*3+j]-pos[id[0]*3+j];T[j]=(e1*dv2-e2*dv1)/ud;B[j]=(e2*du1-e1*du2)/ud;}nrm(T);nrm(B);hasT=true;}}
  for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++){
   float a=((sy[1]-sy[2])*(x+.5f-sx[2])+(sx[2]-sx[1])*(y+.5f-sy[2]))/det,b=((sy[2]-sy[0])*(x+.5f-sx[2])+(sx[0]-sx[2])*(y+.5f-sy[2]))/det,c=1-a-b;
   if(a<0||b<0||c<0)continue;
   float bc[3]={a,b,c},z=0;for(int i=0;i<3;i++)z+=bc[i]*pos[id[i]*3+2];
   int at=y*w+x;if(z<=depth[at])continue;depth[at]=z;
   float N[3]={0,0,0},U[2]={0,0},UN[2]={0,0},A=0;
   for(int i=0;i<3;i++){int q=id[i];A+=bc[i]*(ao?ao[q]:1.f);for(int j=0;j<3;j++)N[j]+=bc[i]*normal[q*3+j];if(uv)for(int j=0;j<2;j++)U[j]+=bc[i]*uv[q*2+j];if(uvn)for(int j=0;j<2;j++)UN[j]+=bc[i]*uvn[q*2+j];}
   nrm(N);if(N[2]<0){for(int j=0;j<3;j++)N[j]=-N[j];}
   if(hasT&&!clay){float tn[3];sample(ntex,nw,nh,UN[0],UN[1],tn);tn[0]=(tn[0]*2-1)*nscale;tn[1]=(tn[1]*2-1)*nscale;tn[2]=tn[2]*2-1;float o[3];for(int j=0;j<3;j++)o[j]=N[j]*tn[2]+T[j]*tn[0]+B[j]*tn[1];nrm(o);if(o[2]>0)for(int j=0;j<3;j++)N[j]=o[j];}
   float base[3]={1,1,1};if(tw&&uv&&!clay)sample(tex,tw,th,U[0],U[1],base);
   float ka=std::max(0.f,dot3(N,kn)),fb=std::max(0.f,dot3(N,fn)),rb=std::pow(std::max(0.f,1-std::fabs(N[2])),2.f)*std::max(0.f,N[1]*.5f+.5f);
   float sh=.20f+.78f*ka+.22f*fb;
   float hv[3]={kn[0],kn[1],kn[2]+1};nrm(hv);float spec=std::pow(std::max(0.f,dot3(N,hv)),10+110*(1-rough))*(1-rough)*.35f;
   float fuzz=sheen*rb*.55f;
   for(int j=0;j<3;j++){float col=clay?(j==0?.80f:j==1?.776f:.73f):base[j]*factor[j];
    float lin=std::pow(std::max(col,0.f),2.2f)*sh*(.3f+.7f*A)+spec*(clay?.3f:1.f)+fuzz*(clay?.2f:std::pow(std::max(col,0.f),1.2f))+.10f*rb;
    rgb[at*3+j]=std::pow(std::min(std::max(lin,0.f),1.f),1/2.2f);}
  }
 }
}
// Linear-blend skinning of positions and normals.
extern "C" void skin(int nv,const float*v,const float*n,const uint8_t*j,const uint8_t*w,const float*m,float*out,float*outn){
 for(int i=0;i<nv;i++){
  float x=v[i*3],y=v[i*3+1],z=v[i*3+2],nx=n[i*3],ny=n[i*3+1],nz=n[i*3+2];
  for(int r=0;r<3;r++){out[i*3+r]=0;outn[i*3+r]=0;}
  for(int k=0;k<4;k++){float wt=w[i*4+k]/255.f;if(wt==0)continue;const float*a=m+j[i*4+k]*16;
   for(int r=0;r<3;r++){out[i*3+r]+=wt*(a[r*4]*x+a[r*4+1]*y+a[r*4+2]*z+a[r*4+3]);outn[i*3+r]+=wt*(a[r*4]*nx+a[r*4+1]*ny+a[r*4+2]*nz);}}
  float l=std::sqrt(outn[i*3]*outn[i*3]+outn[i*3+1]*outn[i*3+1]+outn[i*3+2]*outn[i*3+2]);if(l>1e-9f)for(int r=0;r<3;r++)outn[i*3+r]/=l;
 }
}
// Rasterize triangles in UV space (u -> x, v -> y, glTF convention: v=0 is the top row) and
// write barycentrically interpolated per-vertex attributes (na floats each) into out (H*W*na).
extern "C" void bake(int nf,const int32_t*faces,const float*uv,int na,const float*attr,int W,int H,float*out,uint8_t*cover){
 for(int k=0;k<nf;k++){
  int id[3]={faces[k*3],faces[k*3+1],faces[k*3+2]};float sx[3],sy[3];
  for(int j=0;j<3;j++){sx[j]=uv[id[j]*2]*W;sy[j]=uv[id[j]*2+1]*H;}
  float det=(sy[1]-sy[2])*(sx[0]-sx[2])+(sx[2]-sx[1])*(sy[0]-sy[2]);if(std::fabs(det)<1e-12f)continue;
  int x0=std::max(0,(int)std::floor(std::min({sx[0],sx[1],sx[2]}))-1),x1=std::min(W-1,(int)std::ceil(std::max({sx[0],sx[1],sx[2]}))+1);
  int y0=std::max(0,(int)std::floor(std::min({sy[0],sy[1],sy[2]}))-1),y1=std::min(H-1,(int)std::ceil(std::max({sy[0],sy[1],sy[2]}))+1);
  for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++){
   float a=((sy[1]-sy[2])*(x+.5f-sx[2])+(sx[2]-sx[1])*(y+.5f-sy[2]))/det,b=((sy[2]-sy[0])*(x+.5f-sx[2])+(sx[0]-sx[2])*(y+.5f-sy[2]))/det,c=1-a-b;
   const float e=-.02f;if(a<e||b<e||c<e)continue;
   int at=y*W+x;if(cover[at]==2)continue;
   bool inside=a>=0&&b>=0&&c>=0;
   if(cover[at]==1&&!inside)continue;
   a=std::max(a,0.f);b=std::max(b,0.f);c=std::max(c,0.f);float s=a+b+c;a/=s;b/=s;c/=s;
   for(int q=0;q<na;q++)out[(size_t)at*na+q]=a*attr[id[0]*na+q]+b*attr[id[1]*na+q]+c*attr[id[2]*na+q];
   cover[at]=inside?2:1;
  }
 }
}
