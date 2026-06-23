#video to audio conversion
import yt_dlp
from pydub import AudioSegment#use when we need chunking 
import os

DOWNLOAD_DIR='downloads'
os.makedirs(DOWNLOAD_DIR,exist_ok=True)

def download_youtube_audio(url :str)->str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")#Team meeting.wav#team meeting is title  . ext as extension
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,#will  supress all the download logs in the terminal
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
    return filename


#creating a function which will convert dual audio into mono audio(same audio will come from both end)
#locking the audio quality around 16khz
#for whisper tanscription the sweet spot is around 16khz


def convert_to_wav(input_path: str) -> str:
    # 1. A docstring explaining the function's overall purpose
    """Convert any audio/video file to WAV format using pydub."""

    # 2. Splits the original extension off and creates a new path ending in '_converted.wav'
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    # 3. Loads the source audio or video file into an in-memory AudioSegment object
    audio = AudioSegment.from_file(input_path)

    # 4. Converts the audio to mono (1 channel) and changes the sample rate to 16,000 Hz
    audio = audio.set_channels(1).set_frame_rate(16000)

    # 5. Saves the processed in-memory audio out to a physical file on your hard drive
    audio.export(output_path, format="wav")

    # 6. Returns the string path of the newly created WAV file
    return output_path


#converts long video into chunks for whisper ai

def chunk_audio(wav_path:str, chunk_minutes :int = 10) -> list:#if i divide the 50 min video into 5parts and they can be saved with downloads with specific file paths and then it will be stored int he list and i will return it 
    audio = AudioSegment.from_wav(wav_path)
    #chunking mainly works on milliseconds 
    chunk_ms = chunk_minutes *60 * 1000
    
    chunks=[]
    
    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk=audio[start : start + chunk_ms]
        chunk_path=f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format ="wav")
        
        chunks.append(chunk_path)
    return chunks
    

#giving the links of each function that it can be called directly
def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)
    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks

