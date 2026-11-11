import json,hashlib,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent.parent
work=root/'.codex-lighting'
backup=json.loads((work/'backup.json').read_text())
info=json.loads((root/'Info.dat').read_text(encoding='utf-8'))
d=json.loads((root/'NormalStandard.dat').read_text(encoding='utf-8'))
with zipfile.ZipFile(backup['path']) as z:
    old=json.loads(z.read('NormalStandard.dat'))
    assert z.read('NormalStandard.dat')==(root/'EasyStandard.dat').read_bytes()
    oldinfo=json.loads(z.read('Info.dat'))
    assert info['difficultyBeatmaps'][:-1]==oldinfo['difficultyBeatmaps']
    for k in oldinfo:
        if k!='difficultyBeatmaps': assert info[k]==oldinfo[k]
if (work/'before-reapply.zip').exists():
    with zipfile.ZipFile(work/'before-reapply.zip') as z:
        old=json.loads(z.read('NormalStandard.dat'))
for k in old:
    if k not in ('obstacles','basicBeatmapEvents'): assert old[k]==d[k],k
for name,digest in backup['hashes'].items():
    if '/' not in name and name not in ('NormalStandard.dat','Info.dat'):
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
for diff in info['difficultyBeatmaps']:
    for k in ('beatmapDataFilename','lightshowDataFilename'):
        json.loads((root/diff[k]).read_text(encoding='utf-8'))
walls=d['obstacles']; events=d['basicBeatmapEvents']
assert walls==sorted(walls,key=lambda w:(w['b'],w['x']))
assert events==sorted(events,key=lambda e:(e['b'],e['et']))
assert len(set((e['b'],e['et']) for e in events))==len(events)
assert all(w['x']+w['w']<=-1 or w['x']>=5 for w in walls)
# Check concurrent geometry at the player's plane and same-side overlaps.
max_active=0; overlaps=[]
for i,w in enumerate(walls):
    active=[o for o in walls if o['b']<=w['b']<o['b']+o['d']]
    max_active=max(max_active,len(active))
    for o in walls[i+1:]:
        if o['b']>=w['b']+w['d']: break
        if (max(w['x'],o['x'])<min(w['x']+w['w'],o['x']+o['w']) and
            max(w['y'],o['y'])<min(w['y']+w['h'],o['y']+o['h'])):
            overlaps.append((w,o))
assert not overlaps,overlaps
assert all(any(e['et']==t and e['i']==0 and e['b']==385 for e in events) for t in range(5))
print(json.dumps({'status':'PASS','original_exact_copy':True,'latest_notes_bombs_timing_bookmarks_preserved':True,'other_root_original_files_unchanged':True,'all_references_parse':True,'wall_play_lane_intersections':0,'wall_geometry_overlaps':len(overlaps),'max_walls_at_player_plane':max_active,'events':len(events),'walls':len(walls),'vr_playtest':'not performed'},indent=2))
