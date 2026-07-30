import os
import yt_dlp
import whisper
import edge_tts
import asyncio
import subprocess
import imageio_ffmpeg
import time

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] += os.pathsep + os.path.dirname(FFMPEG_PATH)

# ---------- STEP 1: Download video ----------
def download_video(url, output_path="input_video.mp4"):
    if os.path.exists(output_path):
        os.remove(output_path)
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][vcodec^=avc1][height<=720]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("✅ Video downloaded:", output_path)
    return output_path

# ---------- STEP 2: Transcribe audio ----------
def transcribe_audio(video_path):
    print("Loading Whisper model... (first time takes a bit)")
    model = whisper.load_model("base")
    result = model.transcribe(video_path, condition_on_previous_text=False)
    print("✅ Transcription done. Detected language:", result["language"])
    return result["text"], result["language"], result["segments"]

# ---------- Helper: translate with retry ----------
def translate_with_retry(text, retries=3, delay=3):
    from deep_translator import GoogleTranslator
    for attempt in range(retries):
        try:
            result = GoogleTranslator(source='auto', target='en').translate(text)
            if result:
                return result
        except Exception as e:
            print(f"⚠️ Translate retry {attempt+1}/{retries}:", e)
            time.sleep(delay)
    return text  # fallback: original text

# ---------- STEP 3: Translate to English ----------
def translate_text(text, source_lang):
    max_chunk = 4500
    chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
    translated_chunks = [translate_with_retry(chunk) for chunk in chunks]
    translated = " ".join(translated_chunks)
    print("✅ Translation done")
    return translated

# ---------- STEP 3.5: Generate SRT subtitles ----------
def generate_srt(segments, output_srt="subtitles.srt"):
    def format_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    with open(output_srt, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            translated = translate_with_retry(seg["text"]) or seg["text"]
            f.write(f"{i}\n")
            f.write(f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n")
            f.write(f"{translated.strip()}\n\n")

    print("✅ Subtitles generated:", output_srt)
    return output_srt

# ---------- STEP 4: Text-to-speech ----------
async def generate_speech(text, output_audio="dubbed_audio.mp3"):
    communicate = edge_tts.Communicate(text, voice="en-US-AndrewNeural", rate="-12%", pitch="-2Hz")
    await communicate.save(output_audio)
    print("✅ Speech generated:", output_audio)

# ---------- STEP 5: Replace audio in video ----------
def replace_audio(video_path, audio_path, output_path="final_dubbed_video.mp4"):
    command = [
        FFMPEG_PATH, "-i", video_path, "-i", audio_path,
        "-c:v", "copy", "-map", "0:v:0", "-map", "1:a:0",
        "-shortest", output_path, "-y"
    ]
    subprocess.run(command)
    print("✅ Final dubbed video ready:", output_path)

# ---------- STEP 6: Burn subtitles ----------
def burn_subtitles(video_path, srt_path, output_path="final_dubbed_with_subtitles.mp4"):
    srt_path_fixed = srt_path.replace("\\", "/").replace(":", "\\:")
    command = [
        FFMPEG_PATH, "-i", video_path,
        "-vf", f"subtitles={srt_path_fixed}",
        "-c:a", "copy", output_path, "-y"
    ]
    subprocess.run(command)
    print("✅ Subtitled video ready:", output_path)

def main(youtube_url):
    start_time = time.time()
    print("🚀 Starting pipeline...\n")

    video_path = download_video(youtube_url)
    text, lang, segments = transcribe_audio(video_path)
    translated_text = translate_text(text, lang)
    asyncio.run(generate_speech(translated_text))
    replace_audio(video_path, "dubbed_audio.mp3")

    #srt_path = generate_srt(segments)
    #burn_subtitles("final_dubbed_video.mp4", srt_path)

    elapsed = time.time() - start_time
    print(f"\n🎉 Done! Total time taken: {elapsed/60:.2f} minutes")

if __name__ == "__main__":
    url = input("Enter YouTube URL: ")
    main(url)