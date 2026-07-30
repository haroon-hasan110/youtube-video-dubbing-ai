# 🎬 YouTube Video Dubbing AI
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Whisper](https://img.shields.io/badge/OpenAI-Whisper-black)
![Status](https://img.shields.io/badge/Status-Working-brightgreen)

A Python pipeline that takes any YouTube video — in any language — and produces an English-dubbed version, powered by Whisper, machine translation, and Microsoft Edge's neural text-to-speech.

Built as part of the **Agentic Python Development internship assignment** at Idealabs Digital.

## 🔄 How it works

\`\`\`
YouTube URL → Download (yt-dlp) → Transcribe (Whisper) → Translate (deep-translator)
            → Generate English voice (edge-tts) → Replace audio (ffmpeg) → Dubbed video
\`\`\`

**Pipeline steps in detail:**
1. **Download** — `yt-dlp` fetches the video in H.264 (avc1) format, capped at 720p, for broad compatibility across players.
2. **Transcribe** — Whisper (`base` model) listens to the audio and produces the transcript plus the detected source language (no hardcoding — works for any language).
3. **Translate** — `deep-translator` converts the transcript into English, chunking long text to stay within API limits.
4. **Synthesize** — `edge-tts` converts the English text into a natural voice (`en-US-AndrewNeural`, slightly slowed down for clarity).
5. **Remix** — `ffmpeg` swaps the original audio track for the new dubbed audio and saves the final video, without re-encoding the video stream itself.

## ✨ Features
- Works with videos in **any language** — auto-detects the source language, no manual configuration needed
- Downloads in H.264/720p for wide player compatibility
- Natural-sounding English voiceover using Microsoft's neural TTS voices
- Fully automated end-to-end — just paste a URL and get a dubbed video back

## 🛠 Tech Stack

| Tool | Purpose | Why this one |
|---|---|---|
| `yt-dlp` | Download YouTube videos | Actively maintained fork of youtube-dl; handles YouTube's frequent site changes reliably |
| `openai-whisper` | Speech-to-text transcription | Open-source, multilingual, strong accuracy, runs free locally |
| `deep-translator` | Translate transcript to English | Fast and simple (Google Translate backend) — a deliberate trade-off over heavier tools like IndicTrans2 given the project timeline |
| `edge-tts` | Generate natural English speech | Free, high-quality neural voices from Microsoft Edge |
| `ffmpeg` (via `imageio-ffmpeg`) | Replace audio track in final video | Swaps audio without re-encoding video, keeping quality intact |

## ⚙️ Setup

\`\`\`bash
python -m venv venv
venv\\Scripts\\activate      # Windows
pip install yt-dlp openai-whisper edge-tts deep-translator imageio-ffmpeg
\`\`\`

## ▶️ Usage

\`\`\`bash
python dubber.py
\`\`\`
Paste a YouTube URL when prompted. The final dubbed video is saved as `final_dubbed_video.mp4`.

## 📊 Results

- Successfully tested on videos in **English, Hindi, and Marathi**.
- End-to-end processing time for an 8-minute video: **~2–4 minutes** on a standard CPU (no GPU used).
- Output: a 720p H.264 video with the original visuals and a natural English voiceover replacing the original audio.

## 🐛 Issues Faced & How They Were Solved

| Issue | Solution |
|---|---|
| Python 3.15 (alpha) was pre-installed, incompatible with ML libraries | Installed Python 3.11 (stable) and built the virtual environment on that instead |
| Whisper couldn't find `ffmpeg` on PATH | `imageio-ffmpeg` ships a binary under a different filename — copied it into the venv's `Scripts` folder as `ffmpeg.exe` |
| Re-running with a new URL reused the old downloaded file | Delete any existing `input_video.mp4` before each new download |
| `faster-whisper` was tried for speed, but first-time Hugging Face model downloads were too slow on the available connection | Reverted to standard `openai-whisper` "base" model — already fast enough (under 4 minutes end-to-end for an 8-minute video) |
| Default download format was low-res (360p, AV1) and unplayable in Windows Media Player | Constrained the format selector to H.264 at up to 720p for both quality and compatibility |
| Generated voice occasionally mispronounced technical acronyms | Known limitation of general-purpose TTS — noted as a future improvement via a custom pronunciation dictionary |

## ⚠️ Known Limitations
- TTS occasionally mispronounces technical acronyms (e.g. "GitHub") — a known limitation of general-purpose TTS engines.
- Processing time scales with video length and CPU speed (no GPU acceleration used).
- Translation uses a general-purpose translator rather than a domain-specific one, so idiomatic phrasing can occasionally be lost.

## 📚 What I Learned
- How a real speech-to-text-to-speech pipeline is structured end-to-end.
- Practical trade-offs between model size, speed, and accuracy (`base` vs `small` vs `faster-whisper`).
- Debugging real-world environment issues (Python versions, PATH variables, video codecs) that don't show up in tutorials.
- Working iteratively with an AI coding assistant (vibe coding) to build and debug a non-trivial project under a tight deadline.