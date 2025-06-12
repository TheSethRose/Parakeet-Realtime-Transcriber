# Troubleshooting Guide

Common issues and solutions for the Parakeet Real-time Audio Transcriber.

## Installation Issues

### Python Environment Problems

**Issue: Python version incompatibility**
```
ERROR: Python 3.7 is not supported
```

**Solution:**
```bash
# Check Python version
python3 --version

# Install Python 3.9-3.11 via Homebrew
brew install python@3.10

# Create virtual environment with specific version
python3.10 -m venv .venv
source .venv/bin/activate
```

**Issue: Virtual environment creation fails**
```
ERROR: No module named 'venv'
```

**Solution:**
```bash
# Install venv module
python3 -m pip install --user virtualenv

# Alternative: Use virtualenv directly
virtualenv .venv
source .venv/bin/activate
```

### Dependency Installation

**Issue: Package installation fails**
```
ERROR: Failed building wheel for package
```

**Solution:**
```bash
# Update pip and setuptools
pip install --upgrade pip setuptools wheel

# Install build tools
xcode-select --install

# Retry installation
pip install -r requirements.txt
```

**Issue: NeMo installation problems**
```
ERROR: Could not find a version that satisfies the requirement nemo_toolkit
```

**Solution:**
```bash
# Install specific NeMo version
pip install nemo_toolkit[all]==1.20.0

# Alternative: Install from conda-forge
conda install -c conda-forge nemo_toolkit
```

## Audio System Issues

### Device Detection Problems

**Issue: No audio devices found**
```
ERROR: No suitable audio devices available
```

**Solution:**
```bash
# List all audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Reset audio system
sudo killall coreaudiod

# Check system preferences
open "/System/Preferences/Sound/"
```

**Issue: Microphone permission denied**
```
ERROR: [Errno -9999] Unanticipated host error
```

**Solution:**
1. **System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Microphone** from left sidebar
3. Check the box next to **Terminal** or your Python IDE
4. Restart the application

### Background Music Issues

**Issue: Background Music not working**
```
ERROR: Background Music device not found
```

**Solution:**
```bash
# Reinstall Background Music
brew uninstall background-music
brew install --cask background-music

# Open Background Music
open "/Applications/Background Music.app"

# Set as default output device in System Preferences
```

**Issue: Audio echoing/feedback**
```
Audio feedback loop detected
```

**Solution:**
```bash
# Reset audio system
sudo killall coreaudiod

# In Background Music app:
# 1. Set output device to headphones/speakers
# 2. Disable "Play through to other outputs"
# 3. Adjust output volume to 50-70%
```

### Audio Quality Problems

**Issue: Poor transcription accuracy**

**Possible Causes & Solutions:**

1. **Low audio quality:**
   ```bash
   # Test audio levels
   python -c "
   import sounddevice as sd
   import numpy as np
   
   def callback(indata, frames, time, status):
       volume = np.sqrt(np.mean(indata**2))
       print(f'Volume: {volume:.4f}')
   
   with sd.InputStream(callback=callback):
       input('Press Enter to stop...')
   "
   ```

2. **Background noise:**
   - Use noise-canceling microphone
   - Record in quiet environment
   - Adjust VAD aggressiveness

3. **Speaking too fast/unclear:**
   - Speak at normal conversational pace
   - Enunciate clearly
   - Use natural pauses

## Database Issues

### Connection Problems

**Issue: Database connection fails**
```
ERROR: connection to server failed
```

**Solution:**
```bash
# Check .env file exists and contains DATABASE_URL
cat .env

# Test connection manually
python -c "
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
url = os.getenv('DATABASE_URL')
print(f'URL: {url[:50]}...')

try:
    conn = psycopg2.connect(url)
    print('✅ Connection successful')
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

**Issue: SSL certificate problems**
```
ERROR: SSL SYSCALL error
```

**Solution:**
```bash
# Add SSL mode to connection string
# In .env file, ensure URL ends with: ?sslmode=require

# Test with different SSL modes
DATABASE_URL="postgresql://user:pass@host:port/db?sslmode=prefer"
```

### Schema Issues

**Issue: Table does not exist**
```
ERROR: relation "recordings" does not exist
```

**Solution:**
```bash
# Run database initialization
python -c "
from database import DatabaseManager
db = DatabaseManager()
print('✅ Database initialized')
"
```

**Issue: Permission denied on tables**
```
ERROR: permission denied for table recordings
```

**Solution:**
- Check database user permissions in Neon console
- Ensure user has read/write access to tables
- Verify connection string uses correct user

## Model Loading Issues

### Download Problems

**Issue: Model download fails**
```
ERROR: Failed to download parakeet_tdt_0.6b
```

**Solution:**
```bash
# Clear model cache
rm -rf ~/.cache/nemo

# Set custom cache directory
export NEMO_CACHE_DIR=/path/to/large/disk
mkdir -p $NEMO_CACHE_DIR

# Retry with verbose output
python -c "
import os
os.environ['NEMO_CACHE_DIR'] = '/tmp/nemo_cache'
from transcription import TranscriptionEngine
engine = TranscriptionEngine()
"
```

**Issue: Insufficient disk space**
```
ERROR: No space left on device
```

**Solution:**
```bash
# Check available space
df -h

# Clear cache and temporary files
rm -rf ~/.cache/nemo
rm -rf /tmp/nemo_*

# Use external drive for cache
export NEMO_CACHE_DIR="/Volumes/External/nemo_cache"
```

### Memory Issues

**Issue: Out of memory during model loading**
```
ERROR: CUDA out of memory
```

**Solution:**
```bash
# Check available RAM
top -l 1 -s 0 | grep PhysMem

# For systems with < 16GB RAM:
# 1. Close other applications
# 2. Use CPU-only mode (slower but less memory)

# Force CPU mode
export CUDA_VISIBLE_DEVICES=""
python main.py
```

## Runtime Issues

### Performance Problems

**Issue: High latency/delays**

**Diagnostic Steps:**
```bash
# Monitor system resources
top -pid $(pgrep -f "python main.py")

# Check audio buffer settings
python -c "
import sounddevice as sd
print(f'Default latency: {sd.default.latency}')
print(f'Default channels: {sd.default.channels}')
print(f'Default samplerate: {sd.default.samplerate}')
"
```

**Solutions:**
- Reduce `max_segment_duration` (faster processing, less context)
- Increase `min_segment_duration` (fewer but larger segments)
- Close resource-intensive applications

**Issue: Frequent crashes/freezes**

**Debug with logging:**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py 2>&1 | tee transcription.log

# Check log for errors
tail -f transcription.log
```

### Text Processing Issues

**Issue: Duplicate text appearing**

**Causes & Solutions:**
1. **Audio echo:** Fix Background Music configuration
2. **VAD sensitivity:** Lower aggressiveness level
3. **Buffer overlap:** Reduce overlap duration

**Issue: Missing words/sentences**

**Solutions:**
1. **Increase VAD sensitivity:** Use level 3 for quiet speech
2. **Check microphone positioning:** 6-12 inches from speaker
3. **Verify audio levels:** Should be consistent, not too quiet

## Error Code Reference

### Common Exit Codes

- **Exit 1:** General error (check logs)
- **Exit 2:** Invalid command line arguments  
- **Exit 130:** User interrupted (Ctrl+C)
- **SIGTERM:** Process terminated externally

### Database Error Codes

- **08001:** Connection refused
- **08006:** Connection failure  
- **42P01:** Table does not exist
- **42501:** Insufficient privileges

### Audio Error Codes

- **-9999:** Unanticipated host error (permissions)
- **-9998:** Invalid device ID
- **-9997:** Device unavailable

## Debugging Tools

### Log Analysis

```bash
# Enable comprehensive logging
export LOG_LEVEL=DEBUG
export PYTHONUNBUFFERED=1

# Run with logging
python main.py 2>&1 | tee debug.log

# Analyze logs
grep ERROR debug.log
grep WARNING debug.log
```

### System Information

```bash
# Gather system info for support
python -c "
import platform
import sys
import sounddevice as sd

print(f'OS: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'Audio devices: {len(sd.query_devices())}')
print(f'Default device: {sd.default.device}')
"
```

### Network Diagnostics

```bash
# Test database connectivity
ping your-neon-host.neon.tech

# Test port accessibility  
nc -zv your-neon-host.neon.tech 5432

# DNS resolution
nslookup your-neon-host.neon.tech
```

## Getting Help

### Before Reporting Issues

1. **Check logs:** Enable debug logging and review output
2. **Test minimal case:** Try with simple, short audio
3. **Verify environment:** Ensure all dependencies are installed
4. **Update software:** Make sure you have the latest version

### Information to Include

- **System details:** OS version, Python version, RAM
- **Error messages:** Complete error text and stack traces  
- **Steps to reproduce:** Exact sequence that causes the issue
- **Configuration:** Relevant settings and environment variables
- **Audio setup:** Device type, Background Music configuration

### Support Channels

- **GitHub Issues:** For bugs and feature requests
- **Documentation:** Check all docs in `/docs` folder first
- **Community:** Search existing issues for similar problems

## Performance Optimization

### System-Level Optimizations

```bash
# Increase file descriptor limits
ulimit -n 4096

# Optimize for audio processing
sudo sysctl -w kern.maxfiles=65536
sudo sysctl -w kern.maxfilesperproc=32768

# Reduce system audio latency
# System Preferences → Sound → Input → Configure → Reduce latency
```

### Application Tuning

```python
# Optimize transcriber settings for your use case

# For speed over accuracy:
transcriber = RealTimeTranscriber(
    max_segment_duration=10,    # Shorter segments
    min_segment_duration=3,     # Process sooner
    vad_aggressiveness=1        # Less strict VAD
)

# For accuracy over speed:
transcriber = RealTimeTranscriber(
    max_segment_duration=25,    # Longer context
    min_segment_duration=8,     # More content per segment
    vad_aggressiveness=3        # Strict VAD
)
```

## Next Steps

If issues persist after trying these solutions:

1. **Check [Setup Guide](setup.md)** for proper installation
2. **Review [Usage Guide](usage.md)** for correct operation
3. **Consult [API Documentation](api.md)** for integration issues
4. **Report new issues** with complete diagnostic information
