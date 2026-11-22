"""Procedural SFX generator (NumPy, standard-library WAV writer)."""
import wave
import numpy as np
SFX_NAMES=("impact_thud impact_heavy impact_soft impact_boom impact_cartoon impact_snap impact_slam impact_knock impact_crash impact_punch whoosh_fast whoosh_slow whoosh_reverse whoosh_rise whoosh_fall whip_transition swipe_left swipe_right air_sweep zoom_whoosh pop_bubble ding_idea notification_ping click_soft click_heavy button_press error_buzz success_chime warning_beep confirm_tone electric_zap electric_arc laser_charge laser_shot energy_pulse power_up power_down glitch_short glitch_long sci_fi_scan heartbeat heartbeat_fast crunch_bite crunch_snap steam_hiss bubble_pop liquid_pour gulp stomach_growl breath_short clock_tick clock_tock gear_turn metal_clank spring_boing rubber_bounce cash_register coin_drop glass_tap object_roll".split())
SFX_PRESETS={n:{"label":n} for n in SFX_NAMES}
EVENTS=[]
def _norm(a,peak=.9):
 a=np.asarray(a,dtype=np.float32);m=float(np.max(np.abs(a))) if len(a) else 0
 return a*(peak/m) if m>1e-8 else a
def render_sfx(name,duration=None,intensity=1,seed=None,sample_rate=44100):
 if name not in SFX_PRESETS:raise KeyError(name)
 rng=np.random.default_rng(seed);d=max(.025,min(5,float(duration or .4)));t=np.arange(int(d*sample_rate))/sample_rate;n=len(t);noise=rng.normal(0,1,n);tone=lambda f:np.sin(2*np.pi*f*t)
 env=np.exp(-t*(8 if d<.3 else 4));kind=name
 if any(x in kind for x in ("whoosh","swipe","sweep","whip")):sig=noise*.3+tone(200+1600*t/d);env=np.sin(np.pi*np.clip(t/d,0,1))
 elif any(x in kind for x in ("heartbeat",)):sig=tone(60+20*np.sin(t*25))+tone(90);env=np.exp(-t*15)*(np.exp(-((t-.04)/.035)**2)+.7*np.exp(-((t-.28)/.05)**2))
 elif any(x in kind for x in ("zap","arc","laser","electric")):sig=tone(350+3000*np.exp(-t*16))+noise*.4;env=np.exp(-t*8)
 elif any(x in kind for x in ("tick","tock","click","knock","tap","press")):sig=noise;env=np.exp(-t*55)
 elif any(x in kind for x in ("ding","chime","ping","register","coin")):sig=tone(740)+.5*tone(1480)+.2*tone(2220);env=np.exp(-t*5)
 elif any(x in kind for x in ("crunch","bite","snap","crash")):sig=noise+.3*tone(110);env=np.exp(-t*18)
 elif any(x in kind for x in ("steam","breath","pour","gulp")):sig=noise;env=np.exp(-t*3)*.3
 elif any(x in kind for x in ("buzz","error","warning","glitch")):sig=np.sign(tone(120+80*np.sin(20*t)))+noise*.3;env=np.exp(-t*5)
 elif any(x in kind for x in ("spring","bounce","boing")):sig=tone(220+100*np.sin(18*t));env=np.exp(-t*6)*np.abs(np.sin(20*t))
 else:sig=tone(100)+.4*tone(240)+noise*.15;env=np.exp(-t*5)
 return _norm(sig*env*float(intensity))
def write_wav(path,audio,sample_rate=44100):
 pcm=np.clip(np.asarray(audio)*32767,-32768,32767).astype(np.int16)
 with wave.open(str(path),"wb") as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sample_rate);w.writeframes(pcm.tobytes())
 return str(path)
def render_to_file(name,path,**kw):write_wav(path,render_sfx(name,**kw),kw.get("sample_rate",44100));return path
def trigger(name,at=0,duration=None,intensity=1,seed=None):
 e={"name":name,"at":max(0,float(at)),"duration":duration,"intensity":intensity,"seed":seed};EVENTS.append(e);return e
def clear_events():EVENTS.clear()
def render_events(events=None,total_duration=None,sample_rate=44100):
 ev=list(EVENTS if events is None else events);end=max([e["at"]+(e.get("duration") or .4) for e in ev]+[float(total_duration or 0)]);out=np.zeros(int(end*sample_rate),np.float32)
 for e in ev:
  clip=render_sfx(e["name"],e.get("duration"),e.get("intensity",1),e.get("seed"),sample_rate);i=int(e["at"]*sample_rate);j=min(len(out),i+len(clip))
  if j>i:out[i:j]+=clip[:j-i]
 return _norm(out,.95)
class SFX:
 trigger=staticmethod(trigger);render=staticmethod(render_sfx);events=staticmethod(lambda:list(EVENTS))
