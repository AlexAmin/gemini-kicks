![Alt text](assets/github-header.jpg)

# llama-hoops
LlamaCon Hackathon 2025 Project using Llama API and Groq Inferencing to extract Basketball Highlights and compose sports clips in real-time as well as a full game summary.

## type of events
- Free Throws
- Fouls
- Steals
- Turnovers
- Timeouts
- Substitutions

## inputs
- Video of an entire basketball match
  - During the hackathon, we used pre-recorded basketball games to simplify the developent.
  - Connecting a live stream should be easy, as the processing is done using a rolling window of video, very similar to chunks of video that would you would get from a live stream.

## outputs
- Individual clips from each highlight detected
- Full game narrated audio-only sumary of all highlights

## contributors
- Alex Amin, https://www.linkedin.com/in/alex-amin/
- Olcay Buyan, https://www.linkedin.com/in/olcaybuyan/