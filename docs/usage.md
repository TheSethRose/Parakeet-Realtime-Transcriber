# Usage Guide

Complete guide to using the Parakeet Real-time Audio Transcriber for various transcription scenarios.

## Basic Operation

### Starting a Transcription Session

```bash
# Activate environment and start
source .venv/bin/activate
python main.py
```

### Session Setup

1. **Device Selection:** Choose your audio input device
2. **Recording Name:** Enter a name for your session (or leave empty for no name)
3. **Real-time Processing:** The system begins transcribing immediately

### Session Features

- **📝 Real-time Display:** Transcriptions appear instantly with timestamps
- **🎯 Smart Segmentation:** Natural sentence boundaries preserved
- **🔍 Duplicate Filtering:** Removes redundant text automatically
- **💾 Auto-saving:** All segments saved to database continuously
- **⏱️ Timestamp Tracking:** Precise timing for each segment

## Recording Scenarios

### Voice Meetings & Interviews

**Best Practices:**
- Use built-in microphone or external mic
- Speak clearly with natural pauses
- Position microphone 6-12 inches from speaker
- Minimize background noise

**Example Session:**
```
📝 Recording: Board Meeting - Q4 Review
=====================================

[00:00:15] Welcome everyone to our quarterly review meeting.
[00:00:23] Let's start with the financial performance overview.
[00:00:31] Revenue grew by twelve percent compared to last quarter.
```

### System Audio Transcription

**Use Cases:**
- YouTube videos
- Online lectures
- Podcast transcription
- Webinar content

**Setup:**
1. Install Background Music app
2. Select "Background Music" as audio device
3. Play your content normally
4. Transcription captures system audio

**Example Session:**
```
📝 Recording: What is Generative AI?
==================================

[00:01:12] Generative AI refers to artificial intelligence systems that can create new content.
[00:01:24] These models learn patterns from training data to generate text, images, or code.
[00:01:33] Popular examples include GPT models for text and DALL-E for images.
```

### Lecture & Educational Content

**Optimal Settings:**
- 16kHz sampling rate (default)
- VAD Level 2 for classroom environments
- Smart pause detection for natural breaks

## Managing Recordings

### Viewing Active Session

During transcription, you'll see:
- **Real-time segments** with timestamps
- **Session name** at the top
- **Feature status** indicators
- **Live processing** confirmation

### Database Storage

All transcriptions are automatically saved with:
- **Segment Text:** The transcribed content
- **Timestamp:** Precise timing information
- **Recording Name:** Session identifier (or NULL if none)
- **Category:** Optional classification
- **Date:** Creation timestamp

### Combining Segments

The database module provides built-in methods to combine segments programmatically:

```python
from database import DatabaseManager

# Initialize database connection
db = DatabaseManager()

# Combine all segments for a specific recording
combined_id = db.combine_recording_segments(
    recording_name="Meeting Notes",
    combined_title="Weekly Team Meeting Summary"
)

# Get all combined recordings
combined_recordings = db.get_combined_recordings()
```

**Programmatic Combination:**
1. All segments for a recording are merged into one entry
2. Combined text includes natural paragraph breaks
3. Total duration and segment count are preserved
4. Saved to `combined_recordings` table with metadata

**Example Combined Result:**
```
Title: "What is Generative AI?"
Content: "Generative AI refers to artificial intelligence systems that can create new content.
These models learn patterns from training data to generate text, images, or code.
Popular examples include GPT models for text and DALL-E for images."
Duration: 00:02:15
Segments: 8 combined
```

## Advanced Features

### Smart Segment Combination

The system automatically combines segments that occur within the same second:
- **Real-time Merging:** Overlapping speech consolidated instantly
- **Context Preservation:** Natural sentence flow maintained
- **Duplicate Elimination:** Redundant phrases filtered out

### Voice Activity Detection (VAD)

Intelligent audio processing:
- **Silence Detection:** Automatically pauses during quiet periods
- **Speech Boundaries:** Natural sentence segmentation
- **Noise Filtering:** Reduces interference from background sounds

### Recording Name Management

**Named Sessions:**
```
Enter recording name: "Team Standup - Sprint 23"
📝 Recording: Team Standup - Sprint 23
```

**Anonymous Sessions:**
```
Enter recording name (leave empty for no name): [Enter]
📝 Recording: (No name)
```

## Workflow Examples

### Academic Research

1. **Interview Transcription:**
   ```bash
   python main.py
   # Name: "Interview - Dr. Smith - Climate Research"
   # Use microphone input
   ```

2. **Lecture Capture:**
   ```bash
   python main.py
   # Name: "Physics 101 - Quantum Mechanics"
   # Use Background Music for recorded lectures
   ```

### Content Creation

1. **Podcast Transcription:**
   ```bash
   python main.py
   # Name: "Tech Talk Episode 15"
   # Background Music for audio files
   ```

2. **Video Content:**
   ```bash
   python main.py
   # Name: "YouTube - How to Build Apps"
   # System audio capture
   ```

### Business Use

1. **Meeting Minutes:**
   ```bash
   python main.py
   # Name: "All-Hands Meeting - June 2025"
   # Conference room microphone
   ```

2. **Client Calls:**
   ```bash
   python main.py
   # Name: "Client Discovery - Acme Corp"
   # Headset microphone recommended
   ```

## Keyboard Controls

- **Ctrl+C:** Stop transcription and save session
- **Background operation:** Runs continuously until stopped
- **Automatic saving:** No manual save required

## Quality Tips

### For Best Accuracy

**Audio Quality:**
- Use quality microphone when possible
- Minimize background noise
- Maintain consistent volume levels
- Avoid audio compression if possible

**Speaking Practices:**
- Speak clearly and naturally
- Use normal conversational pace
- Allow natural pauses between sentences
- Avoid talking over others in meetings

**Environment:**
- Choose quiet spaces for voice input
- Use headphones to prevent audio feedback
- Test audio levels before important sessions

### Troubleshooting Quality Issues

**Low Accuracy:**
- Check microphone positioning
- Reduce background noise
- Verify audio device selection
- Test with shorter segments first

**Missing Speech:**
- Increase VAD sensitivity if needed
- Check audio input levels
- Verify device connectivity
- Try different microphone

**Duplicate Text:**
- System automatically filters duplicates
- May indicate audio echo or feedback
- Check Background Music configuration
- Restart audio system if needed

## Next Steps

- Learn about [Database Management](DATABASE_SETUP.md)
- Explore [API Integration](api.md)  
- Review [Troubleshooting Guide](troubleshooting.md)
- Check [Performance Optimization](optimization.md)
