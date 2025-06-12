# Setup Guide

This guide walks you through setting up the Parakeet Real-time Audio Transcriber on macOS.

## Prerequisites

- **macOS 10.15+** (Catalina or later)
- **Python 3.8+** (Python 3.9-3.11 recommended)
- **16GB RAM minimum** (for optimal model performance)
- **Microphone or audio input device**
- **Neon Database account** (for cloud database storage)

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/TheSethRose/Parakeet-Realtime-Transcriber.git
cd Parakeet-Realtime-Transcriber

# Run the automated setup script
chmod +x setup.sh
./setup.sh

# Activate the virtual environment
source .venv/bin/activate
```

### 2. Database Configuration

1. **Create a Neon Database:**
   - Visit [Neon Console](https://console.neon.tech)
   - Create a new project named "Transcription Database"
   - Copy the connection string

2. **Configure Environment:**
   ```bash
   # Copy the environment template
   cp .env.example .env
   
   # Edit .env with your database connection string
   nano .env
   ```
   
   Add your Neon database URL:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
   ```

3. **Initialize Database Schema:**
   The database tables will be created automatically on first run.

### 3. Audio Setup (macOS)

For **system audio capture** (capturing computer audio):

```bash
# Install Background Music app
brew install background-music
open /Applications/Background\ Music.app

# If you experience audio echoing issues:
sudo killall coreaudiod
```

For **microphone input**, no additional setup is required.

### 4. First Run

```bash
# Start the transcriber
python main.py
```

**First run will:**
- Download the Parakeet TDT 0.6B V2 model (~600MB)
- Initialize database tables
- Test audio device connectivity
- Begin real-time transcription

## Advanced Configuration

### Audio Device Selection

The system will automatically detect and list available audio devices:
- **Built-in microphone** for voice input
- **Background Music** virtual device for system audio
- **External audio interfaces** for professional setups

### Model Performance Tuning

The transcriber uses optimized settings for the Parakeet model:
- **Segment Duration:** 5-20 seconds (optimal for context)
- **VAD Aggressiveness:** Level 2 (balanced sensitivity)
- **Buffer Overlap:** 1 second (prevents word cutoff)

### Database Optimization

For high-volume transcription:
- **Smart Insertion:** Combines segments in the same second
- **Indexing:** Optimized for timestamp-based queries
- **Connection Pooling:** Managed automatically

## Troubleshooting

### Common Issues

**Model Download Fails:**
```bash
# Clear model cache and retry
rm -rf ~/.cache/nemo
python main.py
```

**Audio Device Not Found:**
```bash
# List available devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Reset audio system
sudo killall coreaudiod
```

**Database Connection Error:**
- Verify your `.env` file contains the correct Neon database URL
- Check network connectivity
- Ensure database exists and is accessible

**Background Music Issues:**
```bash
# Reinstall Background Music
brew uninstall background-music
brew install background-music
open /Applications/Background\ Music.app
```

### Performance Optimization

**For Better Accuracy:**
- Use a quality microphone in a quiet environment
- Speak clearly with natural pauses
- Avoid background music during voice transcription

**For System Audio:**
- Use Background Music app for best quality
- Set system volume to 50-70% for optimal signal
- Avoid audio feedback loops

## Next Steps

- See [Usage Guide](usage.md) for detailed operation instructions
- Check [API Documentation](api.md) for integration options
- View [Database Setup](DATABASE_SETUP.md) for advanced database configuration
- Review [Troubleshooting](troubleshooting.md) for common issues and solutions
