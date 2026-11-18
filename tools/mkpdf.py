# Bird's-eye PDF plan drawn straight from the 3D model data. Units: metres. Mirrored like the DXF: windows at top, big boardroom on the right.
import json,re,math,matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle,Circle,Arc,Patch,Polygon
from matplotlib.lines import Line2D
t=open('3d/arc-office-3d.html').read(); m=re.search(r'DATA\s*=\s*',t); D=json.JSONDecoder().raw_decode(t[m.end():])[0]
W=D['width']; Y9=D['depth']; B=D['bump']['w']; YBB=D['bump']['d']
MX=lambda x: W-x
RED='#d0021b'; GLASS='#cfe8f7'; WOOD='#c49a6c'; SOFA='#9fb4c7'
COL={'white':'#ffffff','yellow':'#ffd800','oak':'#c8955c','marble':'#d9d9d9'}
def kind(o):
    if o['room'] in ('bigBoard','smallBoard') or o['kind'] in ('rrect','round'): return 'oak'
    if o['kind']=='marble' or o['room']=='eating': return 'marble'
    if o.get('top')=='yellow': return 'yellow'
    return 'white'
def R(x,y,w,d): return (MX(x+w),y,w,d)          # plan rect to mirrored drawing rect (left,bottom,w,h)

def cuts_on(w):
    hz=abs(w['y1']-w['y2'])<1e-6; out=[]
    for d in D['doors']:
        dh=abs(d['y1']-d['y2'])<1e-6
        if dh==hz and abs((d['y1'] if hz else d['x1'])-(w['y1'] if hz else w['x1']))<0.02:
            out.append((min(d['x1'],d['x2']),max(d['x1'],d['x2'])) if hz else (min(d['y1'],d['y2']),max(d['y1'],d['y2'])))
    if w['id']=='g2':
        for p in D.get('sidePanes',[]): out.append((p['a'],p['b']))
    return sorted(out)
def wall_rects():
    res=[]
    for w in D['walls']:
        hz=abs(w['y1']-w['y2'])<1e-6; a,b=(sorted([w['x1'],w['x2']]) if hz else sorted([w['y1'],w['y2']])); at=w['y1'] if hz else w['x1']
        typ='wall' if (w['type']=='wall' or w['id']=='g2') else w['type']
        thick=w.get('thick',0.127) if w['type']=='window' else 0.12 if typ=='wall' else 0.05
        if w['id']=='w9': thick=D['divider']
        segs=[]; s=a
        for c0,c1 in cuts_on(w):
            if c0>s: segs.append((s,c0))
            s=max(s,c1)
        if s<b: segs.append((s,b))
        for s0,s1 in segs:
            if w['type']=='glass' and w.get('thick'): thick=w['thick']; o0=at    # measured glass wall, on the open plan side
            elif w['type']=='window': o0=at if at>1 else at-thick     # window glass sits outside the white bound
            elif w['id']=='w9': o0=at
            else: o0=at-thick/2
            res.append((typ,R(s0,o0,s1-s0,thick) if hz else R(o0,s0,thick,s1-s0)))
    for p in D.get('sidePanes',[]): res.append(('glass',R(p['a'],-0.025,p['b']-p['a'],0.05)))
    return res

def draw(ax,furn):
    obst=[]                                   # boxes text must avoid: (x0,y0,x1,y1) in drawing space
    def box(l,b,w,h,pad=0.0): obst.append((l-pad,b-pad,l+w+pad,b+h+pad))
    for typ,(l,b,w,h) in wall_rects():
        if typ=='wall': ax.add_patch(Rectangle((l,b),w,h,fc='black',ec='black',lw=1.2,zorder=5))
        else: ax.add_patch(Rectangle((l,b),w,h,fc=GLASS,ec='black',lw=1.6,zorder=5))
        box(l,b,w,h,0.02)
    # bold outline of the whole office along the white bound
    outline=[(-B,0),(W,0),(W,Y9),(0,Y9),(0,YBB),(-B,YBB)]
    ax.add_patch(Polygon([(MX(x),y) for x,y in outline],closed=True,fill=False,ec='black',lw=3.2,zorder=6))
    # doors: leaf and swing
    for d in D['doors']:
        hz=abs(d['y1']-d['y2'])<1e-6; hx,hy=d['hinge']['x'],d['hinge']['y']
        w=abs(d['x2']-d['x1']) if hz else abs(d['y2']-d['y1'])
        if hz: cx_,cy_=(d['x2'] if abs(hx-d['x1'])<1e-6 else d['x1']),hy; ox,oy=hx,hy+w
        else: cx_,cy_=hx,(d['y2'] if abs(hy-d['y1'])<1e-6 else d['y1']); ox,oy=hx+w,hy   # user 10:42: side doors hinge at the divider and open into their rooms
        H=(MX(hx),hy); C=(MX(cx_),cy_); O=(MX(ox),oy)
        ax.plot([H[0],O[0]],[H[1],O[1]],color='#333',lw=1.4,zorder=4)
        a1=math.degrees(math.atan2(C[1]-H[1],C[0]-H[0])); a2=math.degrees(math.atan2(O[1]-H[1],O[0]-H[0]))
        if (a2-a1)%360>180: a1,a2=a2,a1
        ax.add_patch(Arc(H,2*w,2*w,theta1=a1,theta2=a2,color='#333',lw=0.9,ls=(0,(4,3)),zorder=4))
        obst.append((min(H[0],C[0],O[0]),min(H[1],C[1],O[1]),max(H[0],C[0],O[0]),max(H[1],C[1],O[1])))
    for p in D['pillars']:
        l,b,w,h=R(p['x'],p['y'],p['width'],p['depth']); ax.add_patch(Rectangle((l,b),w,h,fc='black',ec='black',zorder=5)); box(l,b,w,h,0.03)
    for k in ('cabinet','cab2'):
        c=D[k]; l,b,w,h=R(c['x'],c['y'],c['width'],c['depth'])
        ax.add_patch(Rectangle((l,b),w,h,fc=WOOD,ec='black',lw=1,zorder=4))
        ax.plot([l,l+w],[b,b+h],color='#5a3d1e',lw=0.6,zorder=4); ax.plot([l,l+w],[b+h,b],color='#5a3d1e',lw=0.6,zorder=4); box(l,b,w,h,0.03)
    if not furn: return obst
    for o in D['furniture']:
        if o['kind']=='tvh':
            l,b,w,h=R(o['cx']-o['w']/2,o['cy']-0.03,o['w'],0.06); ax.add_patch(Rectangle((l,b),w,h,fc='#222',ec='#222',zorder=3)); box(l,b,w,h,0.03); continue
        if o['id']=='sv':
            l,b,w,h=R(o['cx']-o['w']/2,o['cy']-o['d']/2,o['w'],o['d']); ax.add_patch(Rectangle((l,b),w,h,fc='#8a8a8a',ec='black',lw=0.8,zorder=3)); box(l,b,w,h,0.03); continue
        c=COL[kind(o)]
        if o['kind']=='round':
            ax.add_patch(Circle((MX(o['cx']),o['cy']),o['w']/2,fc=c,ec='black',lw=0.9,zorder=3)); r=o['w']/2; obst.append((MX(o['cx'])-r,o['cy']-r,MX(o['cx'])+r,o['cy']+r))
        else:
            l,b,w,h=R(o['cx']-o['w']/2,o['cy']-o['d']/2,o['w'],o['d']); ax.add_patch(Rectangle((l,b),w,h,fc=c,ec='black',lw=0.9,zorder=3)); box(l,b,w,h,0.03)
    for o in D['furniture']:
        if o['kind']=='tvh' or o['id']=='sv' or kind(o) not in ('white','yellow'): continue   # only the measured desks
        tall=o['d']>o['w']*1.2
        txt=('%.3f m across'%o['w']) if o['kind']=='round' else ('%.3f x %.3f m'%((o['d'],o['w']) if tall else (o['w'],o['d'])))
        fs=7 if min(o['w'],o['d'])>0.6 else 5.5
        if max(o['w'],o['d'])<0.8: txt=txt.replace(' x ','\nx ').replace(' m',' m'); fs=5.5
        ax.text(MX(o['cx']),o['cy'],txt,ha='center',va='center',fontsize=fs,rotation=90 if tall else 0,zorder=8,color='#1a1a1a',linespacing=1.0)
    for c in D['chairs']:
        r=0.2 if c.get('stool') else 0.27; x=MX(c['cx'])
        ax.add_patch(Circle((x,c['cy']),r,fc='white',ec='#555',lw=0.9,zorder=3)); obst.append((x-r,c['cy']-r,x+r,c['cy']+r))
    s=D['sofa']; dd=s['depth']
    y0=s['b']['y']; xc=s['c']['x']; ya=y0+s['a']['len']; yc=s['c']['y']
    zz=[(0,ya),(dd,ya),(dd,y0+dd),(xc+dd,y0+dd),(xc+dd,yc),(xc,yc),(xc,y0),(0,y0)]   # one Z-shaped sofa, no breaks
    ax.add_patch(Polygon([(MX(x),y) for x,y in zz],closed=True,fc=SOFA,ec='black',lw=0.9,zorder=3))
    for (x,y,w,h) in ((0,y0,dd,s['a']['len']),(dd,y0,xc,dd),(xc,yc,dd,y0+dd-yc)):
        l,b,w2,h2=R(x,y,w,h); box(l,b,w2,h2,0.03)
    return obst

def area(a,b): return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
def overlaps(a,b): return not (a[2]<=b[0] or b[2]<=a[0] or a[3]<=b[1] or b[3]<=a[1])
def place(ax,fig,txt,cands,obst,**kw):
    """put txt at the first candidate point whose text box hits nothing; keep the box as a new obstacle"""
    inv=ax.transData.inverted(); best=None
    for (x,y) in cands:
        tt=ax.text(x,y,txt,ha='center',va='center',zorder=8,**kw); bb=tt.get_window_extent(renderer=fig.canvas.get_renderer())
        (x0,y0),(x1,y1)=inv.transform([(bb.x0,bb.y0),(bb.x1,bb.y1)]); bx=(x0-0.03,y0-0.02,x1+0.03,y1+0.02)
        hits=sum(area(bx,o) for o in obst)
        if best is None or hits<best[0]:
            if best: best[1].remove()
            best=(hits,tt,bx)
        else: tt.remove()
        if hits<1e-9: break
    obst.append(best[2]); return best[1]

def dimline(ax,fig,obst,p1,p2,off,label=None,ext=True,side=None):
    """measurement line in red with arrow heads at both ends; p1,p2 in plan coordinates; off moves it sideways (drawing space)"""
    a=(MX(p1[0]),p1[1]); b=(MX(p2[0]),p2[1]); hz=abs(b[1]-a[1])<abs(b[0]-a[0])
    if hz: a2=(a[0],a[1]+off); b2=(b[0],b[1]+off)
    else: a2=(a[0]+off,a[1]); b2=(b[0]+off,b[1])
    if ext and off:
        for p,q in ((a,a2),(b,b2)):
            ax.plot([p[0],q[0]],[p[1],q[1]],color=RED,lw=0.5,ls=(0,(2,2)),zorder=7)
    ax.annotate('',xy=b2,xytext=a2,arrowprops=dict(arrowstyle='<|-|>',color=RED,lw=0.8,mutation_scale=9,shrinkA=0,shrinkB=0),zorder=7)
    L=math.dist(a,b); label=label or '%.3f m'%L
    mx,my=(a2[0]+b2[0])/2,(a2[1]+b2[1])/2
    sd=side if side is not None else 1
    cands=[]
    for dist in (0.13,0.22,0.34,0.48):
        for sg in (sd,-sd):
            for f in (0,-0.2,0.2,-0.35,0.35):
                cands.append((mx+f*L,my+sg*dist) if hz else (mx+sg*(dist+0.12),my+f*L))
    place(ax,fig,label,cands,obst,color=RED,fontsize=8.5,rotation=0 if hz else 90,bbox=dict(fc='white',ec='none',pad=0.4))
    obst.append((min(a2[0],b2[0])-0.02,min(a2[1],b2[1])-0.02,max(a2[0],b2[0])+0.02,max(a2[1],b2[1])+0.02))

POS={}   # label spots chosen on page 1, reused on page 2 so both pages match
def page(pdf,furn,sub):
    fig=plt.figure(figsize=(16.54,11.69)); ax=fig.add_axes([0.03,0.1,0.94,0.8])
    ax.set_xlim(-1.3,16.6); ax.set_ylim(-2.1,9.6); ax.set_aspect('equal',adjustable='datalim'); ax.axis('off')
    obst=draw(ax,furn); fig.canvas.draw()
    # room names, kept clear of tables, seats and walls
    for r in D['rooms']:
        if r['id']=='printIT': continue
        cx=MX(r['x']+r['width']/2); cy=r['y']+r['depth']/2
        cands=sorted([(cx+dx*r['width'],cy+dy*r['depth']) for dy in [i/20 for i in range(-9,10)] for dx in [i/20 for i in range(-7,8)]],key=lambda q:math.dist(q,(cx,cy)))
        tt=place(ax,fig,r['name'],POS.get(r['id'],cands),obst,fontsize=12,weight='bold',color='#1a1a1a'); POS.setdefault(r['id'],[tt.get_position()])
    if furn:
        s=D['sofa']
        place(ax,fig,'Sofa',[(MX(s['c']['x']+s['depth']/2),s['c']['y']+s['c']['len']/2)],obst,fontsize=8,color='#1a1a1a',rotation=90)
        pr=[o for o in D['furniture'] if o['id']=='sv'][0]
        ax.text(MX(pr['cx']),pr['cy'],'Printer',ha='center',va='center',fontsize=7,color='white',zorder=8)
    for d in D['doors']:
        hz=abs(d['y1']-d['y2'])<1e-6; x=MX((d['x1']+d['x2'])/2); y=(d['y1']+d['y2'])/2
        name=d['name'].replace(' (card lock)','').replace(' (locked)','')
        cands=[(x,-0.2),(x,-0.3)] if hz else [(x+1.3,y),(x+1.3,y+0.2),(x+1.3,y-0.2),(x+1.3,y+0.35),(x+1.3,y-0.35)]
        tt=place(ax,fig,name,POS.get(d['id'],cands),obst,fontsize=7.5,color='#333'); POS.setdefault(d['id'],[tt.get_position()])
    # measurement chains outside the building
    yb=-0.55
    for x1,x2 in ((-B,0),(0,2.399),(2.399,11.419),(11.419,W)): dimline(ax,fig,obst,(x1,0),(x2,0),yb,side=-1)
    dimline(ax,fig,obst,(0,0),(W,0),-1.05,side=-1,label='%.3f m (main office, without the boardroom bump)'%W)
    dimline(ax,fig,obst,(-B,0),(W,0),-1.55,side=-1,label='%.3f m (total front, with the boardroom bump)'%(W+B))
    xs=[0,3.272,4.224,4.327,Y9]
    for y1,y2 in zip(xs,xs[1:]): dimline(ax,fig,obst,(W,y1),(W,y2),-0.45,side=-1,label='%.3f m'%(y2-y1) if y2-y1>0.2 else '%.3f'%(y2-y1))
    dimline(ax,fig,obst,(W,0),(W,Y9),-0.95,side=-1)
    dimline(ax,fig,obst,(-B,0),(-B,YBB),0.45,side=1); dimline(ax,fig,obst,(0,YBB),(0,Y9),0.45+B,side=1); dimline(ax,fig,obst,(0,0),(0,Y9),0.95+B,side=1,label='%.3f m'%Y9)
    P={p['id']:p for p in D['pillars']}
    yt=Y9+0.5
    for x1,x2 in ((P['p1']['x']+P['p1']['width'],P['p2']['x']),(P['p2']['x'],P['p2']['x']+P['p2']['width']),(P['p2']['x']+P['p2']['width'],11.419)):
        dimline(ax,fig,obst,(x1,Y9),(x2,Y9),yt-Y9,side=1)
    # pillar and cupboard sizes, next to each object
    def od(x1,y1,x2,y2,side):
        hz=abs(y2-y1)<abs(x2-x1); dimline(ax,fig,obst,(x1,y1),(x2,y2),0,ext=False,side=side)
    for k in ('p1','p3'):
        p=P[k]; yy=p['y']+p['depth']+0.12 if k=='p1' else p['y']-0.15; od(p['x'],yy,p['x']+p['width'],yy,-1); od(p['x']+p['width']+0.15,p['y'],p['x']+p['width']+0.15,p['y']+p['depth'],1)
    p=P['p2']; od(p['x']+p['width']+0.15,p['y'],p['x']+p['width']+0.15,p['y']+p['depth'],-1)
    c=D['cabinet']; od(c['x'],c['y']+c['depth']+0.15,c['x']+c['width'],c['y']+c['depth']+0.15,1); od(c['x']+c['width']+0.15,0,c['x']+c['width']+0.15,c['depth'],-1)
    c=D['cab2']; od(c['x'],c['y']-0.15,c['x']+c['width'],c['y']-0.15,-1); od(c['x']-0.15,c['y'],c['x']-0.15,c['y']+c['depth'],-1)
    fig.text(0.5,0.955,'ARC Group Hong Kong office, 5/F',fontsize=19,weight='bold',ha='center')
    fig.text(0.5,0.93,sub,fontsize=11,ha='center')
    fig.text(0.5,0.91,'The lift lobby, the pantry and the toilets are not shown.',fontsize=11,ha='center')
    H=[Line2D([],[],color='black',lw=3.2,label='Office outline (white bound)'),
       Patch(fc='black',ec='black',label='Solid wall'),
       Patch(fc=GLASS,ec='black',lw=1.6,label='Glass wall or window'),
       Line2D([],[],color='#333',lw=1,ls=(0,(4,3)),label='Door and its swing'),
       Line2D([],[],color=RED,lw=0.8,marker='>',ms=5,label='Measurement, in metres (m)'),
       Patch(fc='black',ec='black',label='Pillar (fixed, cannot move)'),
       Patch(fc=WOOD,ec='black',label='Full height wooden cupboard')]
    if furn: H+=[Patch(fc='#ffffff',ec='black',label='White desk, 1.397 x 0.699 m (55 x 27.5 in)'),
       Patch(fc='#ffd800',ec='black',label='Yellow desk, 1.600 x 0.800 m (63 x 31.5 in)'),
       Patch(fc='#c8955c',ec='black',label='Oak meeting table'),
       Patch(fc='#d9d9d9',ec='black',label='Marble eating table'),
       Patch(fc=SOFA,ec='black',label='Sofa'),
       Line2D([],[],ls='none',marker='o',ms=10,mfc='white',mec='#555',label='Seat'),
       Patch(fc='#222',ec='#222',label='TV screen (thin bar)'),
       Patch(fc='#8a8a8a',ec='black',label='Printer')]
    fig.legend(handles=H,loc='lower center',ncol=5,fontsize=9.5,frameon=True,edgecolor='#999',bbox_to_anchor=(0.5,0.01),handlelength=2.6,columnspacing=1.6)
    pdf.savefig(fig); plt.close(fig)

out='/mnt/project-files/office-dimensions/arc-hk-office-plan.pdf'
with PdfPages(out) as pdf:
    page(pdf,True,'Units: metres (m). Windows at the top, lift lobby at the bottom. 18 Nov 2026.')
    page(pdf,False,'Outline only, without furniture. Units: metres (m). Windows at the top, lift lobby at the bottom. 18 Nov 2026.')
print('ok')
