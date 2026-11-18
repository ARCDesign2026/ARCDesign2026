import json
s=json.load(open('snap.json')); f=json.load(open('furn.json'))
doors=[]
for d in s['doors']:
    d=dict(d)
    if d['id']=='d1':   # user 09:55: big boardroom door 38 in wide; edge by the boardroom glass corner kept
        d['x2']=2.399; d['x1']=round(d['x2']-38*0.0254,4); d['hinge']={'x':d['x2'],'y':0}   # user 10:42: hinged at the divider, opens into the boardroom   # right against the glass divider
    if d['id']=='d4':   # user 09:55: top left room door 36.8 in, hinge on the divider side
        d['y2']=round(d['y1']+36.8*0.0254,4)
    if d['id']=='d3':   # user 09:54: small boardroom door leaf 36.75 in, inside the 37.5 in opening; hinge on the divider side
        d['y1']=round(d['y2']-36.75*0.0254,4)
    if d['id']=='d2':   # user 09:52: main door 39.3 in wide; cupboard side frame kept where it is
        # user 10:17: front from the boardroom: wall, boardroom door, 5 in glass divider, 8 in pane, main door, 8 in pane, then the wooden slats
        w=round(39.3*0.0254,4); d['x1']=round(2.399+5*0.0254+8*0.0254,4); d['x2']=round(d['x1']+w,4); d['hinge']={'x':d['x1'],'y':0}
    doors.append({k:d[k] for k in ('id','name','x1','y1','x2','y2','hinge')})
cab=[o for o in s['furniture'] if o['id']=='st'][0]
xen=s['gridlines']['x']['XEN']; xsm=s['gridlines']['x']['XSM']; PANE=round(8*0.0254,4)   # user 09:55: tall 8 in glass pane on each side of the main door
cab=dict(x=round([d for d in doors if d['id']=='d2'][0]['x2']+PANE,4),y=0,width=round(3*0.6064+1.2176+(11.75+5.45)*0.0254,4),depth=round(15*0.0254,4))  # user 09:49: entrance cupboard SLSS + 11.75 in + 5.45 in long, 15 in thick; wooden slat wall runs the whole front
furn=f['furniture']; chairs=f['chairs']
for o in furn:
    if o['room']=='openPlan' and o['cy']-o['d']/2 < cab['depth']+0.9 and o['cx']+o['w']/2>cab['x'] and o['cx']-o['w']/2<cab['x']+cab['width']:
        o['cy']=round(o['cy']+0.55,3)
for c in chairs:
    if c['room']=='openPlan' and c['cy']<2 and cab['x']-0.5<c['cx']<cab['x']+cab['width']+0.5: c['cy']=round(c['cy']+0.55,3)
# user 08:24: measured desks. Middle cluster and desks flush against the cupboard: 55 x 27.5 in. All other desks: 63 x 31.5 in. Height 29.5 in.
IN=0.0254; A=(55*IN,27.5*IN); B=(63*IN,31.5*IN)
F={o['id']:o for o in furn}
cl=['c1','c2','c3','c4']; mx=sum(F[k]['cx'] for k in cl)/4; my=(F['c1']['cy']+F['c5']['cy'])/2
for i,k in enumerate(cl):
    for k2,sg in ((k,-1),('c'+str(i+5),1)):
        F[k2].update(w=round(A[0],4),d=round(A[1],4),cx=round(mx+(i-1.5)*A[0],3),cy=round(my+sg*A[1]/2,3))
def pair(a,b,size,y0=None):
    c=(F[a]['cx']+F[b]['cx'])/2
    for k,sg in ((a,-1),(b,1)):
        o=F[k]; cy=o['cy'] if y0 is None else y0+size[0]/2
        o.update(w=round(size[1],4),d=round(size[0],4),cx=round(c+sg*size[1]/2,3),cy=round(cy,3))
pair('dS','dT',A,y0=cab['depth'])            # flush against the cupboard
pair('dC','dF',B,y0=F['dC']['cy']-F['dC']['d']/2)
pair('dTh','dA',B)
F['dN'].update(w=round(B[1],4),d=round(B[0],4),cy=round(min(F['dN']['cy'],s['gridlines']['y']['Y9']-0.05-B[0]/2),3))
F['dG'].update(w=round(B[0],4),d=round(B[1],4))
for k in ('dC','dF','dTh','dA','dN','dG'): F[k]['top']='yellow'   # user 08:26: these desks are yellow, middle and cupboard desks white
# user 08:19: desk next to the middle pillar sits flush against it; its chair is on the window side, facing the office
p2=[o for o in s['furniture'] if o['id']=='p2'][0]
# user 08:32: wooden cupboard on the desk side of the middle pillar; pillar + cupboard = 17 3/16 in + 2S; desk and chair flush against its end
T=s['tile_sizes']; Y9=s['gridlines']['y']['Y9']; IN=0.0254
# user 09:42: middle pillar is a 37.4 in square; its cupboard is 1L + 1S + 6 in wide and 18 in deep, on the office side.
# Window line to cupboard front stays 17 3/16 in + 2S (user 08:32). Pillar keeps its desk side edge (2.877 m to the top left room glass).
PW=round(37.4*IN,4); CW=round(T['L']['m']+T['S']['m']+6*IN,4); CD=round(18*IN,4)
P2FRONT=round(Y9-(4.5+37.4+18)*IN,4)   # user 10:08: pillar + cupboard sit 4.5 in in front of the white bound (the room line). The 08:32 total (17 3/16 in + 2S) is 0.128 m longer and is not used
p2r=p2['x']+p2['width']; p2.update(x=round(p2r-PW,4),y=round(P2FRONT+CD,4),width=PW,depth=PW)
OVER=round(CW-PW,4)
cab2=dict(x=round(p2r-CW,4),y=P2FRONT,width=CW,depth=CD)
for o in furn:
    if o['id']=='dG':
        o['cx']=round(p2['x']+p2['width']+o['w']/2,3); o['cy']=round(P2FRONT+o['d']/2,3)  # flush against the pillar side and lined up with the cupboard front
        for c in chairs:
            pass
        chairs.append(dict(room='openPlan',cx=o['cx'],cy=round(o['cy']+o['d']/2+0.3,3)))   # own chair; the cluster keeps all 8 of its chairs
# eating area: 2 marble tables with stools, L-shaped sofa along the window wall and the big boardroom glass
ey=[r for r in s['rooms'] if r['id']=='eating'][0]
pil=[o for o in s['furniture'] if o['id']=='p1'][0]
# user 09:44: eating area pillar is 47.25 in (door-to-window direction) by 35.75 in (boardroom-to-boardroom direction). Kept its office side edge (measured 6.514 m chain) and its back face.
_back=pil['y']+pil['depth']; _r=pil['x']+pil['width']
pil.update(shape='rect',width=round(35.75*0.0254,4),depth=round(47.25*0.0254,4)); pil.update(x=round(_r-pil['width'],4),y=round(_back-pil['depth'],4))
xbb=ey['width']; d1=[d for d in doors if d['id']=='d2'][0]
SD=round(0.65*2/3,3)   # user 10:39: sofa 2/3 of the earlier 0.65 m depth
sofa=dict(depth=SD,a=dict(x=0,y=ey['y'],len=round(pil['y']-ey['y'],3)),b=dict(x=0,y=ey['y'],len=round(xbb+SD,3)),c=dict(x=round(xbb+5*0.0254,3),y=round(abs(d1['x2']-d1['x1'])*1.5,3),len=round(ey['y']-abs(d1['x2']-d1['x1'])*1.5,3)))
sofa['b']['len']=round(sofa['c']['x']+SD,3)   # user 10:40: one single sofa, the runs meet flush at the corner
ty=ey['y']+0.65+0.15+0.35
for o in furn:
    if o['id'] in ('et1','et2'):
        o.update(cx=1.15 if o['id']=='et1' else 1.9, cy=round(ty,3), w=0.65, d=0.7, kind='marble')
chairs=[c for c in chairs if c['room']!='eating']
# 4 stools in a row on the window side of the tables, starting clear of the eating area pillar (0.36 m apart, stool seat 0.36 m across)
for i in range(4): chairs.append(dict(room='eating',cx=round(pil['x']+pil['width']+0.2+i*0.36,3),cy=round(ty+0.35+0.28,3),stool=True))
# big boardroom sticks out past the eating area's window wall by BUMP m (user: about an arm's length, to be measured)
BUMP=round(39.75*0.0254,3)   # user 09:37: measured 39.75 in from the eating area wall
walls=[dict(w) for w in s['walls']]
for w in walls:
    if w['id']=='w6': w['x1']=-BUMP
    if w['id']=='n2': w['y1']=5.067
    if w['id']=='n1': w['thick']=round(5*0.0254,3)
    if w['id']=='g3': w['thick']=round(5*0.0254,3)   # user 10:17: glass between the big boardroom and the open plan is 5 in thick, on the open plan side   # window glass 5 in thick, outside the room line
walls.append(dict(id='n2b',name='External windows, big boardroom',type='window',x1=-BUMP,y1=0,x2=-BUMP,y2=5.067,thick=round(5*0.0254,3)))   # glass pane 5 in thick
walls.append(dict(id='w6b',name='Step wall, boardroom to eating area',type='wall',x1=-BUMP,y1=5.067,x2=0,y2=5.067))
s['walls']=walls
for r in s['rooms']:
    if r['id']=='bigBoard': r['x']=-BUMP; r['width']=round(2.399+BUMP,3)
for o in furn+chairs:
    if o['room']=='bigBoard': o['cx']=round(o['cx']-BUMP/2,3)
for o in furn:
    if o['id']=='tv1': o['w']=[x for x in furn if x['id']=='tv4'][0]['w']
printer=dict(cx=round(p2['x']-OVER/2,3),cy=round(p2['y']+0.32,3),w=0.6,d=0.55,h=1.05)
# user 08:59: remove the tall box (comms rack); the small box is the printer, hidden between the cupboard and the window
furn=[o for o in furn if o['id']!='rk']
for o in furn:
    if o['id']=='sv': o.update(name='Printer',cx=printer['cx'],cy=round(p2['y']+0.03+o['d']/2,3))
# the larger top left room pillar now reaches the round table's chairs, so the table and its chairs move 0.3 m toward the divider
for o in furn:
    if o['id']=='t3': o['cy']=round(o['cy']-0.3,3)
for c in chairs:
    if c['room']=='securities' and c['cx']>12.5 and c['cy']<7: c['cy']=round(c['cy']-0.3,3)
# scale pass (user 08:58): office chairs about 0.62 m across; seat centre 0.35 m from the table edge; no chair overlaps another chair or glass
F={o['id']:o for o in furn}
F['dN']['cx']=round(max(F['dN']['cx'],s['gridlines']['x']['XSM']+0.03+F['dN']['w']/2),3)   # was crossing the top left room glass
chairs.append(dict(room='securities',cx=round(F['dN']['cx']+F['dN']['w']/2+0.35,3),cy=F['dN']['cy']))   # user 16:40: the top left room desk had no chair; seat on the room side, facing the glass
SURF=[o for o in furn if o['kind'] not in ('tvh',) and o['id']!='sv']
def near(c):
    return min(SURF,key=lambda o:(max(abs(c['cx']-o['cx'])-o['w']/2,0)**2+max(abs(c['cy']-o['cy'])-o['d']/2,0)**2) if o['room']==c['room'] else 99)
groups={}
for c in chairs:
    if c.get('stool'): continue
    o=near(c); dx=abs(c['cx']-o['cx'])-o['w']/2; dy=abs(c['cy']-o['cy'])-o['d']/2
    if o['kind']=='round':
        import math; a=math.atan2(c['cy']-o['cy'],c['cx']-o['cx']); c['cx']=round(o['cx']+math.cos(a)*(o['w']/2+0.3),3); c['cy']=round(o['cy']+math.sin(a)*(o['w']/2+0.3),3); continue
    if dx>=dy:   # chair beside a long side running along y
        sg=1 if c['cx']>o['cx'] else -1; c['cx']=round(o['cx']+sg*(o['w']/2+0.35),3); groups.setdefault((o['id'],'x',sg),[]).append(c)
    else:
        sg=1 if c['cy']>o['cy'] else -1; c['cy']=round(o['cy']+sg*(o['d']/2+0.35),3); groups.setdefault((o['id'],'y',sg),[]).append(c)
for (oid,ax,sg),cs in groups.items():
    o=F[oid]; k='cy' if ax=='x' else 'cx'; centre=o[k]; length=o['d'] if ax=='x' else o['w']
    n=len(cs); pitch=max(0.65,length/n) if n>1 else 0
    if o['room']=='openPlan' and n==1: cs[0][k]=round(centre,3); continue
    if n>1:
        cs.sort(key=lambda c:c[k]); start=centre-pitch*(n-1)/2
        for i,c in enumerate(cs): c[k]=round(start+i*pitch,3)
# user 09:45: top left room pillar same size as the eating area pillar (47.25 in door-to-window, 35.75 in across); kept its office side edge and back face
p3=[o for o in s['furniture'] if o['id']=='p3'][0]; _back=p3['y']+p3['depth']
p3.update(shape='rect',width=round(35.75*0.0254,4),depth=round(47.25*0.0254,4)); p3['y']=round(_back-p3['depth'],4)
# measurement lines for objects the user measured (drawn next to each object)
def od(x1,y1,x2,y2,v): return dict(x1=round(x1,3),y1=round(y1,3),x2=round(x2,3),y2=round(y2,3),t='%.3f m'%v)
P={o['id']:o for o in s['furniture'] if o['id'] in ('p1','p2','p3')}
objdims=[
 od(cab['x'],cab['depth']+0.2,cab['x']+cab['width'],cab['depth']+0.2,cab['width']),
 od(cab['x']+cab['width']+0.2,0,cab['x']+cab['width']+0.2,cab['depth'],cab['depth']),
 od(cab2['x'],cab2['y']-0.2,cab2['x']+cab2['width'],cab2['y']-0.2,cab2['width']),
 od(cab2['x']-0.2,cab2['y'],cab2['x']-0.2,cab2['y']+cab2['depth'],cab2['depth']),
]
for k,o in P.items():
    objdims.append(od(o['x'],o['y']+o['depth']+0.12,o['x']+o['width'],o['y']+o['depth']+0.12,o['width']) if k=='p3' else od(o['x'],o['y']-0.15,o['x']+o['width'],o['y']-0.15,o['width']) if k!='p2' else od(o['x']+o['width']+0.15,o['y'],o['x']+o['width']+0.15,o['y']+o['depth'],o['depth']))
    if k!='p2': objdims.append(od(o['x']+o['width']+0.15,o['y'],o['x']+o['width']+0.15,o['y']+o['depth'],o['depth']))
objdims.append(od(-BUMP,5.067+0.3,0,5.067+0.3,BUMP))
# desk sizes (user 08:24): one desk of each group, size shown on its office-side edges
for k in ('c1','dS','dC','dTh','dG','dN'):
    f=[x for x in furn if x['id']==k][0]; x0,y0,x1,y1=f['cx']-f['w']/2,f['cy']-f['d']/2,f['cx']+f['w']/2,f['cy']+f['d']/2
    objdims.append(od(x0,y0+0.08,x1,y0+0.08,f['w'])); objdims.append(od(x1-0.08,y0,x1-0.08,y1,f['d']))
D2=[d for d in doors if d['id']=='d2'][0]
sidePanes=[dict(a=round(D2['x1']-PANE,4),b=D2['x1']),dict(a=D2['x2'],b=round(D2['x2']+PANE,4))]
for w in s['walls']:
    if w['id']=='w6': w['x2']=[d for d in doors if d['id']=='d1'][0]['x1']
for c in chairs:   # keep every chair inside the window line
    if not c.get('stool'): c['cy']=round(min(c['cy'],s['gridlines']['y']['Y9']-0.3),3)
data=dict(sidePanes=sidePanes,objdims=objdims,cab2=cab2,bump=dict(x=-BUMP,y=0,w=BUMP,d=5.067),sofa=sofa,width=s['gridlines']['x']['X9'],depth=s['gridlines']['y']['Y9'],divider=round(s['gridlines']['y']['YSB2']-s['gridlines']['y']['YSB'],4),
  walls=[{k:w[k] for k in ('id','type','x1','y1','x2','y2','thick') if k in w} for w in s['walls']],doors=doors,
  rooms=[{k:r[k] for k in ('id','name','x','y','width','depth')} for r in s['rooms']],
  pillars=[{k:o[k] for k in ('id','shape','x','y','width','depth')} for o in s['furniture'] if o['id'] in ('p1','p2','p3')],
  cabinet=cab,furniture=furn,chairs=chairs,sites=json.load(open('sites.json')))
open('3d/arc-office-3d.html','w').write(open('3d/template.html').read().replace('__DATA__',json.dumps(data)))
