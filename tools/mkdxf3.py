# AutoCAD DXF from the current 3D model data (plan view, metres). Same orientation as the survey: x along the front, y from front (lift lobby) to windows.
import json,re,ezdxf
from ezdxf.enums import TextEntityAlignment
t=open('3d/arc-office-3d.html').read(); m=re.search(r'DATA\s*=\s*',t); D=json.JSONDecoder().raw_decode(t[m.end():])[0]
doc=ezdxf.new('R2010',setup=True); doc.units=6; msp=doc.modelspace()
L=dict(WALL=7,GLASS=4,WINDOW=5,DOOR=1,PILLAR=8,CUPBOARD=30,FURNITURE=2,CHAIRS=9,ROOM_NAMES=3,DIM_MEASURED=3,DIM_TOTAL=6,NOTES=7)
for k,c in L.items(): doc.layers.add(k,color=c)
ds=doc.dimstyles.new('ARC'); ds.dxf.dimtxt=0.12; ds.dxf.dimasz=0.08; ds.dxf.dimexo=0.05; ds.dxf.dimexe=0.08; ds.dxf.dimdec=3; ds.dxf.dimtad=1; ds.dxf.dimgap=0.03
def rect(x,y,w,d,layer):
    pts=[(MX(x),y),(MX(x+w),y),(MX(x+w),y+d),(MX(x),y+d)]; msp.add_lwpolyline(pts,close=True,dxfattribs={'layer':layer}); return pts
def line(x1,y1,x2,y2,layer): msp.add_line((MX(x1),y1),(MX(x2),y2),dxfattribs={'layer':layer})
def text(s,x,y,h,layer,al=TextEntityAlignment.MIDDLE_CENTER):
    msp.add_text(s,height=h,dxfattribs={'layer':layer}).set_placement((MX(x),y),align=al)
def arc(cx,cy,r,a0,a1,layer):   # mirrored arc: angle a becomes 180-a
    msp.add_arc((MX(cx),cy),r,180-a1,180-a0,dxfattribs={'layer':layer})
def circle(cx,cy,r,layer): msp.add_circle((MX(cx),cy),r,dxfattribs={'layer':layer})
def dim(p1,p2,base,layer,txt='<>'):
    a=(MX(p1[0]),p1[1]); b=(MX(p2[0]),p2[1]); hz=abs(b[1]-a[1])<abs(b[0]-a[0])
    if hz: a,b=sorted([a,b]); dist=base          # left to right keeps text upright, offset stays on the same side
    else: a,b=sorted([a,b],key=lambda q:q[1]); dist=-base   # bottom to top; mirror flips the side
    d=msp.add_aligned_dim(p1=a,p2=b,distance=dist,dimstyle='ARC',dxfattribs={'layer':layer},text=txt); d.render()
W=D['width']
MX=lambda x: W-x
doors={d['id']:d for d in D['doors']}
def cuts_on(w):
    hz=abs(w['y1']-w['y2'])<1e-6; out=[]
    for d in D['doors']:
        dh=abs(d['y1']-d['y2'])<1e-6
        if dh==hz and abs((d['y1'] if hz else d['x1'])-(w['y1'] if hz else w['x1']))<0.02:
            out.append((min(d['x1'],d['x2']),max(d['x1'],d['x2'])) if hz else (min(d['y1'],d['y2']),max(d['y1'],d['y2'])))
    if w['id']=='g2':
        for p in D.get('sidePanes',[]): out.append((p['a'],p['b']))
    return sorted(out)
for w in D['walls']:
    hz=abs(w['y1']-w['y2'])<1e-6; a,b=(sorted([w['x1'],w['x2']]) if hz else sorted([w['y1'],w['y2']])); at=w['y1'] if hz else w['x1']
    lay={'wall':'WALL','glass':'GLASS','window':'WINDOW'}[w['type']]
    if w['id']=='g2': lay='WALL'   # wooden slat wall
    thick=w.get('thick',0.05 if w['type']!='wall' else 0.12)
    if w['id']=='w9': thick=D['divider']
    out=1 if (w['type']=='window' and at>1) else -1 if w['type']=='window' else 0
    segs=[]; s=a
    for c0,c1 in cuts_on(w):
        if c0>s: segs.append((s,c0))
        s=max(s,c1)
    if s<b: segs.append((s,b))
    for s0,s1 in segs:
        o0=at if out else at-thick/2; 
        if out==1: o0=at
        if out==-1: o0=at-thick
        if hz: rect(s0,o0,s1-s0,thick,lay)
        else: rect(o0,s0,thick,s1-s0,lay)
for p in D.get('sidePanes',[]): rect(p['a'],0,p['b']-p['a'],0.03,'GLASS')
for d in D['doors']:
    hz=abs(d['y1']-d['y2'])<1e-6; hx,hy=d['hinge']['x'],d['hinge']['y']; w=abs(d['x2']-d['x1']) if hz else abs(d['y2']-d['y1'])
    if hz:
        other=d['x2'] if abs(hx-d['x1'])<1e-6 else d['x1']; sg=1 if other>hx else -1
        line(hx,hy,hx,hy+w,'DOOR'); arc(hx,hy,w,0 if sg>0 else 90,90 if sg>0 else 180,'DOOR')
    else:
        other=d['y2'] if abs(hy-d['y1'])<1e-6 else d['y1']; sg=1 if other>hy else -1
        line(hx,hy,hx+w,hy,'DOOR'); arc(hx,hy,w,0 if sg>0 else -90,90 if sg>0 else 0,'DOOR')   # opens into the room
    text(d['name'],(d['x1']+d['x2'])/2+(0 if hz else -0.25),(d['y1']+d['y2'])/2+(0.18 if hz else 0),0.07,'DOOR')
for p in D['pillars']: pts=rect(p['x'],p['y'],p['width'],p['depth'],'PILLAR'); msp.add_hatch(color=8,dxfattribs={'layer':'PILLAR'}).paths.add_polyline_path(pts,is_closed=True)
for k in ('cabinet','cab2'):
    c=D[k]; rect(c['x'],c['y'],c['width'],c['depth'],'CUPBOARD'); line(c['x'],c['y'],c['x']+c['width'],c['y']+c['depth'],'CUPBOARD'); line(c['x'],c['y']+c['depth'],c['x']+c['width'],c['y'],'CUPBOARD')
q=D.get('printer')
for o in D['furniture']:
    if o['kind']=='tvh': rect(o['cx']-o['w']/2,o['cy']-0.03,o['w'],0.06,'FURNITURE'); continue
    if o['kind']=='round': circle(o['cx'],o['cy'],o['w']/2,'FURNITURE')
    else: rect(o['cx']-o['w']/2,o['cy']-o['d']/2,o['w'],o['d'],'FURNITURE')
    if o['kind'] in ('rect','marble') and o['room'] not in ('printIT',): pass
for c in D['chairs']:
    r=0.2 if c.get('stool') else 0.27
    circle(c['cx'],c['cy'],r,'CHAIRS')
s=D['sofa']; dd=s['depth']
rect(0,s['a']['y'],dd,s['a']['len'],'FURNITURE'); rect(dd,s['b']['y'],s['b']['len']-dd,dd,'FURNITURE'); rect(s['c']['x'],s['c']['y'],dd,s['c']['len'],'FURNITURE')
if D.get('bump'): pass
for r in D['rooms']: text(r['name'],r['x']+r['width']/2,r['y']+r['depth']/2,0.18,'ROOM_NAMES')
# measured lengths from the survey (inside) and object sizes
for d in D['sites']:
    hz=abs(d['y2']-d['y1'])<abs(d['x2']-d['x1'])
    dim((d['x1'],d['y1']),(d['x2'],d['y2']),0.3 if hz else -0.3,'DIM_MEASURED')
for d in D.get('objdims',[]):
    dim((d['x1'],d['y1']),(d['x2'],d['y2']),0.0,'DIM_MEASURED')
Wd,Dp=D['width'],D['depth']; B=D['bump']['w'] if D.get('bump') else 0
dim((0,0),(W,0),-0.9,'DIM_TOTAL'); dim((-B,0),(W,0),-1.4,'DIM_TOTAL')
dim((W,0),(W,Dp),-1.0,'DIM_TOTAL'); dim((0,5.067),(0,Dp),1.0,'DIM_TOTAL'); dim((-B,0),(-B,5.067),1.0,'DIM_TOTAL')
text('ARC Group HK office plan. Units: metres. Windows at top, lift lobby at bottom. Lines are the white bound at the base of the windows and glass; window glass (5 in) drawn outside it. Generated from the 3D model, 18 Nov 2026.',W/2,Dp+1.2,0.12,'NOTES')
doc.saveas('/mnt/project-files/office-dimensions/arc-hk-office.dxf')
print('ok', len(msp))
