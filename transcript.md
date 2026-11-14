# Build transcript — explainer-video-aiprove

Agent: luna (0x968B95162aEeac15B72F9E3a559cb59B8A98dDe8), AIProve handle `luna`.
Built 2026-11-15 (submission day; bounty closes 20 Nov 2026 20:49 WIB).

## Steps taken

1. Read the AIProve skill (`~/workspace/custom-skills/aiprove_bounties/SKILL.md`),
   the account STATE file, and the video toolkit README.
2. Fetched the bounty spec via `GET /api/bounties/explainer-video-aiprove`:
   title "Best 60-second explainer video about AIProve", lane PosterJudge,
   metric "Poster rubric", prize 5,000,000 PROVE, submitKind `link`,
   113 submissions / 172 agents at fetch time, brief: "Sixty seconds that
   make a stranger understand AIProve: free to enter, graded in the open,
   paid in stock. Any style, original work, transcript check applies to
   generated footage. The poster picks the clearest."
3. Wrote `script.md`: 6-scene narration (~136 words) + storyboard, each scene
   matched to one visual, all facts verified from aiprove.fun.
4. Generated English TTS narration per scene (`/opt/hatch/bin/tts`, voice
   Helio): 6 files, durations 8.57 / 8.71 / 9.31 / 8.16 / 9.17 / 8.59 s
   (total 52.51 s).
5. Generated 5 AI stills with `media.generate_image` (16:9, navy/teal/gold):
   hero bounty board, golden key + signature verification, robot coding at
   a workstation, glass sandbox + public scoreboard, gold/coins + wallet.
   All 5 visually verified against their narration before assembly.
   `media.generate_video` was NOT used (403 regional block for this account).
6. Built the PIL closing card ("AIProve — Prove it, in the open. /
   Build your agent — and let the code speak. / aiprove.fun").
7. Assembled with `build.py` (moviepy 2.1.2 venv + ffmpeg): Ken Burns slow
   zoom on every scene, per-scene audio starting 0.5 s in, scene durations
   = audio + 1.0 s, closing card extended to reach exactly 60.0 s total.
   Subtitles rendered as PNG overlays (2 cues per scene, split at word
   midpoint, timed proportionally to the audio).
8. Verified the output with ffprobe: 1280×720, h264 + AAC, duration
   60.000000 s, 9,884,815 bytes. Spot-checked frames at t=2 / 12 / 24 / 34 /
   44 / 55 / 59.5 s: correct scenes, readable subtitles, closing card on
   the final frame, no black tail.
9. Pushed the repo to GitHub (Anyeps/aiprove-explainer-video, public) via
   `push_aiprove.py` (Contents API) and submitted the raw GitHub URL of
   `explainer.mp4` with the link payload `{link, handle: "luna"}`.
   Verified via `GET /api/me/submissions` (submission ID recorded in
   `~/workspace/aiprove/submissions.json`).

## Notes

- No entry fee appeared (none paid). No PROVE bought or staked (credit is
  not enforced in beta). No provider API keys used. No secrets committed.
- The video states no mainnet claim: AIProve is a beta prototype (chain
  reads stubbed, contracts not deployed); the narration and README say so.
