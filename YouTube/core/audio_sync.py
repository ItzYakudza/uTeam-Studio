"""
uTeam-Studio
core/audio_sync.py — вырезка пауз, привязка текста к голосу, фоновая музыка и SFX.
"""

import os
import re
import math
import wave
import shutil
import subprocess
from typing import List, Tuple, Dict, Optional

import numpy as np

from .config import FormatConfig

SR = 44100


# ============================================================
# Вспомогательные
# ============================================================

def syl(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    g = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and not w.endswith(("le", "ee")) and g > 1:
        g -= 1
    if w.endswith("ed") and g > 1 and not w.endswith(("ted", "ded")):
        g -= 1
    return max(1, g)


def load_voice(path: str) -> np.ndarray:
    exe = None
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    exe = exe or shutil.which("ffmpeg")
    if not exe:
        raise RuntimeError("ffmpeg not found")
    raw = subprocess.run(
        [exe, "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        stdout=subprocess.PIPE, check=True
    ).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def find_pauses(x: np.ndarray, min_pause: float = 0.25) -> List[Tuple[float, float]]:
    hop = SR // 100
    n = len(x) // hop
    if n == 0:
        return []
    db = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    sil = db < -40
    iv = []
    s0 = None
    for i, v in enumerate(sil):
        if v and s0 is None:
            s0 = i
        if not v and s0 is not None:
            iv.append((s0 * 0.01, i * 0.01))
            s0 = None
    return [(a, b) for a, b in iv if b - a >= min_pause and a > 0.2 and b < n * 0.01 - 0.2]


def tighten(x: np.ndarray, iv: List[Tuple[float, float]], gap: float = 0.14) -> Tuple[np.ndarray, List[float]]:
    """Сжимает паузы до gap. Возвращает новый звук и центры пауз."""
    tail = 0.03
    parts = []
    gc = []
    cur = 0.0
    prev = 0.0
    fade = np.linspace(0, 1, int(0.006 * SR))

    for a, b in iv:
        seg_ = x[int(prev * SR): int((a + tail) * SR)].copy()
        if len(seg_) > len(fade):
            seg_[:len(fade)] *= fade
            seg_[-len(fade):] *= fade[::-1]
        parts.append(seg_)
        cur += len(seg_) / SR
        parts.append(np.zeros(int((gap - 2 * tail) * SR)))
        gc.append(cur + (gap - 2 * tail) / 2)
        cur += (gap - 2 * tail)
        prev = b - tail

    last = x[int(prev * SR):].copy()
    if len(last) > len(fade):
        last[:len(fade)] *= fade
    parts.append(last)

    y = np.concatenate(parts) if parts else x.copy()
    end = np.where(np.abs(y) > 0.003)[0]
    if len(end):
        y = y[: end[-1] + int(0.15 * SR)]
    return y, gc


def text_breaks(texts: List[str]) -> Tuple[List[Tuple[int, str, int]], int]:
    S = 0
    br = []
    for si, t in enumerate(texts):
        for tok in re.findall(r"[A-Za-z']+|[.,?!]", t):
            if tok[0].isalpha():
                S += syl(tok)
            else:
                br.append((S, tok, si))
    return br, S


def align(iv: List[Tuple[float, float]], total_speech: float,
          texts: List[str]) -> Tuple[List[Tuple[int, str, int]], Dict[int, int]]:
    """Динамическое программирование: знаки препинания ↔ паузы."""
    T = []
    cum = 0.0
    prev = 0.0
    for a, b in iv:
        cum += a - prev
        T.append(cum)
        prev = b
    dur = [b - a for a, b in iv]

    br, Stot = text_breaks(texts)
    rate = total_speech / max(Stot, 1)

    br = br + [(Stot, ".", -1)]
    T = T + [total_speech]
    dur = dur + [1.0]

    J, I = len(br), len(T)
    INF = 1e18
    P = [0.0]
    for b in br:
        P.append(P[-1] + (0.6 if b[1] == "," else 3.0))

    F = np.full((J + 1, I + 1), INF)
    F[0, 0] = 0
    B = {}

    Sj = lambda j: 0 if j < 0 else br[j][0]
    Ti = lambda i: 0 if i < 0 else T[i]

    for j in range(J):
        for i in range(I):
            best = INF
            arg = None
            for j0 in range(max(-1, j - 8), j):
                for i0 in range(max(-1, i - 8), i):
                    v = F[j0 + 1, i0 + 1]
                    if v >= INF:
                        continue
                    dS = (Sj(j) - Sj(j0)) * rate
                    dT = Ti(i) - Ti(i0)
                    c = v + (dT - dS) ** 2 / (0.25 * dS + 0.6) + (P[j] - P[j0 + 1]) + 0.5 * (i - i0 - 1)
                    if c < best:
                        best, arg = c, (j0, i0)
            if arg is None:
                continue
            pen = 0.0
            if br[j][1] != "," and dur[i] < 0.3:
                pen += 1.0
            if br[j][1] == "," and dur[i] > 0.9:
                pen += 1.0
            F[j + 1, i + 1] = best + pen
            B[(j, i)] = arg

    node = (J - 1, I - 1)
    pairs = {}
    while node != (-1, -1):
        j, i = node
        if j < J - 1:
            pairs[j] = i
        node = B.get(node, (-1, -1))
    return br[:-1], pairs


def build_timeline(vlen_tight: float, gc: List[float],
                   br: List[Tuple[int, str, int]], pairs: Dict[int, int],
                   Stot: int, texts: List[str],
                   lead: float, tail: float) -> Tuple[List[float], List[float], List[List[float]], float]:
    anchors = [(0, 0.0)] + [(br[j][0], gc[i]) for j, i in sorted(pairs.items())] + [(Stot, vlen_tight)]
    xs = [a[0] for a in anchors]
    ys = [a[1] for a in anchors]

    tt = []
    for j, b in enumerate(br):
        if j in pairs:
            tt.append(gc[pairs[j]])
        else:
            tt.append(float(np.interp(b[0], xs, ys)))

    ends = [[] for _ in texts]
    for j, b in enumerate(br):
        if b[1] != ",":
            ends[b[2]].append(tt[j])

    starts, cues = [], []
    for si in range(len(texts)):
        sc0 = 0.0 if si == 0 else lead + ends[si - 1][-1]
        first = lead if si == 0 else sc0
        starts.append(sc0)
        cues.append([first] + [lead + e for e in ends[si][:-1]])

    total = lead + vlen_tight + tail
    durs, T = [], []
    for si in range(len(texts)):
        end = starts[si + 1] if si < len(texts) - 1 else total
        durs.append(end - starts[si])
        T.append([max(0.1, v - starts[si] - 0.08) for v in cues[si]] + [end - starts[si]])
    return starts, durs, T, total


# ============================================================
# Фоновая музыка + SFX
# ============================================================

def make_background_audio(path: str, total: float, starts: List[float], T: List[List[float]]):
    n = int(SR * total)
    mix = np.zeros(n)

    def add(t0: float, sig: np.ndarray, v: float = 1.0):
        s = int(t0 * SR)
        if s < 0 or s >= n:
            return
        sig = sig[: n - s]
        mix[s: s + len(sig)] += sig * v

    chords = [
        (220, 261.63, 329.63),
        (174.61, 220, 261.63),
        (261.63, 329.63, 392.0),
        (196, 246.94, 293.66),
    ]
    cd = 8.0
    i = 0
    while i * cd < total:
        L = int(SR * (cd + 1.5))
        tt = np.arange(L) / SR
        sig = sum(np.sin(2 * np.pi * f * tt) for f in chords[i % 4]) * 0.022
        sig += np.sin(2 * np.pi * chords[i % 4][0] / 2 * tt) * 0.026
        env = np.minimum(1, tt / 1.5) * np.minimum(1, (L / SR - tt) / 1.5)
        add(i * cd, sig * env)
        i += 1

    mix *= np.minimum(1, np.arange(n) / (SR * 2)) * np.minimum(1, (n - np.arange(n)) / (SR * 2.5))

    def pop_(t0, v=0.2):
        t = np.arange(int(SR * 0.18)) / SR
        add(t0, np.sin(2 * np.pi * (400 * t + 1800 * t * t)) * np.exp(-t * 18), v)

    def click(t0, v=0.18):
        t = np.arange(int(SR * 0.04)) / SR
        add(t0, np.random.uniform(-1, 1, len(t)) * np.exp(-t * 120), v)

    def swoosh(t0):
        t = np.arange(int(SR * 0.4)) / SR
        add(t0, np.random.uniform(-1, 1, len(t)) * np.sin(np.pi * t / 0.4) ** 2 * 0.10)

    for si, st in enumerate(starts):
        if si > 0:
            swoosh(st - 0.05)
        for k, c in enumerate(T[si][:-1]):
            (pop_ if k % 2 == 0 else click)(st + c + 0.05)

    mix = np.clip(mix, -1, 1)
    st = np.stack([mix, mix], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def write_wav_mono(path: str, y: np.ndarray):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


# ============================================================
# Главная функция
# ============================================================

class SyncResult:
    def __init__(self, y, starts, durs, T, total, voice_path_tight):
        self.y = y
        self.starts = starts
        self.durs = durs
        self.T = T                  # T[scene_idx] = list of cue times inside scene
        self.total = total
        self.voice_path_tight = voice_path_tight


def prepare_voice(voice_path: str, texts: List[str], cfg: FormatConfig,
                  work_dir: str = ".") -> SyncResult:
    """
    Читает озвучку, вырезает паузы, считает тайминги сцен.
    """
    x = load_voice(voice_path)
    iv = find_pauses(x, cfg.min_pause)
    y, gc = tighten(x, iv, cfg.gap)

    br, Stot = text_breaks(texts)
    total_speech = len(x) / SR - sum(b - a for a, b in iv)
    br2, pairs = align(iv, total_speech, texts)

    starts, durs, T, total = build_timeline(
        len(y) / SR, gc, br2, pairs, Stot, texts, cfg.lead, cfg.tail
    )

    tight_path = os.path.join(work_dir, "voice_tight.wav")
    write_wav_mono(tight_path, y)

    print(f"[1/4] Обработка озвучки: {len(x)/SR:.1f}s → {len(y)/SR:.1f}s | пауз: {len(iv)}, привязано: {len(pairs)}/{len(br2)}")
    print(f"      → {tight_path}")
    return SyncResult(y, starts, durs, T, total, tight_path)
