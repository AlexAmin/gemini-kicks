# gemini-kicks
Initially built as a LlamaCon Hackathon 2025 Project using Llama API and Groq Inferencing to extract Basketball Highlights and compose sports clips in real-time as well as a full game summaries.
Reworked for Gemini and Soccer.


✨What Gemini does
- **team_recognition.py** (gemini-2.5-flash-preview-04-17 to detect the names of the teams using 8 keyframes in the video)
- **speech_to_text.py** (gemini-2.0-flash-lite to generate transcripts of the commentary of a soccer match - flash-light is used to save cost)
- **event_detection.py** (gemini-2.5-flash-preview-04-17 with thinking to detect events in transcriptions)
- **event_summary.py** (gemini-2.5-flash-preview-04-17 to summarize the entire match as a short podcast)
- **player_recognition.py** (gemini-2.5-flash-preview-04-17 to detect player names involved in highlights based on transcripts)

☁️Google Cloud
- **text_to_speech.py** (Gemini has no direct TTS yet so we'll substitue using GCP)

## ⚡ type of events
- FOUL: A violation of the rules by a player.
- PENALTY_KICK: A free kick awarded to the attacking team after a foul in the penalty area.
- CORNER_KICK: A free kick awarded to the attacking team when the ball goes out of bounds over the defending team's goal line after being last touched by a defender.
- THROW-IN: A method of restarting play when the ball has gone out over the touchline.
- OFFSIDE: A rule violation where an attacking player is in an illegal position when the ball is played to them.
- SUBSTITUTION: When one player is replaced by another player from the bench.
- GOAL: When the ball completely crosses the goal line between the posts and under the crossbar.
- YELLOW_CARD: A caution given to a player for committing a foul or misconduct.

## 📄 inputs
- Video of an entire soccer match

## 📺 outputs
- Individual clips from each highlight are detected with a sponsor overlay
- Full game narrated audio-only summary of all highlights

## ⚽🏈🎾 supporting other sports
- Adding support for other sports like football, soccer, tennis, is straight forward.
  - You need to identify the type of events that are relevant.
    - example for soccer: goals, corner kicks, red and yellow cards.
  - Update the prompts defined inside the folder **/prompts** to make use of those events. 

## 🧑‍💻 contributors
- Alex Amin, https://www.linkedin.com/in/alex-amin/
- Olcay Buyan, https://www.linkedin.com/in/olcaybuyan/