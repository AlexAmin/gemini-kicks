import os

from google.cloud import texttospeech

from util_io import get_temp_path


def text_to_speech(text: str, players="", output_dir="tts"):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Chirp3-HD-Achernar"
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    speech_file_path = os.path.join(get_temp_path(output_dir), f"audio_summary-{players}.wav")

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    with open(speech_file_path, "wb") as out:
        out.write(response.audio_content)

    return speech_file_path

if __name__ == "__main__":
    speech_file_path = text_to_speech("Bayern and MBC are off to a shaky start, with both teams struggling with turnovers, currently tied at 6-6.")
    print(speech_file_path)


