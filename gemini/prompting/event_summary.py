import json
from typing import List

from google.genai import types

from gemini.gemini_client import gemini_client
from models.summary_length import SummaryLength
from models.transcription_segment import TranscriptionSegment
from utils_llm import load_prompt_file


def highlight_summary(transcripts: List[TranscriptionSegment], length=SummaryLength.SHORT) -> str:
    transcription_json = json.dumps([item.to_dict() for item in transcripts])
    base_prompt = load_prompt_file("prompts/event_summary_prompt.md")

    event_summary_xxl_prompt = load_prompt_file("prompts/event_summary_duration/event_summary_xxl_prompt.md")
    event_summary_long_prompt = load_prompt_file("prompts/event_summary_duration/event_summary_long_prompt.md")
    event_summary_medium_prompt = load_prompt_file("prompts/event_summary_duration/event_summary_medium_prompt.md")
    event_summary_short_prompt = load_prompt_file("prompts/event_summary_duration/event_summary_short_prompt.md")
    length_prompt = ""
    if length == SummaryLength.XXL:
        length_prompt = event_summary_xxl_prompt
    elif length == SummaryLength.LONG:
        length_prompt = event_summary_long_prompt
    elif length == SummaryLength.MEDIUM:
        length_prompt = event_summary_medium_prompt
    else:
        length_prompt = event_summary_short_prompt

    prompt = base_prompt.replace("{LENGTH_PROMPT}", length_prompt)
    completion = gemini_client.models.generate_content(
        model="gemini-2.5-flash-preview-04-17",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=1024),
            response_mime_type="text/plain",
            system_instruction=prompt
        ),
        contents=[
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=transcription_json)]
            ),

        ]
    )

    output = completion.text
    return output


if __name__ == "__main__":
    from test_data.demo_transcript import demo_transcript
    result = highlight_summary(demo_transcript, SummaryLength.MEDIUM)
    print(f"Event Summary: {result}")
