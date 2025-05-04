import os
import time
import tempfile
from groq import Groq

from util_io import get_temp_path

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def text_to_speech(text: str, output_dir="tts"):
    # Voices: https://console.groq.com/docs/text-to-speech
    timestamp = str(int(time.time()))
    speech_file_path = os.path.join(get_temp_path(output_dir), f"{timestamp}.wav")

    model = "playai-tts"
    voice = "Mikail-PlayAI"
    text = text
    response_format = "wav"

    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        response_format=response_format
    )
    response.write_to_file(speech_file_path)
    return speech_file_path

if __name__ == "__main__":
    speech_file_path = text_to_speech("Bayern and MBC are off to a shaky start, with both teams struggling with turnovers, currently tied at 6-6.")
    print(speech_file_path)


