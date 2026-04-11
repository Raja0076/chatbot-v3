import os
from pydub import AudioSegment


FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
FFPROBE_PATH = r"C:\ffmpeg\bin\ffprobe.exe"

if not os.path.exists(FFMPEG_PATH):
    raise FileNotFoundError(f"ffmpeg.exe not found at: {FFMPEG_PATH}")

if not os.path.exists(FFPROBE_PATH):
    raise FileNotFoundError(f"ffprobe.exe not found at: {FFPROBE_PATH}")

AudioSegment.converter = FFMPEG_PATH
AudioSegment.ffmpeg = FFMPEG_PATH
AudioSegment.ffprobe = FFPROBE_PATH

ffmpeg_bin_dir = os.path.dirname(FFMPEG_PATH)
os.environ["PATH"] = ffmpeg_bin_dir + os.pathsep + os.environ.get("PATH", "")


def convert_webm_to_wav(input_path, output_path):
    audio = AudioSegment.from_file(input_path, format="webm")
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    audio.export(output_path, format="wav")