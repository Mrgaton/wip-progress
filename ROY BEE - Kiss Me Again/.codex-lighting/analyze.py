import json, hashlib, zipfile
from pathlib import Path
from datetime import datetime
import numpy as np
import soundfile as sf
from scipy import signal

root = Path(__file__).resolve().parent.parent
work = root / '.codex-lighting'
backup = root / 'backups' / ('before-lighting-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.zip')
backup.parent.mkdir(exist_ok=True)
files = [p for p in root.rglob('*') if p.is_file() and not any(x in p.relative_to(root).parts for x in ['backups', '.codex-lighting'])]
manifest = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
with zipfile.ZipFile(backup, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in files: z.write(p, p.relative_to(root))
    z.writestr('backup-sha256.json', json.dumps(manifest, indent=2))
with zipfile.ZipFile(backup) as z:
    assert z.testzip() is None
    assert all(hashlib.sha256(z.read(n)).hexdigest() == h for n,h in manifest.items())
(work/'backup.json').write_text(json.dumps({'path':str(backup), 'hashes':manifest},indent=2))
d=json.loads((root/'NormalStandard.dat').read_text())
y,sr=sf.read(root/'ROYBEEKissMeAgain.ogg',dtype='float32')
y=signal.resample_poly(y.mean(axis=1),1,4); sr=sr//4
freq,t,Z=signal.stft(y,fs=sr,nperseg=1024,noverlap=904)
S=abs(Z)
bands={}
for name,lo,hi in [('bass',35,200),('mid',250,3500),('high',3500,5800),('full',35,5800)]:
    A=S[(freq>=lo)&(freq<hi)]
    env=np.maximum(np.diff(np.log1p(A*100),axis=1),0).mean(axis=0)
    env=np.r_[0,env]
    bands[name]=env
env=bands['full']; dt=t[1]-t[0]
ac=signal.correlate(env-env.mean(),env-env.mean(),mode='full',method='fft')[len(env)-1:]
lags=np.arange(int(60/190/dt),int(60/140/dt)+1)
lag=lags[np.argmax(ac[lags])]
# Refined grid fit: accumulate onset energy over every beat for candidate tempi/phases.
candidates=np.arange(164,169.001,.01); phases=np.arange(0,.360,.003)
scores=[]
for bpm in candidates:
    times=np.arange(3,370)*60/bpm
    vals=np.array([np.interp(times+p,t,bands['bass']).mean() for p in phases])
    i=vals.argmax(); scores.append((float(vals[i]),float(bpm),float(phases[i])))
best=max(scores)
bpm=166.48
notes=sorted(set(n['b'] for n in d['colorNotes']))
peaks,_=signal.find_peaks(env,distance=8,prominence=np.percentile(env,65)*.6)
pt=t[peaks]
errors=[float(np.min(abs(pt-b*60/bpm))) for b in notes if len(pt)]
sections=[]
marks=d['customData']['bookmarks']
for i,m in enumerate(marks):
    a=m['b']; b=marks[i+1]['b'] if i+1<len(marks) else 375
    mask=(t>=a*60/bpm)&(t<b*60/bpm)
    sections.append({'start':a,'end':b,'name':m['n'],'rms':float(np.sqrt(np.mean(y[int(a*60/bpm*sr):int(b*60/bpm*sr)]**2))),'onset':float(env[mask].mean()),'notes':sum(a<=n['b']<b for n in d['colorNotes'])})
report={'backup':str(backup),'duration':len(y)/sr,'bpm_existing':bpm,'bpm_autocorrelation':60/(lag*dt),'bpm_grid_fit':best[1],'onset_phase_seconds':best[2],'note_onset_error_median_ms':float(np.median(errors)*1000),'note_onsets_within_60ms':float(np.mean(np.array(errors)<.060)),'sections':sections,'method':'Spectral flux by frequency band; bass periodicity and grid fit. Mid band is not isolated vocals. Existing note timings and bookmarks retained.'}
(work/'analysis.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
np.savez_compressed(work/'features.npz',t=t,**bands)
print(json.dumps(report,indent=2))
