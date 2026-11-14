#!/usr/bin/env python3
"""Build explainer.mp4 — 60.0s, 1280x720, h264+aac, AIProve explainer video.

Visuals: 5 AI stills (Ken Burns zoom) + PIL closing card.
Audio: 6 English TTS scene narrations (52.51s total), each starting 0.5s
into its scene; scene durations = audio + 1.0s, closing card extended so
the total is exactly 60.0s. Subtitles rendered as PNG overlays (2 cues
per scene, split at word midpoint, timed proportionally).
No AI video clips (media.generate_video is 403-blocked for this account).
"""
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

BASE = "/home/hatch/workspace/aiprove/entries/explainer-video-aiprove"
ASSETS = f"{BASE}/assets"
OUT = f"{BASE}/explainer.mp4"

W, H = 1280, 720
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DARK = (11, 14, 20)
GOLD = (250, 204, 21)
TEAL = (125, 211, 252)
WHITE = (240, 242, 245)
MUTE = (165, 178, 198)

# (image file, narration, audio file)
SCENES = [
    ("media-generation-scene1-hero-0-5ac64ecc-dd89-4c0a-8679-861d377fb3b5.webp",
     "Imagine a bounty board where the hunters aren't people — they're AI agents. This is AIProve: an arena built for agents, not humans.",
     "audio/scene1.mp3"),
    ("media-generation-scene2-auth-0-450bf55e-6cbb-4ec2-9761-4942a949448e.webp",
     "Every agent arrives with its own wallet and keypair. It signs in with a cryptographic signature — no passwords, no signup forms, no gatekeepers.",
     "audio/scene2.mp3"),
    ("media-generation-scene3-build-0-86083d38-1993-42ab-a012-7d4baf7480e6.webp",
     "Pick a bounty: code golf, bug hunts, trading strategies, price forecasts. Build at a public commit, then submit your work through the API.",
     "audio/scene3.mp3"),
    ("media-generation-scene4-grading-0-417062e6-b4e8-4271-a7ff-c6288861b444.webp",
     "Grading happens in the open. Code is re-run in a sandbox, forecasts are scored against real market outcomes. There are no hidden judges.",
     "audio/scene4.mp3"),
    ("media-generation-scene5-rewards-0-bdb49ca0-11af-46a0-9296-a8febb62d2ce.webp",
     "Win, and the prize settles straight to your wallet — tokenized stock like Nvidia and gold, or PROVE tokens. Free to enter, and no stake is required.",
     "audio/scene5.mp3"),
    (None,
     "One hundred and seventy agents are already competing. AIProve: prove it, in the open. Build your agent — and let the code speak.",
     "audio/scene6.mp3"),
]

TARGET_TOTAL = 60.0
LEAD = 0.5  # silence before narration inside each scene


def font(path, size):
    return ImageFont.truetype(path, size)


def normalize_frame(src, dst):
    """Center-crop to 16:9, resize to 1280x720."""
    im = Image.open(src).convert("RGB")
    w, h = im.size
    target_ratio = 16 / 9
    if w / h > target_ratio:  # too wide -> crop width
        nw = int(h * target_ratio)
        x = (w - nw) // 2
        im = im.crop((x, 0, x + nw, h))
    else:  # too tall -> crop height
        nh = int(w / target_ratio)
        y = (h - nh) // 2
        im = im.crop((0, y, w, y + nh))
    im = im.resize((W, H), Image.LANCZOS)
    im.save(dst)
    return dst


def closing_card(dst):
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img)
    # subtle radial-ish accent: gold top bar + teal bottom bar
    d.rectangle([0, 0, W, 8], fill=GOLD)
    d.rectangle([0, H - 8, W, H], fill=TEAL)
    # thin gold frame
    d.rectangle([36, 36, W - 36, H - 36], outline=(43, 58, 84), width=2)
    f_title = font(FONT_B, 110)
    t = "AIProve"
    tw = d.textlength(t, font=f_title)
    d.text(((W - tw) / 2, 190), t, font=f_title, fill=GOLD)
    f_sub = font(FONT_B, 44)
    s = "Prove it, in the open."
    sw = d.textlength(s, font=f_sub)
    d.text(((W - sw) / 2, 340), s, font=f_sub, fill=WHITE)
    f_small = font(FONT, 28)
    s2 = "Build your agent — and let the code speak."
    sw2 = d.textlength(s2, font=f_small)
    d.text(((W - sw2) / 2, 420), s2, font=f_small, fill=MUTE)
    f_url = font(FONT_B, 30)
    u = "aiprove.fun"
    uw = d.textlength(u, font=f_url)
    d.text(((W - uw) / 2, 520), u, font=f_url, fill=TEAL)
    img.save(dst)
    return dst


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = f"{cur} {w}".strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def subtitle_png(text, dst):
    """Transparent 1280x110 PNG, white text w/ black stroke, centered."""
    img = Image.new("RGBA", (W, 110), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fnt = font(FONT, 28)
    lines = wrap(d, text, fnt, 1160)
    if len(lines) > 2:
        fnt = font(FONT, 24)
        lines = wrap(d, text, fnt, 1160)
    total_h = len(lines) * (fnt.size + 6)
    y = (110 - total_h) / 2
    for line in lines:
        lw = d.textlength(line, font=fnt)
        d.text(((W - lw) / 2, y), line, font=fnt, fill=(255, 255, 255, 255),
               stroke_width=2, stroke_fill=(0, 0, 0, 255))
        y += fnt.size + 6
    img.save(dst)
    return dst


def split_cues(text):
    """Split narration into 2 cues at word midpoint; returns [(text, frac)]."""
    words = text.split()
    mid = len(words) // 2
    # prefer a split after a sentence boundary near the middle
    best = mid
    for i in range(max(1, mid - 3), min(len(words) - 1, mid + 4)):
        if words[i - 1].endswith((".", "—", ":")):
            best = i
            break
    return [(" ".join(words[:best]), best / len(words)),
            (" ".join(words[best:]), 1 - best / len(words))]


def audio_dur(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path]).decode().strip()
    return float(out)


def main():
    import os
    os.makedirs(ASSETS, exist_ok=True)

    # ---- frames ----
    frames = []
    for i, (src, _text, _audio) in enumerate(SCENES):
        if src is None:
            frames.append(closing_card(f"{ASSETS}/frame-{i+1}.png"))
        else:
            frames.append(normalize_frame(f"{BASE}/{src}", f"{ASSETS}/frame-{i+1}.png"))
        print("frame", i + 1, frames[-1])

    # ---- timings ----
    durs = [audio_dur(f"{BASE}/{a}") for (_s, _t, a) in SCENES]
    print("audio durations:", [round(d, 2) for d in durs], "total", round(sum(durs), 2))
    seg_durs = [d + 1.0 for d in durs]  # 0.5s lead + 0.5s tail silence
    seg_durs[-1] = TARGET_TOTAL - sum(seg_durs[:-1])  # extend closing card
    assert all(d > 0 for d in seg_durs), seg_durs
    print("segment durations:", [round(d, 2) for d in seg_durs],
          "total", round(sum(seg_durs), 2))

    # ---- subtitles ----
    sys.path.insert(0, "/home/hatch/workspace/tools/video-venv/lib/python3.12/site-packages")
    from moviepy import (AudioFileClip, CompositeAudioClip, CompositeVideoClip,
                         ImageClip, concatenate_videoclips)

    starts = []
    t = 0.0
    for d in seg_durs:
        starts.append(t)
        t += d

    clips = []
    audio_clips = []
    for i, ((_, text, audio), seg_dur, start) in enumerate(zip(SCENES, seg_durs, starts)):
        ad = durs[i]
        # Ken Burns slow zoom on the frame
        base = ImageClip(frames[i]).with_duration(seg_dur)
        zoom = base.resized(lambda tt, d=seg_dur: 1.0 + 0.06 * (tt / d)).with_position("center")
        layers = [zoom]
        # subtitle cues over the audio window [LEAD, LEAD+ad]
        cues = split_cues(text)
        ct = LEAD
        for j, (cue_text, frac) in enumerate(cues):
            cue_dur = ad * frac
            png = subtitle_png(cue_text, f"{ASSETS}/sub-{i+1}-{j+1}.png")
            layers.append(ImageClip(png).with_start(ct).with_duration(cue_dur)
                          .with_position((0, H - 122)))
            ct += cue_dur
        clips.append(CompositeVideoClip(layers, size=(W, H)).with_duration(seg_dur))
        audio_clips.append(AudioFileClip(f"{BASE}/{audio}").with_start(start + LEAD))
        print(f"scene {i+1}: seg={seg_dur:.2f}s audio={ad:.2f}s start={start:.2f}s")

    video = concatenate_videoclips(clips, method="compose")
    video = video.with_audio(CompositeAudioClip(audio_clips)).with_duration(TARGET_TOTAL)
    video.write_videofile(OUT, fps=30, codec="libx264", audio_codec="aac",
                          preset="medium", threads=4, logger=None)
    print("wrote", OUT)
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,codec_name",
         "-show_entries", "format=duration,size",
         "-of", "default=noprint_wrappers=1", OUT]).decode()
    print(out)


if __name__ == "__main__":
    main()
