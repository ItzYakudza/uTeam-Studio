"""Contrast-safe text treatments for the uTeam-Studio drawing Canvas."""
from __future__ import annotations
from .palettes import PALETTES, get_palette, luminance, safe_text_colors
STYLE_FAMILIES=("comic_punch","neon_glow","sticker_tag","kinetic_word","warning_stamp",
 "gradient_fill","split_color","impact_title","soft_caption","bold_underline","floating_label","double_shadow")
TEXT_STYLES={}
for family in STYLE_FAMILIES:
 for i in range(10):
  TEXT_STYLES[f"{family}_{i+1:02d}"]={"family":family,"variant":i+1}
def style(name):
 if name in TEXT_STYLES:return dict(TEXT_STYLES[name])
 if name in STYLE_FAMILIES:return {"family":name,"variant":1}
 raise KeyError(name)
def resolve_style(name, bg, text_color=None, accent=None):
 s=style(name); colors=safe_text_colors(bg,text_color)
 lum=luminance(bg)
 # Dark ink stroke only on light backgrounds; never use white outline.
 s.update(colors)
 s["accent"]=tuple(accent) if accent else (255,170,35)
 s["stroke_width"]=0 if lum<90 else (3 if lum>140 else 0)
 s["shadow_offset"]=(5,5)
 s["badge"]=bool(colors["badge_required"] or s["family"] in ("sticker_tag","warning_stamp"))
 return s
def draw_text(cv,x,y,label,size=48,style_name="impact_title",color=None,bg=None,accent=None,shadow=True,**kw):
 from .primitives import text, rrect
 bg=tuple(bg or cv.bg); s=resolve_style(style_name,bg,color,accent)
 family=s["family"]; col=s["text"]; stroke=s.get("stroke")
 if family=="split_color":
  # Two-color keyword treatment via safe badge is preferred for legacy Canvas.
  s["badge"]=True
 if s["badge"]:
  # Text metrics via PIL; keep drawing helpers compatible with legacy canvas.
  from .primitives import get_font
  f=get_font(int(size)); box=f.getbbox(str(label)); tw=box[2]-box[0]; th=box[3]-box[1]
  pad=max(10,int(size*.22)); rr=max(8,int(size*.18))
  rrect(cv,x-tw/2-pad,y-th/2-pad/2,x+tw/2+pad,y+th/2+pad/2,rr,
        s["badge"],0)
 if shadow:
  text(cv,x+s["shadow_offset"][0],y+s["shadow_offset"][1],label,size,s["shadow"],**kw)
 text(cv,x,y,label,size,col,**kw)
 return s
def draw_split(cv,x,y,before,keyword,after,size=48,style_name="split_color",color=None,accent=None,**kw):
 from .primitives import text,twidth
 base=tuple(color or (24,28,34)); hot=tuple(accent or (240,90,45))
 full=before+keyword+after; total=twidth(full,size); left=x-total/2
 text(cv,left+twidth(before,size)/2,y,before,size,base,**kw)
 text(cv,left+twidth(before,size)+twidth(keyword,size)/2,y,keyword,size,hot,**kw)
 text(cv,left+twidth(before+keyword,size)+twidth(after,size)/2,y,after,size,base,**kw)
def palette_style(name,palette_name="deep_ocean_01"):
 p=get_palette(palette_name)
 return resolve_style(name,p["bg"],p["text"],p["accent"])
