"""Curated scene palettes with contrast-aware foreground suggestions."""
from __future__ import annotations
import colorsys

_BASE = {
 "deep_ocean":((12,24,52),(240,247,255),(42,190,255),(255,184,62)),
 "golden_punch":((255,196,40),(24,30,46),(232,72,45),(255,245,206)),
 "purple_lab":((38,22,68),(248,244,255),(184,95,255),(70,225,255)),
 "bio_green":((12,48,38),(240,255,245),(83,230,148),(255,213,80)),
 "warm_paper":((247,232,205),(35,36,42),(214,74,53),(255,180,60)),
 "ice_science":((214,242,255),(20,38,58),(30,140,225),(255,92,112)),
 "alert_coral":((255,104,92),(34,28,38),(255,222,72),(255,230,225)),
 "ink_mono":((28,30,36),(245,245,242),(170,190,210),(90,230,220)),
 "electric_yellow":((250,232,40),(30,34,42),(255,75,55),(55,160,245)),
 "blueprint":((24,70,130),(242,250,255),(255,220,65),(92,205,255)),
 "crimson_drama":((68,12,26),(255,242,235),(255,88,112),(255,205,80)),
 "fresh_mint":((205,250,225),(25,45,40),(20,150,120),(255,130,72)),
}
def _adjust(c, factor):
 return tuple(max(0,min(255,int(v*factor))) for v in c)
def _lum(c):
 r,g,b=[v/255 for v in c]
 return 255*(.2126*r+.7152*g+.0722*b)
def _contrast(a,b):
 la,lb=_lum(a),_lum(b)
 hi,lo=max(la,lb),min(la,lb)
 return (hi+12.5)/(lo+12.5)
def _make(base, i):
 bg,fg,accent,secondary=base
 # Variations preserve hue families; shift lightness/saturation deterministically.
 shift=(i-4.5)*.045
 def tweak(c):
  h,l,s=colorsys.rgb_to_hls(*(v/255 for v in c))
  l=max(.12,min(.88,l+shift))
  return tuple(int(v*255) for v in colorsys.hls_to_rgb(h,l,s))
 b=tweak(bg); f=tweak(fg); a=tweak(accent); sec=tweak(secondary)
 lum=_lum(b)
 ink=(20,22,30)
 stroke=ink if lum>140 else None
 shadow=_adjust(b,.28) if lum>110 else _adjust(b,1.7)
 badge= f if _contrast(b,f)>=3 else (255,255,255) if lum<128 else (20,22,30)
 return {"bg":b,"text":f,"accent":a,"secondary":sec,"shadow":shadow,
         "stroke":stroke,"badge":badge,"badge_text":b,"lum":lum}
PALETTES={}
for family,base in _BASE.items():
 for n in range(10):
  PALETTES[f"{family}_{n+1:02d}"]=_make(base,n)
PALETTE_FAMILIES=tuple(_BASE)
def get_palette(name="deep_ocean_01"):
 if name in PALETTES:return dict(PALETTES[name])
 if name in _BASE:return _make(_BASE[name],4)
 raise KeyError(f"Unknown palette: {name}")
def list_palettes(family=None):
 return tuple(k for k in PALETTES if family is None or k.startswith(family+"_"))
def luminance(color):
 return _lum(tuple(color))
def contrast_ratio(a,b):
 return _contrast(tuple(a),tuple(b))
def safe_text_colors(bg, text_color=None):
 bg=tuple(bg); lum=_lum(bg)
 ink=(20,22,31); white=(250,250,250)
 text_color=tuple(text_color) if text_color else (white if lum<130 else ink)
 # Enforce readable contrast and avoid dirty white stroke.
 if _contrast(bg,text_color)<3.0:
  text_color=white if lum<130 else ink
 stroke=ink if lum>140 else None
 return {"text":text_color,"stroke":stroke,"shadow":_adjust(bg,.25 if lum>110 else 1.65),
         "badge_required":lum<90,"badge":white if lum<128 else ink}
