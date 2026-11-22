"""
30-second engine-v2 test render.
Run from repository root: py YouTube/test_engine_v2.py
Uses core Canvas/primitives, 100-prop library, typography, motion, procedural SFX/music.
"""
from pathlib import Path
import numpy as np
from moviepy import VideoClip, AudioArrayClip
from core.toolkit import *

DURATION = 30
CFG = get_format("shorts")
SR = 44100
OUT = Path("YouTube/engine_v2_test.mp4")
WORK = Path("YouTube/engine_v2_test_audio")
WORK.mkdir(parents=True, exist_ok=True)

# New v2 music and sound generators, all rendered as a single stereo track.
music = generate_music(style="energetic", bpm=112, key="D", duration=DURATION, seed=12, sample_rate=SR)
audio = np.zeros(int(DURATION*SR), dtype=np.float32)
audio[:min(len(music),len(audio))] += music[:len(audio)] * .24
sfx_plan = [
    ("whoosh_rise", .12, .55), ("impact_heavy", 5.8, .8),
    ("electric_zap", 11.9, .55), ("pop_bubble", 17.8, .55),
    ("power_up", 23.7, .8), ("impact_soft", 29.2, .5)
]
for name, at, intensity in sfx_plan:
    clip = render_sfx(name, duration=.55, intensity=intensity, seed=int(round(at*100)), sample_rate=SR)
    i = int(at*SR); j = min(len(audio), i+len(clip))
    if j>i: audio[i:j] += clip[:j-i] * .38
audio = np.clip(audio, -.98, .98)
AudioArrayClip(audio, fps=SR).write_audiofile(str(WORK/"engine_v2_audio.wav"), fps=SR, codec="pcm_s16le", logger=None)

def draw_center(cv, label, y, size, col, bg, accent):
    draw_text(cv, CFG.center_x, y, label, size, style_name="impact_title", color=col, bg=bg, accent=accent, shadow=True)

def scene(t):
    idx = min(4, int(t//6))
    local = t - idx*6
    palettes = ["deep_ocean_04", "purple_lab_06", "bio_green_05", "golden_punch_06", "ink_mono_05"]
    p = get_palette(palettes[idx])
    cv = Canvas(CFG, p["bg"])
    # restrained grid texture, engine line primitives
    for x in range(40, CFG.width, 60):
        line(cv, [(x,0),(x,CFG.height)], 1, tuple(int(v*.22) for v in p["accent"]))
    for y in range(40, CFG.height, 60):
        line(cv, [(0,y),(CFG.width,y)], 1, tuple(int(v*.22) for v in p["accent"]))
    # headline animates with engine motion easing
    popk = motion_ease(min(1,local/.6), "ease_out_back")
    ytitle = 180 + (1-popk)*45
    titles = ["VISUAL ENGINE", "MOTION SYSTEM", "100+ PROPS", "PROCEDURAL AUDIO", "uTEAM STUDIO"]
    draw_center(cv, titles[idx], ytitle, 46, p["text"], p["bg"], p["accent"])
    # center hero uses new prop library and is animated by engine motion presets
    hero = ["brain_detailed","molecule","battery_level","lightbulb","earth_globe"][idx]
    drift = motion_apply("float_idle", local, amp=8, speed=1.2)
    scale = 1.25 + .08*np.sin(local*2.4)
    x = CFG.center_x + drift["x"] if "x" in drift else CFG.center_x
    y = 555 + drift["y"]
    draw_prop(cv, x, y, scale=scale, t=local, color=p["accent"], accent=p["secondary"], shadow=True)
    # small moving orbiting nodes around hero
    for k in range(8):
        a = local*1.1 + k*np.pi/4
        xx = x + 145*np.cos(a); yy = y + 145*np.sin(a)
        ell(cv, xx, yy, 7, 7, p["secondary"], 2, p["text"])
    captions = ["Canvas + palettes", "Easing + float motion", "Expanded object registry", "Music bed + layered SFX", "Visual and audio test"]
    draw_text(cv, CFG.center_x, 890, captions[idx], 30, style_name="soft_caption", color=p["text"], bg=p["bg"], accent=p["accent"])
    # Progress strip and chapter number
    rrect(cv, 65, 1080, 610, 1090, 5, tuple(int(v*.4) for v in p["accent"]), 0)
    rrect(cv, 65, 1080, 65+545*(t/DURATION), 1090, 5, p["accent"], 0)
    draw_text(cv, 85, 1140, f"0{idx+1} / 05", 24, style_name="floating_label", color=p["text"], bg=p["bg"], accent=p["accent"])
    return np.array(cv.final_image())

video = VideoClip(scene, duration=DURATION).with_audio(AudioArrayClip(audio, fps=SR))
video.write_videofile(str(OUT), fps=CFG.fps, codec="libx264", audio_codec="aac",
    audio_bitrate="192k", preset="medium", ffmpeg_params=["-crf","17","-pix_fmt","yuv420p","-movflags","+faststart"], logger="bar")
print(f"Rendered engine-v2 test: {OUT.resolve()}")
