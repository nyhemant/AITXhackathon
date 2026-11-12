import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from collections import deque
OUT='art/out/'

def components(alpha, min_px=800):
    h,w=alpha.shape; seen=np.zeros_like(alpha,bool); boxes=[]
    # downsample for speed
    for y in range(0,h,3):
        for x in range(0,w,3):
            if alpha[y,x] and not seen[y,x]:
                q=deque([(y,x)]); seen[y,x]=True; x0=x1=x; y0=y1=y; n=0
                while q:
                    cy,cx=q.popleft(); n+=1
                    x0=min(x0,cx);x1=max(x1,cx);y0=min(y0,cy);y1=max(y1,cy)
                    for dy,dx in ((3,0),(-3,0),(0,3),(0,-3)):
                        ny,nx=cy+dy,cx+dx
                        if 0<=ny<h and 0<=nx<w and alpha[ny,nx] and not seen[ny,nx]:
                            seen[ny,nx]=True; q.append((ny,nx))
                if n*9>=min_px: boxes.append((x0,y0,x1+3,y1+3,n))
    return boxes

# --- stickers: key out green
im=Image.open('art/stickers.jpg').convert('RGB'); a=np.asarray(im).astype(int)
r,g,b=a[...,0],a[...,1],a[...,2]
green=(g>120)&(g>r+40)&(g>b+40)
alpha=(~green).astype(np.uint8)*255
am=Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
boxes=components(np.asarray(am)>128, 4000)
boxes.sort(key=lambda bx:(bx[1]//200, bx[0]))
names=['american-bison','giant-panda','zebra','galapagos-tortoise','caribbean-flamingo','sumatran-tiger','koala','whale-shark']
print('stickers',len(boxes))
rgba=im.convert('RGBA'); rgba.putalpha(am)
# de-spill green on edges
px=np.asarray(rgba).copy(); m=(px[...,1]>px[...,0]+20)&(px[...,1]>px[...,2]+20)&(px[...,3]<250)
px[m,1]=np.maximum(px[m,0],px[m,2]); rgba=Image.fromarray(px)
for name,(x0,y0,x1,y1,n) in zip(names,boxes):
    c=rgba.crop((max(0,x0-4),max(0,y0-4),x1+4,y1+4))
    for size in (96,192):
        t=c.copy(); t.thumbnail((size,size),Image.LANCZOS)
        cv=Image.new('RGBA',(size,size),(0,0,0,0)); cv.paste(t,((size-t.width)//2,(size-t.height)//2),t)
        cv.save(f'{OUT}animal-{name}-{size}-v1.webp',quality=80,method=6)

# --- flourishes: white flood from edges
im=Image.open('art/flourish.jpg').convert('RGB'); a=np.asarray(im).astype(int)
white=(a.min(axis=2)>232)
# flood fill background from border
h,w=white.shape; bg=np.zeros_like(white); q=deque()
for x in range(w):
    for y in (0,h-1):
        if white[y,x]: bg[y,x]=True; q.append((y,x))
for y in range(h):
    for x in (0,w-1):
        if white[y,x] and not bg[y,x]: bg[y,x]=True; q.append((y,x))
while q:
    cy,cx=q.popleft()
    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
        ny,nx=cy+dy,cx+dx
        if 0<=ny<h and 0<=nx<w and white[ny,nx] and not bg[ny,nx]:
            bg[ny,nx]=True; q.append((ny,nx))
alpha=(~bg).astype(np.uint8)*255
am=Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.7))
# group by grid cells 3x2
rgba=im.convert('RGBA'); rgba.putalpha(am)
fn=['compass','ship','whale','liberty','capitol','forest']
cells=[(0,0),(1,0),(2,0),(0,1),(1,1),(2,1)]
A=np.asarray(am)>60
for name,(cx,cy) in zip(fn,cells):
    x0,x1=cx*w//3,(cx+1)*w//3; y0,y1=cy*h//2,(cy+1)*h//2
    sub=A[y0:y1,x0:x1]; ys,xs=np.where(sub)
    bx=(x0+xs.min()-3,y0+ys.min()-3,x0+xs.max()+3,y0+ys.max()+3)
    c=rgba.crop(bx)
    for size in (96,192):
        t=c.copy(); t.thumbnail((size,size),Image.LANCZOS)
        t.save(f'{OUT}deco-{name}-{size}-v1.webp',quality=80,method=6)
    print(name,c.size)

# --- textures: make seamless-ish by mirroring tile, 256px
for src,name in (('art/parchment.jpg','parchment'),('art/ocean.jpg','ocean')):
    t=Image.open(src).convert('RGB').crop((128,128,896,896)).resize((256,256),Image.LANCZOS)
    big=Image.new('RGB',(512,512)); big.paste(t,(0,0)); big.paste(t.transpose(Image.FLIP_LEFT_RIGHT),(256,0))
    big.paste(t.transpose(Image.FLIP_TOP_BOTTOM),(0,256)); big.paste(t.transpose(Image.ROTATE_180),(256,256))
    big=big.resize((256,256),Image.LANCZOS)
    big.save(f'{OUT}tex-{name}-256-v1.webp',quality=70,method=6)
