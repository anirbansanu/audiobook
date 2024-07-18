import os
import argparse
import subprocess
from gtts import gTTS
from pydub import AudioSegment
from tqdm import tqdm

class TextToSpeechConverter:
    def __init__(self, file_path, lang='en', output_file='output.mp3', chunk_size=1024, play_audio=True):
        self.file_path = file_path
        self.lang = lang
        self.output_file = output_file
        self.chunk_size = chunk_size
        self.play_audio = play_audio
        self.chunk_files = []

        if not os.path.exists('audio_chunks'):
            os.makedirs('audio_chunks')

    def read_in_chunks(self, file_object):
        """Lazy function (generator) to read a file piece by piece."""
        while True:
            data = file_object.read(self.chunk_size)
            if not data:
                break
            yield data

    def create_audio_chunks(self):
        with open(self.file_path, 'r') as file:
            total_size = os.path.getsize(self.file_path)
            with tqdm(total=total_size, unit='B', unit_scale=True, desc='Processing') as pbar:
                for i, chunk in enumerate(self.read_in_chunks(file)):
                    tts = gTTS(text=chunk, lang=self.lang)
                    chunk_file = f'audio_chunks/chunk_{i}.mp3'
                    tts.save(chunk_file)
                    self.chunk_files.append(chunk_file)
                    pbar.update(len(chunk))
                    print(f"Chunk {i} created: {chunk_file}")

    def concatenate_audio_files(self):
        combined = AudioSegment.empty()
        for file in self.chunk_files:
            audio = AudioSegment.from_mp3(file)
            combined += audio
        
        combined.export(self.output_file, format='mp3')
        print(f'Audio content written to file "{self.output_file}"')

    def clean_up_chunks(self):
        for chunk_file in self.chunk_files:
            os.remove(chunk_file)

    def play_audio_file(self):
        try:
            if os.name == 'posix':  # For Unix-like systems (Linux, MacOS)
                subprocess.run(["xdg-open", self.output_file])
            elif os.name == 'nt':  # For Windows
                subprocess.run(["start", self.output_file], shell=True)
            else:
                raise OSError("Unsupported operating system")
        except Exception as e:
            print(f"Error playing audio: {e}")

    def convert_text_to_speech(self):
        self.create_audio_chunks()
        self.concatenate_audio_files()
        self.clean_up_chunks()
        if self.play_audio:
            self.play_audio_file()


# Command-line arguments
parser = argparse.ArgumentParser(description='Convert text to speech.')
parser.add_argument('file_path', type=str, help='Path to the input text file.')
parser.add_argument('--lang', type=str, default='en', help='Language code (default: en).')
parser.add_argument('--output', type=str, default='output.mp3', help='Output audio file name (default: output.mp3).')
parser.add_argument('--play', action='store_true', help='Flag to control whether to play the audio after conversion.')
args = parser.parse_args()

# Convert text to speech
converter = TextToSpeechConverter(args.file_path, args.lang, args.output, play_audio=args.play)
converter.convert_text_to_speech()
