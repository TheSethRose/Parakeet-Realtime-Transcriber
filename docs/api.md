# API Documentation

Technical reference for integrating with the Parakeet Real-time Audio Transcriber components.

## Core Components

### DatabaseManager Class

Primary interface for database operations and transcription storage.

#### Initialization

```python
from database import DatabaseManager

# Initialize with automatic connection
db = DatabaseManager()

# Manual connection
db.connect()
```

#### Methods

##### `insert_recording_segment_smart(recording_name, segment_timestamp, segment_text, category=None)`

Intelligently inserts transcription segments with automatic combination.

**Parameters:**
- `recording_name` (Optional[str]): Session name or None for anonymous
- `segment_timestamp` (float): Timestamp in seconds from recording start
- `segment_text` (str): Transcribed text content
- `category` (Optional[str]): Optional classification tag

**Returns:**
- `Optional[int]`: Record ID if successful, None on error

**Example:**
```python
db = DatabaseManager()
record_id = db.insert_recording_segment_smart(
    recording_name="Team Meeting",
    segment_timestamp=45.5,
    segment_text="Let's review the quarterly results.",
    category="business"
)
```

##### `get_recordings_by_name(recording_name)`

Retrieves all segments for a specific recording session.

**Parameters:**
- `recording_name` (Optional[str]): Recording name or None for anonymous sessions

**Returns:**
- `List[Dict[str, Any]]`: List of recording segments with metadata

**Example:**
```python
segments = db.get_recordings_by_name("Team Meeting")
for segment in segments:
    print(f"[{segment['segment_seconds']}s] {segment['segment_text']}")
```

##### `combine_recording_segments(recording_name, combined_title, delete_original=False)`

Combines multiple segments into a single consolidated entry.

**Parameters:**
- `recording_name` (Optional[str]): Source recording name
- `combined_title` (str): Title for the combined entry
- `delete_original` (bool): Whether to remove original segments

**Returns:**
- `Optional[int]`: Combined record ID if successful

**Example:**
```python
combined_id = db.combine_recording_segments(
    recording_name="Lecture Series",
    combined_title="Introduction to Machine Learning",
    delete_original=True
)
```

##### `get_recent_recordings(days=7)`

Fetches recordings from the specified time period.

**Parameters:**
- `days` (int): Number of days to look back (default: 7)

**Returns:**
- `List[Dict[str, Any]]`: Recent recording sessions with metadata

### RealTimeTranscriber Class

Main orchestrator for real-time audio transcription.

#### Initialization

```python
from main import RealTimeTranscriber

transcriber = RealTimeTranscriber(
    recording_name="My Session",  # Optional[str]
    sample_rate=16000,           # Audio sampling rate
    max_segment_duration=20,     # Maximum segment length
    min_segment_duration=5,      # Minimum segment before processing
    vad_aggressiveness=2         # VAD sensitivity (0-3)
)
```

#### Methods

##### `start_transcription(device_id)`

Begins real-time transcription with specified audio device.

**Parameters:**
- `device_id` (int): Audio device identifier from sounddevice

**Example:**
```python
# Get available devices
import sounddevice as sd
devices = sd.query_devices()

# Start transcription
transcriber = RealTimeTranscriber("My Recording")
transcriber.start_transcription(device_id=1)
```

### SentenceProcessor Class

Handles intelligent text processing and database storage.

#### Key Features

- **Smart Grouping:** Combines related segments automatically
- **Duplicate Filtering:** Removes redundant text
- **Timestamp Management:** Maintains precise timing
- **Database Integration:** Seamless storage with smart insertion

#### Usage

```python
from sentence_processor import SentenceProcessor

processor = SentenceProcessor("Session Name")
processor.process_transcription("Hello world", 10.5)
```

## Database Schema

### Primary Tables

#### `recordings` Table

Stores individual transcription segments.

**Columns:**
- `id` (SERIAL PRIMARY KEY): Unique identifier
- `date` (DATE): Recording date
- `recording_name` (TEXT): Session name (nullable)
- `segment_timestamp` (INTERVAL): Time offset from start
- `segment_text` (TEXT): Transcribed content
- `category` (TEXT): Optional classification
- `created_at` (TIMESTAMPTZ): Creation timestamp
- `updated_at` (TIMESTAMPTZ): Last modification time

#### `combined_recordings` Table

Stores consolidated transcription entries.

**Columns:**
- `id` (SERIAL PRIMARY KEY): Unique identifier
- `title` (TEXT NOT NULL): Combined entry title
- `content` (TEXT NOT NULL): Full transcription text
- `original_recording_name` (TEXT): Source session name
- `total_duration` (INTERVAL): Total recording length
- `segment_count` (INTEGER): Number of combined segments
- `created_at` (TIMESTAMPTZ): Creation timestamp

### Indexes

- `idx_recordings_name_timestamp`: Optimized for session queries
- `idx_recordings_date`: Fast date-based filtering
- `idx_combined_recordings_title`: Quick title searches

## Convenience Functions

### Direct Database Operations

```python
# Quick segment saving
from database import save_transcription_segment

success = save_transcription_segment(
    recording_name="Quick Test",
    timestamp=30.0,
    text="This is a test segment",
    category="test"
)

# Retrieve recording history
from database import get_recording_history

history = get_recording_history("Quick Test")
```

### Audio Device Utilities

```python
# List available devices
import sounddevice as sd
print(sd.query_devices())

# Test device connectivity
from audio_capture import AudioCapture
capture = AudioCapture()
device = capture.get_device_selection()
```

## Integration Examples

### Custom Transcription Pipeline

```python
from database import DatabaseManager
from sentence_processor import SentenceProcessor
from transcription import TranscriptionEngine

# Initialize components
db = DatabaseManager()
processor = SentenceProcessor("Custom Session")
engine = TranscriptionEngine()

# Process audio data
def process_audio_chunk(audio_data, timestamp):
    # Transcribe audio
    text = engine.transcribe(audio_data)
    
    # Process and store
    if text:
        processor.process_transcription(text, timestamp)
        
# Usage
audio_chunk = get_audio_data()  # Your audio source
process_audio_chunk(audio_chunk, 45.0)
```

### Batch Processing

```python
from database import DatabaseManager

db = DatabaseManager()

# Process multiple files
recordings = [
    ("file1.wav", "Lecture 1"),
    ("file2.wav", "Lecture 2"),
    ("file3.wav", "Lecture 3")
]

for audio_file, name in recordings:
    # Your transcription logic
    segments = transcribe_file(audio_file)
    
    for timestamp, text in segments:
        db.insert_recording_segment_smart(
            recording_name=name,
            segment_timestamp=timestamp,
            segment_text=text
        )
```

### Real-time Monitoring

```python
from database import DatabaseManager
import time

db = DatabaseManager()

def monitor_recent_activity():
    """Monitor recent transcription activity."""
    recent = db.get_recent_recordings(days=1)
    
    for recording in recent:
        print(f"Session: {recording['recording_name']}")
        print(f"Segments: {recording['segment_count']}")
        print(f"Duration: {recording['total_duration']}")
        print("---")

# Run monitoring
while True:
    monitor_recent_activity()
    time.sleep(60)  # Check every minute
```

## Error Handling

### Database Errors

```python
from database import DatabaseManager
import psycopg2

db = DatabaseManager()

try:
    record_id = db.insert_recording_segment_smart(
        recording_name="Test",
        segment_timestamp=10.0,
        segment_text="Test content"
    )
    if record_id is None:
        print("Failed to insert segment")
        
except psycopg2.Error as e:
    print(f"Database error: {e}")
    
finally:
    db.disconnect()
```

### Audio Processing Errors

```python
from main import RealTimeTranscriber
import sounddevice as sd

try:
    transcriber = RealTimeTranscriber("Error Test")
    transcriber.start_transcription(device_id=999)  # Invalid device
    
except sd.PortAudioError as e:
    print(f"Audio device error: {e}")
    
except Exception as e:
    print(f"Transcription error: {e}")
```

## Performance Considerations

### Database Optimization

- **Batch Inserts:** Group multiple segments for better performance
- **Connection Pooling:** Reuse database connections
- **Index Usage:** Leverage timestamp and name indexes for queries

### Memory Management

- **Model Loading:** Parakeet model requires ~2GB RAM
- **Audio Buffers:** Optimize buffer sizes for your use case
- **Segment Processing:** Process segments incrementally for long sessions

### Real-time Processing

- **VAD Tuning:** Adjust sensitivity based on environment
- **Buffer Overlap:** Balance context preservation with latency
- **Thread Management:** Separate audio capture from transcription processing

## Configuration

### Environment Variables

```bash
# Database connection
DATABASE_URL=postgresql://user:pass@host:port/db

# Optional: Custom model cache
NEMO_CACHE_DIR=/path/to/cache

# Optional: Logging level
LOG_LEVEL=INFO
```

### Runtime Parameters

```python
# Transcriber configuration
config = {
    'sample_rate': 16000,        # Audio sampling rate
    'vad_aggressiveness': 2,     # VAD sensitivity
    'max_segment_duration': 20,  # Maximum segment length
    'min_segment_duration': 5,   # Minimum before processing
    'buffer_overlap': 1.0        # Overlap for context
}

transcriber = RealTimeTranscriber(**config)
```

## Next Steps

- Review [Setup Guide](setup.md) for installation
- Check [Usage Guide](usage.md) for operational details
- See [Troubleshooting](troubleshooting.md) for common issues
