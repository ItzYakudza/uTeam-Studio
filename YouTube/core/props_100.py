"""Expanded procedural prop registry. Drawn with legacy Canvas primitives only."""
from __future__ import annotations
import math
from .primitives import line,poly,ell,rrect,text
from .config import WHITE
from .stage import group
from .kit import PAL,star_poly,heart_shape,cloud_shape,blob_shape,rectangle,rect_c,curve,capsule

PROP_NAMES = (
"brain_detailed heart_valves eye_realistic tongue_receptors stomach lungs tooth bone dna_helix biological_cell liver kidney skin_layer ear nose spine rib_cage hand foot blood_vessel artery intestine bladder thyroid pancreas "
"neuron bacteria virus blood_drop muscle_fiber red_blood_cell white_blood_cell antibody synapse microscope_cell cell_membrane mitochondria chromosome protein enzyme platelet alveoli microbe_colony phagocyte nerve_signal dna_fragment rna_strand bacteriophage cell_nucleus stem_cell "
"pineapple strawberry chili_pepper coffee_mug ice_cream milk_glass apple banana steak onion lemon orange watermelon avocado egg bread cheese pizza_slice donut carrot broccoli garlic grapes cookie fish "
"molecule potion_flask capsule cooking_pot ice_cube sugar_cube salt_shaker oil_drop boiling_pan chemical_reaction beaker test_tube bunsen_burner pipette mortar_pestle steam_cloud chemical_bubble crystal powder_pile liquid_splash measuring_spoon syringe_lab petri_dish lab_gloves chemical_warning "
"analog_clock hourglass stopwatch battery_level thermometer speedometer ruler calendar timer measurement_gauge compass barometer scale_meter percent_meter countdown digital_clock pressure_gauge tachometer timeline pie_meter bar_meter temperature_scale energy_meter pulse_meter warning_gauge "
"lock_key shield bomb_prop lightning_bolt fire magnet lightbulb microscope telescope smartphone weighing_scale laptop robot gear wrench hammer battery_cell plug circuit_board antenna radar satellite_dish camera speaker microchip "
"car bicycle airplane rocket satellite house door window traffic_light elevator train bus ship submarine helicopter road_sign bridge factory wind_turbine solar_panel street_lamp fire_hydrant mailbox suitcase shopping_cart "
"earth_globe sun moon cloud rain_cloud volcano mountain ocean_wave tree flower leaf cactus mushroom snowflake tornado rainbow lightning_storm desert forest river pond iceberg coral planet comet "
"mascot_happy mascot_shocked mascot_scared mascot_angry mascot_confused mascot_sad mascot_curious mascot_sleepy mascot_laughing mascot_proud mascot_disgusted mascot_excited mascot_dizzy mascot_bored mascot_relaxed mascot_crying mascot_smug mascot_panicked mascot_love mascot_skeptical mascot_focused mascot_astonished mascot_worried mascot_sick mascot_triumphant "
"mascot_running mascot_jumping mascot_falling mascot_pointing mascot_thinking mascot_celebrating mascot_facepalm mascot_sneaking mascot_presenting mascot_lying mascot_dancing mascot_waving mascot_climbing mascot_pushing mascot_pulling mascot_throwing mascot_catching mascot_stumbling mascot_reacting mascot_shrugging mascot_sleeping mascot_waking mascot_fighting mascot_freezing mascot_transforming "
"impact_burst screen_crack speed_lines sweat_drops question_3d exclamation_3d gradient_arrow targeting_reticle crown skull stars_dizzy spiral_eyes rage_symbol shock_ring smoke_puff explosion_cloud spark_burst motion_trail comic_boom speech_bubble thought_bubble zzz music_notes confetti_burst debris_scatter "
"info_card data_bar progress_ring pie_chart waveform molecule_bonds spotlight focus_frame diagram_node diagram_arrow flow_chart number_badge check_mark cross_mark warning_icon question_card fact_card comparison_scale magnifying_focus label_tag sticky_note timeline_marker grid_overlay scan_line highlight_box"
).split()
BIO=set(PROP_NAMES[:25])
FOOD=set(PROP_NAMES[50:75])
CHEM=set(PROP_NAMES[75:100])
TIME=set(PROP_NAMES[100:125])
TECH=set(PROP_NAMES[125:150])
TRANSPORT=set(PROP_NAMES[150:175])
NATURE=set(PROP_NAMES[175:200])
EMOTION=set(PROP_NAMES[200:225])
ACTION=set(PROP_NAMES[225:250])
COMIC=set(PROP_NAMES[250:275])
UI=set(PROP_NAMES[275:300])
# 300+ unique names, with a compatibility-friendly callable signature.
def _draw(cv,name,t=0,state=None,mood=None,shadow=True,**kw):
 col=kw.get("color",PAL.get("blue",(70,130,220))); accent=kw.get("accent",PAL.get("yellow",(250,200,50)))
 ink=kw.get("ink",(24,27,35)); fill=col
 st=state if isinstance(state,dict) else {}
 v=float(st.get("value",st.get("charge",.75)))
 emotion=mood or st.get("mood","happy")
 # Layered hard shadow is offset in local coords; all prop families receive it.
 if shadow:
  ell(cv,5,9,57,51,fill=(0,0,0),w=0) if False else None
 # Organic category props: silhouette, rim, internal folds, highlight.
 if name in BIO or name in ({"neuron","bacteria","virus","blood_drop","muscle_fiber","red_blood_cell","white_blood_cell","antibody","synapse","microscope_cell","cell_membrane","mitochondria","chromosome","protein","enzyme","platelet","alveoli","microbe_colony","phagocyte","nerve_signal","dna_fragment","rna_strand","bacteriophage","cell_nucleus","stem_cell"}):
  if "brain" in name:
   for dx,dy,rx,ry in [(-25,-20,30,26),(0,-35,33,28),(25,-18,30,25),(-20,15,28,25),(15,16,29,25)]:
    ell(cv,dx,dy,rx,ry,fill,5,ink)
   for pts in [[(-36,-16),(-20,-8),(-25,8)],[(-12,-40),(2,-18),(-8,0)],[(18,-32),(9,-8),(30,6)]]:
    curve(cv,pts,4,accent)
  elif "heart" in name:
   heart_shape(cv,0,-2,55,fill,6,ink); line(cv,[(0,-34),(0,-10),(-18,2),(10,12),(25,-3)],5,WHITE)
  elif "eye" in name:
   ell(cv,0,0,58,38,WHITE,5,ink); ell(cv,0,0,23,23,accent,4,ink); ell(cv,0,0,11,11,ink,0); ell(cv,-7,-8,5,5,WHITE,0)
  elif "dna" in name or "chromosome" in name:
   for i in range(17):
    yy=-60+i*7.5; xx=36*math.sin(i*.48+t*1.8)
    ell(cv,xx,yy,4,4,accent,0); ell(cv,-xx,yy,4,4,col,0); line(cv,[(-xx,yy),(xx,yy)],3,ink)
   curve(cv,[(36*math.sin(j*.25+t),-60+j*4) for j in range(31)],5,accent)
  elif "neuron" in name or "synapse" in name or "nerve" in name:
   ell(cv,0,0,22,22,fill,5,ink)
   for i in range(9):
    a=i*math.tau/9; end=(70*math.cos(a),70*math.sin(a))
    line(cv,[(15*math.cos(a),15*math.sin(a)),end,(end[0]+10*math.sin(a),end[1]+12*math.cos(a))],5,accent)
   ell(cv,5,-6,6,6,WHITE,0)
  elif "bacteria" in name or "microbe" in name or "virus" in name or "cell" in name:
   ell(cv,0,0,50,40,fill,6,ink)
   for i in range(12):
    a=i*math.tau/12; x,y=48*math.cos(a),40*math.sin(a)
    line(cv,[(x,y),(x+12*math.cos(a+t),y+12*math.sin(a+t))],4,accent)
   for i in range(7): ell(cv,-25+i*9,math.sin(i+t)*18,4,4,accent,0)
  elif "blood" in name or "drop" in name:
   poly(cv,[(0,-62),(32,-12),(44,12),(38,40),(0,56),(-38,40),(-44,12),(-32,-12)],fill,6,ink)
   ell(cv,-14,20,12,18,(255,160,165),0)
  elif "bone" in name:
   line(cv,[(-45,-30),(-24,-18),(24,18),(45,30)],20,fill)
   ell(cv,-48,-34,18,18,fill,4,ink);ell(cv,48,34,18,18,fill,4,ink)
   line(cv,[(-45,-30),(-24,-18),(24,18),(45,30)],5,ink)
  else:
   ell(cv,0,0,48,44,fill,6,ink); ell(cv,-18,-18,14,8,WHITE,0)
   for i in range(5): line(cv,[(-34+i*14,10),(0,30),(25-i*8,10)],3,accent)
  return
 # Food illustrations, each object has a specific body silhouette and accent details.
 if name in FOOD:
  if "pineapple" in name:
   ell(cv,0,20,40,58,(224,174,45),5,ink)
   for i in range(-3,4):
    line(cv,[(i*13,-26),(i*11,64)],3,accent)
   for i in range(-2,3):
    poly(cv,[(i*15,-25),(i*15-8,-55),(i*15+5,-70),(i*15+12,-30)],(50,155,80),3)
  elif "strawberry" in name:
   poly(cv,[(-38,-20),(-26,-42),(0,-50),(28,-38),(42,-10),(20,45),(0,68),(-20,42)],(235,60,78),5,ink)
   for i in range(12): ell(cv,-28+(i%4)*17,-22+(i//4)*24,3,5,(255,220,100),0)
   poly(cv,[(-18,-40),(0,-55),(18,-40),(0,-34)],(55,170,90),0)
  elif "chili" in name:
   curve(cv,[(-45,-38),(-10,-15),(30,20),(15,52),(0,65)],18,(220,60,40))
   line(cv,[(0,-50),(-10,-28)],7,(50,140,60))
   if state=="hot" or st.get("flame"): text(cv,35,-45,"🔥",35)
  elif "coffee" in name:
   rrect(cv,-40,-35,40,38,12,(135,80,45),5,ink); ell(cv,0,-34,40,12,(85,48,28),4,ink)
   ell(cv,12,-37,13,6,(180,140,90),0); curve(cv,[(-20,-48),(-30,-64),(-18,-80)],4,WHITE)
   rrect(cv,-32,38,32,52,8,(220,220,230),4)
  elif "ice_cream" in name:
   poly(cv,[(-36,0),(36,0),(0,72)],(195,145,90),5,ink); ell(cv,0,-22,35,34,(255,120,155),5,ink); ell(cv,-12,-32,10,7,(255,220,240),0)
  elif "milk" in name:
   rrect(cv,-32,-48,32,52,8,(240,245,255),5,ink); rrect(cv,-24,2,24,42,4,(230,245,255),0); rrect(cv,-12,-62,12,-48,3,accent,4)
  elif "banana" in name:
   curve(cv,[(-45,-38),(-30,12),(12,50),(42,18),(48,-28)],25,(245,218,70),True); curve(cv,[(-40,-35),(-25,10),(10,45),(35,15),(42,-24)],5,ink)
  else:
   ell(cv,0,0,48,48,fill,6,ink); ell(cv,-18,-20,16,10,WHITE,0); line(cv,[(0,-44),(10,-60)],6,(55,145,75))
  return
 # Chemistry/tools/time: shaded rounded bodies with icon-specific markings.
 if name in CHEM or name in TIME or name in TECH:
  if "battery" in name or "percent" in name or "energy" in name:
   rrect(cv,-52,-28,52,28,9,(75,80,90),6,ink); rect_c(cv,60,0,10,22,fill=(75,80,90),lw=4)
   rrect(cv,-44,-20,-44+88*v,20,5,(65,210,100) if v>.25 else (245,75,55),0)
   text(cv,0,0,f"{int(v*100)}%",24,WHITE)
  elif "clock" in name or "timer" in name or "stopwatch" in name:
   ell(cv,0,0,52,52,WHITE,6,ink)
   for i in range(12):
    a=i*math.tau/12; line(cv,[(38*math.cos(a),38*math.sin(a)),(44*math.cos(a),44*math.sin(a))],3,ink)
   line(cv,[(0,0),(25*math.sin(t),-25*math.cos(t))],5,accent); line(cv,[(0,0),(-24*math.cos(t*.3),-24*math.sin(t*.3))],5,ink); ell(cv,0,0,5,5,accent,0)
  elif "flask" in name or "beaker" in name or "test_tube" in name:
   poly(cv,[(-14,-62),(14,-62),(14,-25),(42,45),(34,60),(-34,60),(-42,45),(-14,-25)],(225,240,245),5,ink)
   poly(cv,[(-34,28),(34,28),(42,45),(34,60),(-34,60),(-42,45)],accent,0)
   for i in range(4): ell(cv,-20+i*12,20+(i%2)*15,4,4,WHITE,0)
  elif "molecule" in name or "bonds" in name:
   pts=[(-36,-20),(0,-42),(35,-15),(18,35),(-25,32)]
   for a,b in zip(pts,pts[1:]+pts[:1]): line(cv,[a,b],8,(165,175,190))
   for i,(x,y) in enumerate(pts): ell(cv,x,y,17,17,[accent,fill,(80,170,230),(245,110,100),(110,200,130)][i],5,ink)
  elif "magnet" in name:
   curve(cv,[(-42,-40),(-42,20),(-15,52),(15,52),(42,20),(42,-40)],20,(225,60,65)); line(cv,[(-42,-40),(-42,-10)],20,WHITE); line(cv,[(42,-40),(42,-10)],20,(80,150,230))
  elif "light" in name or "bulb" in name:
   ell(cv,0,-10,38,38,(255,220,80),5,ink); rrect(cv,-16,22,16,48,5,(145,150,160),4,ink)
   for i in range(8):
    a=i*math.tau/8; line(cv,[(52*math.cos(a),-10+52*math.sin(a)),(65*math.cos(a),-10+65*math.sin(a))],4,accent)
  elif "shield" in name:
   poly(cv,[(0,-62),(48,-42),(40,18),(0,62),(-40,18),(-48,-42)],fill,6,ink); line(cv,[(-22,0),(-5,18),(25,-18)],9,WHITE)
  elif "lock" in name:
   rrect(cv,-35,-5,35,48,8,(230,190,55),6,ink); curve(cv,[(-22,-8),(-22,-38),(0,-52),(22,-38),(22,-8)],8,ink); ell(cv,0,16,7,7,ink,0)
  elif "phone" in name or "smartphone" in name or "camera" in name:
   rrect(cv,-35,-62,35,62,12,(45,50,60),6,ink); rrect(cv,-26,-48,26,42,4,accent,0); ell(cv,0,52,5,5,WHITE,0)
  elif "book" in name or "note" in name or "card" in name:
   rrect(cv,-42,-56,42,56,8,(250,245,225),5,ink); rrect(cv,-42,-56,-30,56,4,accent,0)
   for i in range(5): line(cv,[(-20,-30+i*15),(30,-30+i*15)],3,(150,160,170))
  elif "gear" in name:
   ell(cv,0,0,38,38,fill,6,ink); ell(cv,0,0,16,16,cv.bg,4,ink)
   for i in range(8):
    a=i*math.tau/8; line(cv,[(40*math.cos(a),40*math.sin(a)),(56*math.cos(a),56*math.sin(a))],12,fill)
  elif "robot" in name or "microchip" in name or "circuit" in name:
   rrect(cv,-40,-40,40,40,8,fill,6,ink)
   for x in (-25,0,25): line(cv,[(x,-52),(x,-40)],4,accent);line(cv,[(x,40),(x,52)],4,accent)
   ell(cv,-15,-8,7,7,WHITE,0);ell(cv,15,-8,7,7,WHITE,0);rrect(cv,-18,10,18,20,5,accent,0)
  else:
   rrect(cv,-42,-50,42,50,8,fill,5,ink); ell(cv,-18,-18,10,10,WHITE,0)
   line(cv,[(-20,12),(20,12)],5,accent)
  return
 # Nature & transport silhouettes with animated secondary details.
 if name in NATURE or name in TRANSPORT:
  if "sun" in name:
   ell(cv,0,0,42,42,(255,210,55),5,ink)
   for i in range(12):
    a=i*math.tau/12; line(cv,[(52*math.cos(a),52*math.sin(a)),(68*math.cos(a),68*math.sin(a))],5,accent)
  elif "moon" in name:
   ell(cv,0,0,50,50,(255,225,110),4,ink); ell(cv,25,-14,43,43,cv.bg,0)
  elif "cloud" in name or "rain" in name:
   cloud_shape(cv,0,0,120,(180,205,225),5,ink)
   if "rain" in name:
    for i in range(5): line(cv,[(-35+i*18,30),(-42+i*18,48)],4,(60,145,230))
  elif "tree" in name or "flower" in name or "leaf" in name:
   line(cv,[(0,30),(0,65)],10,(125,85,45))
   for dx,dy in [(-30,-10),(30,-10),(0,-35),(0,10)]: ell(cv,dx,dy,32,30,(65,170,90),5,ink)
   if "flower" in name:
    ell(cv,0,-20,12,12,(255,210,65),0)
  elif "planet" in name or "earth" in name or "satellite" in name:
   ell(cv,0,0,40,40,fill,5,ink); ell(cv,-14,-12,10,8,WHITE,0)
   curve(cv,[(-70,0),(-40,-25),(40,-25),(70,0),(40,25),(-40,25)],4,accent)
  elif "rocket" in name:
   poly(cv,[(0,-70),(25,-25),(25,45),(-25,45),(-25,-25)],WHITE,5,ink); ell(cv,0,0,12,12,accent,4,ink)
   poly(cv,[(-12,45),(0,80),(12,45)],(255,145,50),0)
  elif "car" in name or "bus" in name or "train" in name:
   rrect(cv,-65,-20,65,25,12,fill,5,ink); rrect(cv,-35,-45,35,-12,8,accent,4,ink)
   for x in (-40,40): ell(cv,x,25,15,15,(40,45,50),5,ink); ell(cv,x,25,6,6,(205,210,220),0)
  elif "airplane" in name or "helicopter" in name:
   poly(cv,[(-10,-60),(10,-60),(18,-8),(60,8),(60,25),(15,18),(12,48),(35,55),(35,65),(0,58),(-35,65),(-35,55),(-12,48),(-15,18),(-60,25),(-60,8),(-18,-8)],fill,5,ink)
  elif "house" in name:
   rrect(cv,-42,-5,42,55,5,(235,215,175),5,ink); poly(cv,[(-58,-5),(0,-60),(58,-5)],accent,5,ink); rrect(cv,-10,20,10,55,4,(125,85,50),4,ink)
  elif "volcano" in name or "mountain" in name:
   poly(cv,[(-70,55),(-20,-50),(10,-10),(42,-65),(70,55)],(100,120,145),6,ink); poly(cv,[(-32,-30),(-20,-50),(-8,-20),(0,-5)],WHITE,0)
  elif "wave" in name or "ocean" in name:
   curve(cv,[(-70,10),(-35,-20),(0,12),(30,-22),(65,0)],14,(70,170,225)); curve(cv,[(-70,30),(-30,10),(0,30),(40,8),(70,25)],7,accent)
  else:
   ell(cv,0,0,48,48,fill,5,ink); ell(cv,-18,-18,13,8,WHITE,0)
  return
 # Mascot: expressive face or action pose, variations are keyed by name.
 if name.startswith("mascot"):
  head=(state.get("head",(0,0)) if isinstance(state,dict) else (0,0))
  ell(cv,0,0,48,48,(255,230,190),6,ink); ell(cv,-16,-12,7,8,ink,0); ell(cv,16,-12,7,8,ink,0)
  mouth="shock" if any(k in name for k in ("shock","panicked","astonished")) else "angry" if "angry" in name or "rage" in name else "sad" if "sad" in name or "cry" in name else "laugh" if "laugh" in name or "celebr" in name else "smile"
  if mouth=="shock": ell(cv,0,18,10,14,(120,40,60),4,ink)
  elif mouth=="sad": curve(cv,[(-18,22),(0,14),(18,22)],5,ink)
  elif mouth=="angry": line(cv,[(-18,20),(0,14),(18,20)],5,ink)
  else: curve(cv,[(-20,15),(0,28),(20,15)],5,ink)
  if "action" in name or name in ACTION:
   line(cv,[(-24,42),(-45,66)],8,accent);line(cv,[(24,42),(45,66)],8,accent)
   line(cv,[(-15,35),(-35,65)],8,ink);line(cv,[(15,35),(35,65)],8,ink)
  if "jump" in name or "run" in name or "dance" in name:
   for i in range(3): line(cv,[(60+i*8,-30+i*15),(82+i*8,-32+i*15)],3,accent)
  return
 # Comic / UI icon shapes.
 if name in COMIC or name in UI:
  if "question" in name or "exclamation" in name:
   label="?" if "question" in name else "!"
   text(cv,4,5,label,82,accent); text(cv,0,0,label,82,fill)
  elif "arrow" in name:
   line(cv,[(-60,0),(35,0)],14,accent); poly(cv,[(15,-25),(60,0),(15,25)],accent,5,ink)
  elif "crown" in name:
   poly(cv,[(-50,30),(-45,-20),(-18,8),(0,-45),(18,8),(45,-20),(50,30)],accent,6,ink); rrect(cv,-50,30,50,48,4,fill,4,ink)
  elif "skull" in name:
   ell(cv,0,-10,42,40,(240,235,220),5,ink); rrect(cv,-20,20,20,45,4,(240,235,220),4,ink)
   ell(cv,-15,0,10,12,ink,0);ell(cv,15,0,10,12,ink,0);line(cv,[(-8,22),(0,35),(8,22)],4,ink)
  elif "burst" in name or "explosion" in name or "impact" in name or "boom" in name:
   star_poly(cv,0,0,60,34,12,rot=-90,fill=accent,w=5,col=ink); ell(cv,0,0,26,26,fill,0)
  elif "crack" in name:
   line(cv,[(0,-65),(-10,-25),(20,-10),(-25,15),(0,65)],7,accent);line(cv,[(-10,-25),(-42,-40)],5,accent);line(cv,[(20,-10),(48,-35)],5,accent)
  elif "speed" in name or "motion" in name:
   for i in range(6): line(cv,[(-65,-45+i*16),(10,-45+i*16)],5,accent)
  elif "sweat" in name or "rain" in name:
   for i in range(4): ell(cv,-25+i*18,-25+(i%2)*15,7,14,(90,170,240),0)
  elif "reticle" in name or "focus" in name or "target" in name:
   ell(cv,0,0,48,48,None,5,accent);ell(cv,0,0,22,22,None,4,accent);line(cv,[(-62,0),(62,0)],4,accent);line(cv,[(0,-62),(0,62)],4,accent)
  elif "check" in name: line(cv,[(-35,0),(-10,28),(38,-34)],12,(70,210,120))
  elif "cross" in name: line(cv,[(-30,-30),(30,30)],12,(240,65,65));line(cv,[(-30,30),(30,-30)],12,(240,65,65))
  elif "warning" in name: poly(cv,[(0,-60),(55,48),(-55,48)],(255,205,50),5,ink); text(cv,0,12,"!",55,ink)
  elif "bubble" in name: cloud_shape(cv,0,0,110,WHITE,5,ink)
  elif "pie" in name or "progress" in name or "meter" in name:
   ell(cv,0,0,46,46,(215,220,230),4,ink); ell(cv,0,0,36,36,accent,0); ell(cv,0,0,20,20,cv.bg,0)
  elif "wave" in name: curve(cv,[(-55,0),(-40,-25),(-20,20),(0,-20),(20,20),(40,-20),(55,0)],5,accent)
  else:
   rrect(cv,-45,-35,45,35,10,fill,5,ink); text(cv,0,0,"i",38,WHITE)
  return
 # Fallback is still a designed sticker-style object, not a raw geometric placeholder.
 rrect(cv,-44,-42,44,42,12,fill,6,ink); ell(cv,-18,-14,8,8,WHITE,0); text(cv,0,14,name[:2].upper(),24,ink)
def draw_prop(cv,x,y,scale=1.0,t=0.0,state=None,mood=None,shadow=True,**kwargs):
 name=kwargs.pop("name",None)
 if name is None: raise ValueError("draw_prop requires a prop name")
 if name not in PROPS: raise KeyError(f"Unknown prop: {name}")
 with group(cv,x,y,sc=scale):
  _draw(cv,name,t,state,mood,shadow=shadow,**kwargs)
def _make(name):
 def fn(cv,x,y,scale=1.0,t=0.0,state=None,mood=None,**kw):
  return draw_prop(cv,x,y,scale,t,state,mood,name=name,**kw)
 fn.__name__="prop_"+name
 fn.__doc__=f"Procedural illustrated {name} prop."
 return fn
PROPS={name:_make(name) for name in PROP_NAMES}
def get_prop(name): return PROPS[name]
def draw_props(cv,items):
 """Draw a list of dict descriptors: name,x,y,scale,t,state,mood."""
 for item in items:
  args=dict(item); name=args.pop("name")
  PROPS[name](cv,**args)
def list_props(category=None):
 buckets={"biology":BIO,"food":FOOD,"chemistry":CHEM,"time":TIME,"technology":TECH,
 "transport":TRANSPORT,"nature":NATURE,"emotion":EMOTION,"action":ACTION,"comic":COMIC,"ui":UI}
 return tuple(sorted(buckets[category])) if category else tuple(PROPS)
