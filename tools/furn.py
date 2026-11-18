import json,re
src=open('v8.bak').read()
GX=json.loads(re.sub(r'(\w+):',r'"\1":',re.search(r'const GX_PT = (\{.*?\});',src).group(1)))
GY=json.loads(re.sub(r'(\w+):',r'"\1":',re.search(r'const GY_PT = (\{.*?\});',src).group(1)))
ROOMS={'bigBoard':('X0','YF','XBB','YBB'),'eating':('X0','YBB','XBB','Y9'),'openPlan':('XBB','YF','XSM','Y9'),'printIT':('XP1','YPT','XP2','Y9'),'smallBoard':('XSM','YF','X9','YSB'),'securities':('XSM','YSB2','X9','Y9')}
body=src[src.index('const OBJ_RAW = ['):]; body=body[:body.index('];')]
objs=[]
for m in re.finditer(r"\['(\w+)','([^']*)','(\w+)','(\w+)',([\d.]+),([\d.]+),([\d.]+),([\d.]+)",body):
    objs.append(dict(id=m[1],name=m[2],room=m[3],kind=m[4],x=float(m[5]),y=float(m[6]),w=float(m[7]),h=float(m[8])))
cb=src[src.index('const CHAIRS_RAW = ['):]; cb=cb[:cb.index('];\n')]
chairs=[]
for m in re.finditer(r"\['(\w+)',([\d.]+),\[(.*?)\]\]",cb):
    for p in re.finditer(r"\[([\d.]+),([\d.]+)\]",m[3]):
        chairs.append(dict(room=m[1],x=float(p[1])+float(m[2])/2,y=float(p[2])+float(m[2])/2))
snap=json.load(open('snap.json')); R={r['id']:r for r in snap['rooms']}
def place(room,cx,cy):
    l,t,r,b=ROOMS[room]; fx=(cx-GX[l])/(GX[r]-GX[l]); fy=(cy-GY[t])/(GY[b]-GY[t]); rr=R[room]
    return rr['x']+fx*rr['width'], rr['y']+fy*rr['depth']
out=[]
for o in objs:
    if o['id'] in ('eb','st','p1','p2','p3'): continue
    cx,cy=place(o['room'],o['x']+o['w']/2,o['y']+o['h']/2)
    l,t,r,b=ROOMS[o['room']]; rr=R[o['room']]
    sx=rr['width']/((GX[r]-GX[l])*0.02); sy=rr['depth']/((GY[b]-GY[t])*0.02)
    out.append(dict(id=o['id'],name=o['name'],room=o['room'],kind=o['kind'],cx=round(cx,3),cy=round(cy,3),w=round(o['w']*0.02*(sx if o['kind']!='round' else (sx*sy)**0.5),3),d=round(o['h']*0.02*(sy if o['kind']!='round' else (sx*sy)**0.5),3),scale=[round(sx,3),round(sy,3)]))
ch=[]
for c in chairs:
    cx,cy=place(c['room'],c['x'],c['y']); ch.append(dict(room=c['room'],cx=round(cx,3),cy=round(cy,3)))
json.dump(dict(furniture=out,chairs=ch),open('furn.json','w'))
print(len(out),len(ch)); [print(o) for o in out]
