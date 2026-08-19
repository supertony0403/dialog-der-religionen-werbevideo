"""Rendert das Werbevideo: Frames -> ffmpeg.

    python3 src/render.py --format 16x9 --out out/ddr_16x9.mp4
    python3 src/render.py --stills 3,9,17,25,31,37 --scale 0.5
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

import backdrops  # noqa: E402
import core  # noqa: E402
import scenes  # noqa: E402
import scenes_tiktok  # noqa: E402
import timing  # noqa: E402
import timing_tiktok  # noqa: E402

EDITIONS = {"trailer": (scenes, timing.END), "tiktok": (scenes_tiktok, timing_tiktok.END)}

FORMATS = {"16x9": (1920, 1080), "9x16": (1080, 1920), "1x1": (1080, 1080)}
_STATE: dict = {}


def _setup(w: int, h: int, edition: str = "trailer"):
    mod = EDITIONS[edition][0]
    bd = core.Backdrop(w, h)
    stage = mod.Stage(w, h, bd.gw, bd.gh)
    _STATE.update(w=w, h=h, bd=bd, stage=stage, mod=mod)


def frame_at(i: int, fps: int = core.FPS) -> np.ndarray:
    w, h, bd, stage = _STATE["w"], _STATE["h"], _STATE["bd"], _STATE["stage"]
    mod = _STATE["mod"]
    t = i / fps
    fr = core.Frame(w, h)
    L = mod.Layout(fr)
    mod.render(fr, L, t, stage)
    buf, glow = fr.compose()
    glow += stage.mist(t)
    img = Image.fromarray(bd.finish(buf, glow, i, mod.exposure(t)))
    zoom, dx, dy = mod.camera_params(t)
    img = backdrops.camera(img, zoom, dx, dy)
    return np.asarray(img)


def _job(i: int) -> bytes:
    return frame_at(i).tobytes()


def render_video(fmt: str, out: Path, fps: int, seconds: float, workers: int,
                 scale: float = 1.0, crf: int = 17, edition: str = "trailer"):
    w, h = FORMATS[fmt]
    w, h = int(w * scale) // 2 * 2, int(h * scale) // 2 * 2
    n = int(round(seconds * fps))
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
           "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264", "-preset", "slow",
           "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    with Pool(workers, initializer=_setup, initargs=(w, h, edition)) as pool:
        for k, buf in enumerate(pool.imap(_job, range(n), chunksize=6)):
            proc.stdin.write(buf)
            if k % 60 == 0:
                print(f"  {fmt}: {k}/{n} frames", flush=True)
    proc.stdin.close()
    proc.wait()
    print(f"  fertig: {out}")


def render_stills(fmt: str, times: list[float], outdir: Path, fps: int, scale: float,
                  edition: str = "trailer"):
    w, h = FORMATS[fmt]
    w, h = int(w * scale) // 2 * 2, int(h * scale) // 2 * 2
    _setup(w, h, edition)
    outdir.mkdir(parents=True, exist_ok=True)
    for t in times:
        img = frame_at(int(round(t * fps)), fps)
        p = outdir / f"still_{fmt}_{t:05.2f}.png"
        Image.fromarray(img).save(p)
        print(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", default="16x9", choices=list(FORMATS))
    ap.add_argument("--out", default=None)
    ap.add_argument("--fps", type=int, default=core.FPS)
    ap.add_argument("--seconds", type=float, default=None)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--crf", type=int, default=17)
    ap.add_argument("--stills", default=None, help="Zeitpunkte in Sekunden, kommagetrennt")
    ap.add_argument("--stills-dir", default="work/stills")
    ap.add_argument("--edition", default="trailer", choices=list(EDITIONS))
    a = ap.parse_args()

    if a.stills:
        render_stills(a.format, [float(x) for x in a.stills.split(",")],
                      Path(a.stills_dir), a.fps, a.scale, a.edition)
        return
    out = Path(a.out or f"out/ddr_{a.edition}_{a.format}.mp4")
    render_video(a.format, out, a.fps, a.seconds or EDITIONS[a.edition][1],
                 a.workers, a.scale, a.crf, a.edition)


if __name__ == "__main__":
    main()
