"""Deterministic vanilla v3 decoration. Source is always the verified backup."""
import copy, hashlib, json, zipfile
from pathlib import Path
import numpy as np

root=Path(__file__).resolve().parent.parent
work=root/'.codex-lighting'
backup=json.loads((work/'backup.json').read_text())
with zipfile.ZipFile(backup['path']) as z:
    original=z.read('NormalStandard.dat')
    info=json.loads(z.read('Info.dat'))
    source=json.loads(original)
assert hashlib.sha256(original).hexdigest()==backup['hashes']['NormalStandard.dat']
# Preserve the latest editor state when reapplying decoration.
current_map=(root/'NormalStandard.dat').read_bytes()
current_info=(root/'Info.dat').read_bytes()
source=json.loads(current_map)
info=json.loads(current_info)
with zipfile.ZipFile(work/'before-reapply.zip','x',zipfile.ZIP_DEFLATED) as z:
    z.writestr('NormalStandard.dat',current_map)
    z.writestr('Info.dat',current_info)
analysis=json.loads((work/'analysis.json').read_text())
F=np.load(work/'features.npz'); bpm=info['audio']['bpm']; seconds=60/bpm
notes=source['colorNotes']; beats=sorted(set(n['b'] for n in notes))
end=analysis['duration']/seconds
sections=analysis['sections']

def strength(b,band):
    mask=abs(F['t']-b*seconds)<.045
    v=float(F[band][mask].max()) if mask.any() else 0
    return float(np.clip(v/(np.percentile(F[band],95)+1e-9),0,1))

events={}
def event(b,t,v,f=1):
    if 0<=b<end:
        events[(round(float(b),4),t)]={'b':round(float(b),4),'et':t,'i':v,'f':round(float(f),3)}
def light(b,t,red,kind,brightness):
    event(b,t,{'on':1,'flash':2,'fade':3,'transition':4}[kind]+(4 if red else 0),brightness)

# A low ring bed preserves visual continuity. Other channels have separate roles.
for t in range(5): event(0,t,0,0)
for t in (12,13): event(0,t,0)
light(1,1,False,'transition',.18)
for si,s in enumerate(sections):
    a,z=s['start'],s['end']; quiet=si==0; build=si==5
    red=si in (2,4,6,8,9)
    intensity=.52 if quiet else (.73 if build else .9)
    light(a,1,red,'transition',.25 if quiet else .48)
    event(a,12,1 if quiet else (2 if build else 3))
    event(a,13,1 if quiet else (3 if build else 2))
    # Bass on the rear lights, weighted by measured bass attacks.
    for b in np.arange(a,z,2 if quiet else 1):
        bass=strength(b,'bass')
        if bass<.16: continue
        light(b,0,red,'flash',intensity*(.38+.5*bass))
        light(b+.65,0,red,'transition',.12 if quiet else .22)
    # Existing musical note timings drive left/right response; minimum 1/2 beat.
    last=-100
    for b in [b for b in beats if a<=b<z]:
        if b-last < (1 if quiet else .5)-1e-6: continue
        mid=strength(b,'mid')
        if mid<(.23 if quiet else .18): continue
        group=2+(int(round((b-a)*2))%2)
        # Alternate sides by musical gesture rather than every simultaneous note.
        group=2+(int((b-a)//2)%2)
        light(b,group,not red if int((b-a)//4)%4==3 else red,'flash',intensity*(.45+.4*mid))
        light(b+.34,group,red,'transition',.10 if quiet else .18)
        last=b
    # Central accents only on strong high-frequency/note attacks.
    for b in np.arange(a,z,4 if quiet else 2):
        if strength(b,'high')>.28:
            light(b,4,not red,'fade',.38 if quiet else .68)
    # Phrase breathing and occasional ring movement, never fast spin spam.
    for b in np.arange(a,z,16 if quiet else 8):
        event(b,8,0)
        light(b,1,red,'flash',.38 if quiet else .72)
        light(b+1.5,1,red,'transition',.22 if quiet else .4)
    if si>0:
        event(a,9,0)
        light(a,4,not red,'flash',.85)

# Relax the final chord into a long, stepped fade, then explicitly stop everything.
for t in range(5):
    for b,f in [(374.5,.75),(376,.48),(379,.24),(382,.08)]:
        light(b,t,False,'transition',f)
    event(385,t,0,0)
for t in (12,13): event(375,t,0)

walls=[]; motifs=[]
def wall(b,x,h=3,d=.5,w=1,y=0):
    assert x+w<=-1 or x>=5, 'One empty lane of clearance outside the four play lanes'
    if b+d<=end and b>=0:
        walls.append({'b':round(float(b),4),'x':int(x),'y':int(y),'d':round(float(d),4),'w':int(w),'h':int(h)})
def pair(b,dist=0,h=3,d=.5,w=1,y=0):
    wall(b,-2-dist-(w-1),h,d,w,y); wall(b,5+dist,h,d,w,y)
def snap_note(b,limit=.5):
    n=min(beats,key=lambda n:abs(n-b))
    return n if abs(n-b)<=limit else b

for si,s in enumerate(sections):
    a,z=s['start'],s['end']
    for k,base in enumerate(np.arange(a,z-2,16 if si==0 else 8)):
        b=snap_note(float(base)); mode=(k+si)%4
        # Each motif occupies at most 3 beats, leaving air between gestures.
        if si==0:
            pair(b,1,2 if k%2==0 else 3,1.5)
            if k%2: pair(b+1,2,2,.75,y=1)
            label='intro: pilares abiertos'
        elif mode==0:
            for j in range(4):
                at=snap_note(b+j*.5,.22)
                pair(at,j,2+j%3,.35)
            label='abanico hacia fuera'
        elif mode==1:
            for j,h in enumerate((2,3,4,3)):
                pair(snap_note(b+j*.5,.22),1,h,.4)
            label='onda de alturas'
        elif mode==2:
            for j in range(4):
                at=snap_note(b+j*.5,.22)
                x=-3 if j%2==0 else 6
                wall(at,x,2+int(2*strength(at,'mid')),.6)
            pair(b+2.5,2,3,.65)
            label='respuesta izquierda-derecha'
        else:
            pair(b,2,3,2,w=2,y=1)
            pair(snap_note(b+1,.25),0,2,.45)
            pair(snap_note(b+2,.25),1,4,.45)
            label='marco lateral abierto'
        motifs.append({'beat':b,'section':s['name'],'pattern':label})
# The last chord fans outward; no wall crosses the player or forms a ceiling.
for j in range(3): pair(374.5+j*.5,j+1,4-j,1.2)

out=copy.deepcopy(source)
out['obstacles']=sorted(walls,key=lambda w:(w['b'],w['x']))
out['basicBeatmapEvents']=sorted(events.values(),key=lambda e:(e['b'],e['et']))
normal=next(d for d in info['difficultyBeatmaps'] if d['characteristic']=='Standard' and d['difficulty']=='Normal')
easy=copy.deepcopy(normal); easy['difficulty']='Easy'; easy['beatmapDataFilename']='EasyStandard.dat'
easy.setdefault('customData',{})['difficultyLabel']='BACKUP - Original sin cambios'
if not any(d['difficulty']=='Easy' and d['characteristic']=='Standard' for d in info['difficultyBeatmaps']):
    info['difficultyBeatmaps'].append(easy)

# Validate before any playable file is written.
for key in source:
    if key not in ('obstacles','basicBeatmapEvents'): assert out[key]==source[key],key
assert len({(e['b'],e['et']) for e in out['basicBeatmapEvents']})==len(events)
assert all(w['d']>0 and w['w']>0 and w['h']>0 for w in walls)
assert all(w['x']+w['w']<=-1 or w['x']>=5 for w in walls)
assert all(e['b']<end for e in events.values())
if (root/'EasyStandard.dat').exists():
    assert (root/'EasyStandard.dat').read_bytes()==original, 'Existing Easy has edits'
assert (root/'NormalStandard.dat').read_bytes()==current_map,'Source changed during generation'
assert (root/'Info.dat').read_bytes()==current_info,'Info changed during generation'
if not (root/'EasyStandard.dat').exists(): (root/'EasyStandard.dat').write_bytes(original)
(work/'NormalStandard.decorated.dat').write_text(json.dumps(out,separators=(',',':'),ensure_ascii=False),encoding='utf-8')
(work/'Info.decorated.dat').write_text(json.dumps(info,indent=2,ensure_ascii=False),encoding='utf-8')
(root/'NormalStandard.dat').write_text(json.dumps(out,separators=(',',':'),ensure_ascii=False),encoding='utf-8')
(root/'Info.dat').write_text(json.dumps(info,indent=2,ensure_ascii=False),encoding='utf-8')
report={'walls':len(walls),'lighting_events':len(events),'notes_preserved':len(notes),'bombs_preserved':len(source['bombNotes']),'wall_clearance':'All walls x+w <= -1 or x >= 5; playing lanes [0,4] completely clear with one extra lane each side.','motifs':motifs,'backup':backup['path'],'vr_playtest':False}
(work/'result.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='motifs'},indent=2))
