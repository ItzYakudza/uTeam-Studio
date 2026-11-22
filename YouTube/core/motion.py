"""Deterministic object and camera motion helpers."""
import math
MOTION_NAMES=("elastic_pop squash_and_stretch anticipation_jump heartbeat_pulse camera_impact_shake whip_pan dolly_zoom float_idle orbit_around shatter_burst bounce overshoot settle spring pendulum shake wobble rotate_in flip spin fade_in fade_out slide_in slide_out rise drop drift follow_path smooth_follow magnetic_pull repulsion gravity_fall friction_stop particle_burst reassemble reveal_wipe mask_reveal wave_motion ripple swing stagger chain_reaction time_freeze camera_zoom zoom_punch smooth_zoom camera_pan camera_tilt camera_follow camera_track camera_orbit camera_roll camera_rack_focus parallax_shift push_in pull_out crash_zoom handheld_noise camera_recoil cinematic_reframe".split()
EASING_NAMES=("ease_out_cubic ease_in_cubic ease_in_out_cubic ease_out_back ease_out_elastic ease_in_out_sine smoothstep damped_spring".split())
def clamp(x,a=0,b=1):return max(a,min(b,x))
def ease(t,kind="ease_out_cubic"):
 x=clamp(t)
 if kind=="ease_in_cubic":return x**3
 if kind=="ease_in_out_cubic":return 4*x**3 if x<.5 else 1-(-2*x+2)**3/2
 if kind=="ease_out_back":return 1+2.70158*(x-1)**3+1.70158*(x-1)**2
 if kind=="ease_out_elastic":return x if x in (0,1) else 2**(-10*x)*math.sin((10*x-.75)*2*math.pi/3)+1
 if kind=="ease_in_out_sine":return -(math.cos(math.pi*x)-1)/2
 if kind=="smoothstep":return x*x*(3-2*x)
 if kind=="damped_spring":return 1-math.exp(-7*x)*math.cos(11*x)
 return 1-(1-x)**3
def elastic_pop(t,d=.45):return ease(t/max(d,1e-6),"ease_out_elastic")
def squash_and_stretch(t,impact=.35):p=math.exp(-((t-impact)/.12)**2);return {"sx":1+.28*p,"sy":1-.24*p}
def anticipation_jump(t,d=1):x=clamp(t/d);j=math.sin(math.pi*clamp((x-.2)/.8)) if x>.2 else 0;return {"y":-160*j+35*math.sin(math.pi*min(x/.2,1))*(x<.2),"sx":1-.12*j,"sy":1+.12*j}
def heartbeat_pulse(t,amp=.08):return 1+amp*(math.exp(-((t%1)-.16)**2/.012)+.65*math.exp(-((t%1)-.34)**2/.018))
def float_idle(t,amp=8,speed=1):return {"y":amp*math.sin(t*speed*math.tau),"rot":2*math.sin(t*speed*math.pi)}
def bounce(t,frequency=2.5,decay=4):return abs(math.sin(t*frequency*math.pi))*math.exp(-decay*max(t,0))
def pendulum(t,amplitude=25,period=1.5):return amplitude*math.sin(t*math.tau/max(period,.01))
def shake(t,amplitude=8,frequency=18,decay=5):return {"x":amplitude*math.sin(t*frequency)*math.exp(-decay*t),"y":amplitude*.65*math.cos(t*frequency*1.3)*math.exp(-decay*t)}
def orbit_around(t,radius=60,speed=1,phase=0):return {"x":radius*math.cos(t*speed+phase),"y":radius*math.sin(t*speed+phase)}
def gravity_fall(t,g=900,velocity=0):return {"y":velocity*t+.5*g*t*t}
def friction_stop(t,velocity=500,friction=5):return velocity*(1-math.exp(-friction*t))/friction
def magnetic_pull(t,distance=200,strength=7):return {"x":distance*math.exp(-strength*max(t,0))}
def repulsion(t,distance=100,strength=6):return {"x":distance*(1-math.exp(-strength*max(t,0)))}
def shatter_burst(t,d=1,n=12,radius=180):p=clamp(t/d);return [{"x":radius*p*math.cos(i*math.tau/n),"y":radius*p*math.sin(i*math.tau/n),"rot":i*36*p,"alpha":1-p} for i in range(n)]
def particle_burst(t,n=20,radius=160,d=1):p=clamp(t/d);return [{"x":radius*p*math.cos(i*math.tau/n),"y":radius*p*math.sin(i*math.tau/n),"alpha":1-p} for i in range(n)]
def reassemble(t,d=1):return 1-ease(t/d,"ease_out_back")
def ripple(t,radius=100,speed=280):return {"radius":speed*t,"alpha":max(0,1-t/max(radius/speed,1e-3))}
def wave_motion(t,amp=20,frequency=2):return {"y":amp*math.sin(t*frequency*math.tau)}
def stagger(t,index=0,gap=.12,d=.4):return ease(clamp((t-index*gap)/d),"ease_out_back")
def time_freeze(t,at=.5):return 0 if t>=at else t
def camera_impact_shake(t,intensity=1,d=.4):return {"dx":intensity*14*math.sin(t*70)*math.exp(-8*t),"dy":intensity*10*math.cos(t*57)*math.exp(-8*t)}
def whip_pan(t,d=.3,direction=1):return {"dx":direction*900*(1-clamp(t/d)),"blur":math.sin(math.pi*clamp(t/d))}
def dolly_zoom(t,amount=.2,d=1):return {"zoom":1+amount*math.sin(math.pi*clamp(t/d))}
def camera_zoom(t,start=1,end=1.2,d=1):return {"zoom":start+(end-start)*ease(t/d)}
def zoom_punch(t,amount=.22,d=.35):return {"zoom":1+amount*math.exp(-8*t)*math.sin(20*t)}
def smooth_zoom(t,start=1,end=1.2,d=1):return {"zoom":start+(end-start)*ease(t/d,"ease_in_out_cubic")}
def camera_pan(t,x=0,y=0,d=1):p=ease(t/d);return {"dx":x*p,"dy":y*p}
def camera_tilt(t,angle=8,d=1):return {"rot":angle*ease(t/d)}
def camera_track(t,x0=0,y0=0,x1=0,y1=0,d=1):p=ease(t/d);return {"dx":x0+(x1-x0)*p,"dy":y0+(y1-y0)*p}
def camera_orbit(t,r=20,speed=1):return {"dx":r*math.cos(t*speed),"dy":r*math.sin(t*speed)}
def camera_roll(t,angle=4,d=1):return {"rot":angle*ease(t/d)}
def camera_rack_focus(t,near=0,far=1,d=1):return {"focus":near+(far-near)*ease(t/d)}
def parallax_shift(t,depth=1,x=100,y=0):p=ease(t);return {"dx":x*depth*p,"dy":y*depth*p}
def push_in(t,d=1,zoom=1.15):return camera_zoom(t,1,zoom,d)
def pull_out(t,d=1,zoom=.9):return camera_zoom(t,1,zoom,d)
def crash_zoom(t,amount=.45):return {"zoom":1+amount*math.exp(-10*t)}
def handheld_noise(t,seed=0,amount=2):return {"dx":amount*math.sin(19*t+seed),"dy":amount*math.cos(23*t+seed*2)}
def camera_recoil(t,amount=18):return {"dx":amount*math.exp(-12*t)*math.sin(26*t),"zoom":1+.05*math.exp(-8*t)}
def cinematic_reframe(t,x=0,y=0,zoom=1.1,d=1):p=ease(t/d,"ease_in_out_sine");return {"dx":x*p,"dy":y*p,"zoom":1+(zoom-1)*p}
# Remaining named presets are callable and use a consistent eased progress interface.
def _generic(name):
 def fn(t,d=1,**kw):
  p=ease(t/d,kw.get("ease","ease_out_cubic"))
  if name in ("fade_in","reveal_wipe","mask_reveal"):return p
  if name in ("fade_out",):return 1-p
  if name in ("slide_in","rise"):return {"y":(1-p)*kw.get("distance",90)}
  if name in ("slide_out","drop"):return {"y":p*kw.get("distance",90)}
  if name in ("spin","rotate_in"):return {"rot":360*p}
  if name=="flip":return {"sx":math.cos(math.pi*p)}
  if name in ("overshoot","settle","spring"):return ease(p,"ease_out_back")
  if name=="drift":return float(kw.get("amplitude",8))*math.sin(t*2)
  return p
 fn.__name__=name;return fn
for _name in MOTION_NAMES:
 if _name not in globals():globals()[_name]=_generic(_name)
def apply(name,t,**kw):
 if name not in MOTION_NAMES and name not in EASING_NAMES:raise KeyError(name)
 return globals()[name](t,**kw)
