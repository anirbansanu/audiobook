import os
import argparse
import subprocess
from gtts import gTTS
from pydub import AudioSegment
from tqdm import tqdm

def text_to_speech_gtts_large_file(file_path, lang='en', output_file='output.mp3', chunk_size=1024, play_audio=True):
    if not os.path.exists('audio_chunks'):
        os.makedirs('audio_chunks')
    
    def read_in_chunks(file_object, chunk_size=1024):
        """Lazy function (generator) to read a file piece by piece."""
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    chunk_files = []
    with open(file_path, 'r') as file:
        total_size = os.path.getsize(file_path)
        with tqdm(total=total_size, unit='B', unit_scale=True, desc='Processing') as pbar:
            for i, chunk in enumerate(read_in_chunks(file, chunk_size)):
                tts = gTTS(text=chunk, lang=lang)
                chunk_file = f'audio_chunks/chunk_{i}.mp3'
                tts.save(chunk_file)
                chunk_files.append(chunk_file)
                pbar.update(len(chunk))
                # print(f"Chunk {i} created: {chunk_file}")
    
    # Concatenate all chunk files into the final output file
    concatenate_audio_files(chunk_files, output_file)
    
    # Delete chunk files
    for chunk_file in chunk_files:
        os.remove(chunk_file)
    
    # Play the output file using the default media player if play_audio is True
    if play_audio:
        try:
            if os.name == 'posix':  # For Unix-like systems (Linux, MacOS)
                subprocess.run(["xdg-open", output_file])
            elif os.name == 'nt':  # For Windows
                subprocess.run(["start", output_file], shell=True)
            else:
                raise OSError("Unsupported operating system")
        except Exception as e:
            print(f"Error playing audio: {e}")

def concatenate_audio_files(files, output_file):
    combined = AudioSegment.empty()
    for file in files:
        audio = AudioSegment.from_mp3(file)
        combined += audio
    
    combined.export(output_file, format='mp3')
    print(f'Audio content written to file "{output_file}"')

# Command-line arguments
parser = argparse.ArgumentParser(description='Convert text to speech.')
parser.add_argument('file_path', type=str, help='Path to the input text file.')
parser.add_argument('--lang', type=str, default='en', help='Language code (default: en).')
parser.add_argument('--output', type=str, default='output.mp3', help='Output audio file name (default: output.mp3).')
parser.add_argument('--play', action='store_true', help='Flag to control whether to play the audio after conversion.')
args = parser.parse_args()

# Convert text to speech
text_to_speech_gtts_large_file(args.file_path, args.lang, args.output, play_audio=args.play)
