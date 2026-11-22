"""Procedural loop music with optional voiceover ducking."""
import wave
import numpy as np
STYLES=("ambient","science_ambient","lofi_science","suspense","energetic","pizzicato")
def _root(k):return {"C":0,"C#":1,"D":2,"Eb":3,"E":4,"F":5,"F#":6,"G":7,"Ab":8,"A":9,"Bb":10,"B":11}.get(k,2)
def generate_music(style="science_ambient",bpm=110,key="D",duration=30,seed=None,sample_rate=44100,instruments=None):
 style=style.lower()
 if style not in STYLES:style="science_ambient"
 rng=np.random.default_rng(seed);d=max(1.,float(duration));n=int(d*sample_rate);t=np.arange(n)/sample_rate;root=45+_root(key)
 scale=[0,2,3,5,7,8,10] if style in ("suspense","lofi_science","science_ambient") else [0,2,4,5,7,9,11]
 f=440*2**((root-69)/12)
 out=(np.sin(2*np.pi*f*t)+.35*np.sin(2*np.pi*f*1.5*t)+.2*np.sin(2*np.pi*f*2*t))*(.12+.04*np.sin(2*np.pi*t/5))
 beat=60/max(40,min(220,float(bpm)))
 for bt in np.arange(0,d,beat*2):
  i=int(bt*sample_rate);L=min(int(beat*1.2*sample_rate),n-i);q=np.arange(L)/sample_rate;bf=440*2**((root-24-69)/12)
  out[i:i+L]+=.1*np.sin(2*np.pi*bf*q)*np.exp(-3*q)
 if style in ("energetic","pizzicato","lofi_science"):
  step=beat/2 if style=="energetic" else beat
  for idx,bt in enumerate(np.arange(0,d,step)):
   if style=="energetic" and idx%4 in (1,3):continue
   midi=root+scale[int(rng.integers(len(scale)))]+12;freq=440*2**((midi-69)/12);i=int(bt*sample_rate);L=min(int(.35*sample_rate),n-i);q=np.arange(L)/sample_rate
   out[i:i+L]+=.1*np.exp(-q*7)*np.sin(2*np.pi*freq*q)
 if style=="suspense":out+=.07*np.sin(2*np.pi*(90+15*np.sin(t/7))*t)
 fade=min(int(sample_rate*.8),n//5)
 if fade:out[:fade]*=np.linspace(0,1,fade);out[-fade:]*=np.linspace(1,0,fade)
 return (out/(np.max(np.abs(out)) or 1)*.65).astype(np.float32)
def duck_music(music,voiceover=None,duck_db=-14,voice_activity=None,sample_rate=44100,attack=.04,release=.35):
 a=np.asarray(music,dtype=np.float32).copy()
 if voice_activity is None and voiceover:
  try:
   import librosa
   y,sr=librosa.load(str(voiceover),sr=sample_rate,mono=True);hop=int(sample_rate*.02)
   rms=librosa.feature.rms(y=y,frame_length=2048,hop_length=hop)[0]
   voice_activity=np.interp(np.arange(len(a))/sample_rate,np.arange(len(rms))*hop/sample_rate,rms)
  except Exception:voice_activity=None
 if voice_activity is None:return a
 v=np.asarray(voice_activity,dtype=np.float32)
 if not len(v):return a
 if len(v)!=len(a):v=np.interp(np.arange(len(a)),np.linspace(0,len(a)-1,len(v)),v)
 active=(v>max(.01,float(v.max())*.12)).astype(float);env=np.zeros_like(active);cur=0
 atk=max(1,int(attack*sample_rate));rel=max(1,int(release*sample_rate))
 for i,z in enumerate(active):cur+=(z-cur)/(atk if z>cur else rel);env[i]=cur
 return a*(1-env*(1-10**(float(duck_db)/20)))
def write_music(path,audio,sample_rate=44100):
 pcm=np.clip(np.asarray(audio)*32767,-32768,32767).astype(np.int16)
 with wave.open(str(path),"wb") as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sample_rate);w.writeframes(pcm.tobytes())
 return str(path)
