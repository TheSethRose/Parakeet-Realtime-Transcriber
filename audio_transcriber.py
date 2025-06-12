#!/usr/bin/env python3
"""
Simple Real-time Audio Transcription using Parakeet TDT 0.6B V2

This script captures system audio (or microphone) and transcribes it in real-time
using NVIDIA's Parakeet model. Keep it running to see live transcriptions.
"""

import sys
import time
from typing import Any

print("Starting Parakeet Audio Transcriber...")
print("Loading dependencies (this may take 30-60 seconds)...")

# Show progress while loading heavy imports
loading_start = time.time()

print("Loading audio libraries...")
import sounddevice as sd
import numpy as np
import tempfile
import os
import threading
import queue
from scipy.io.wavfile import write
import webrtcvad
import collections

print("Loading NeMo ASR toolkit (this is the slow part)...")
import nemo.collections.asr as nemo_asr

from typing import Any

loading_time = time.time() - loading_start
print(f"All dependencies loaded in {loading_time:.1f} seconds")

class AudioTranscriber:
    def __init__(self, sample_rate=16000, max_segment_duration=20, min_segment_duration=5, vad_aggressiveness=2):
        """
        Initialize the audio transcriber using Parakeet best practices.
        
        Args:
            sample_rate: Audio sampling rate (16kHz for Parakeet)
            max_segment_duration: Maximum audio segment length (seconds) - Parakeet handles up to 24 minutes
            min_segment_duration: Minimum segment length before forcing transcription
            vad_aggressiveness: VAD sensitivity (0=least, 3=most aggressive)
        """
        self.sample_rate = sample_rate
        self.max_segment_duration = max_segment_duration
        self.min_segment_duration = min_segment_duration
        self.max_segment_size = int(sample_rate * max_segment_duration)
        self.min_segment_size = int(sample_rate * min_segment_duration)
        self.vad_aggressiveness = vad_aggressiveness
        
        # Audio buffer and queue
        self.audio_queue = queue.Queue()
        self.is_running = False
        
        # VAD setup
        self.vad = webrtcvad.Vad(vad_aggressiveness)
        self.vad_frame_duration = 30  # ms
        self.vad_frame_size = int(sample_rate * self.vad_frame_duration / 1000)
        
        # Speech detection and timing
        self.speech_detected = False
        self.last_speech_time = time.time()
        self.speech_start_time = None
        self.pause_threshold = 0.8  # seconds of pause to trigger processing
        self.silence_threshold = 1.5  # seconds of silence before processing
        
        # Sentence grouping
        self.sentence_buffer = []
        self.last_transcription = ""
        self.min_sentence_length = 10  # minimum characters for a sentence
        
        # Rolling buffer for continuity (prevents losing text at segment boundaries)
        self.overlap_duration = 3.0  # seconds of overlap between segments
        self.overlap_samples = int(sample_rate * self.overlap_duration)
        self.previous_segment = np.array([], dtype=np.float32)
        self.context_buffer = []  # Store recent transcriptions for context matching
        
        # Audio buffering for longer segments (Parakeet best practice)
        self.speech_buffer = collections.deque(maxlen=self.max_segment_size)
        self.current_segment = np.array([], dtype=np.float32)
        self.silence_frames = 0
        self.speech_frames = 0
        self.is_speech_active = False
        
        # Load Parakeet model
        print("Initializing Parakeet TDT 0.6B V2 model...")
        print("   This will download ~600MB on first run...")
        model_start = time.time()
        
        # Suppress NeMo warnings and info messages
        import logging
        import sys
        from io import StringIO
        
        # Temporarily suppress logging
        nemo_logger = logging.getLogger('nemo_logger')
        old_level = nemo_logger.level
        nemo_logger.setLevel(logging.ERROR)
        
        # Also capture stdout/stderr 
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        
        try:
            self.asr_model = nemo_asr.models.ASRModel.from_pretrained(
                model_name="nvidia/parakeet-tdt-0.6b-v2"
            )
        finally:
            # Restore logging and output
            nemo_logger.setLevel(old_level)
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        model_time = time.time() - model_start
        print(f"Model loaded successfully in {model_time:.1f} seconds!")
        
        print("VAD and sentence grouping ready!")
        
    def audio_callback(self, indata, frames, time_info, status):
        """Enhanced callback using Parakeet best practices with longer segments."""
        if status:
            print(f"Audio status: {status}")
        
        # Convert to mono and normalize
        audio_data = indata[:, 0] if indata.ndim > 1 else indata.flatten()
        current_time = time.time()
        
        # Add audio to current segment buffer
        self.current_segment = np.append(self.current_segment, audio_data)
        
        # VAD processing for speech detection
        speech_detected_in_chunk = False
        
        # Process audio in VAD-compatible frames
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        for i in range(0, len(audio_int16) - self.vad_frame_size + 1, self.vad_frame_size):
            frame = audio_int16[i:i + self.vad_frame_size]
            
            try:
                is_speech = self.vad.is_speech(frame.tobytes(), self.sample_rate)
                
                if is_speech:
                    speech_detected_in_chunk = True
                    self.speech_frames += 1
                    self.silence_frames = 0
                    self.last_speech_time = current_time
                    
                    # Track speech start
                    if not self.is_speech_active:
                        self.speech_start_time = current_time
                        self.is_speech_active = True
                else:
                    self.silence_frames += 1
                    
            except Exception:
                # VAD might fail on some frames, continue processing
                pass
        
        # Decision logic for when to transcribe (following Parakeet best practices)
        segment_duration = len(self.current_segment) / self.sample_rate
        time_since_speech = current_time - self.last_speech_time
        
        should_transcribe = False
        transcribe_reason = ""
        
        if self.is_speech_active:
            # Natural pause detection (0.8 seconds)
            if (time_since_speech > self.pause_threshold and 
                segment_duration >= self.min_segment_duration):
                should_transcribe = True
                transcribe_reason = "natural pause"
            
            # Maximum segment length reached
            elif segment_duration >= self.max_segment_duration:
                should_transcribe = True
                transcribe_reason = "max duration"
                
        else:
            # Extended silence - process any remaining audio
            if (time_since_speech > self.silence_threshold and 
                segment_duration >= 1.0):  # At least 1 second of audio
                should_transcribe = True
                transcribe_reason = "silence timeout"
        
        # Trigger transcription
        if should_transcribe and len(self.current_segment) > 0:
            # Send segment for transcription
            self.audio_queue.put(self.current_segment.copy())
            
            # Reset segment buffer
            self.current_segment = np.array([], dtype=np.float32)
            
            # Reset speech detection if we hit a pause/silence
            if transcribe_reason in ["natural pause", "silence timeout"]:
                self.is_speech_active = False
                self.speech_frames = 0
    
    def transcribe_worker(self):
        """Worker thread that processes audio chunks and transcribes them with sentence grouping."""
        while self.is_running:
            try:
                # Get audio chunk from queue (with timeout)
                audio_chunk = self.audio_queue.get(timeout=1.0)
                
                # Save audio chunk to temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    # Convert to int16 for wav file
                    audio_int16 = (audio_chunk * 32767).astype(np.int16)
                    write(temp_file.name, self.sample_rate, audio_int16)
                    temp_filename = temp_file.name
                
                # Transcribe the audio
                try:
                    # Suppress tqdm progress bar
                    import sys
                    from io import StringIO
                    
                    # Capture stderr to suppress tqdm output
                    old_stderr = sys.stderr
                    sys.stderr = StringIO()
                    
                    try:
                        # Type: ignore for NeMo model inference issue
                        output = self.asr_model.transcribe([temp_filename])  # type: ignore
                    finally:
                        # Always restore stderr
                        sys.stderr = old_stderr
                    
                    text = output[0].text if output and len(output) > 0 and hasattr(output[0], 'text') else ""
                    
                    # Process transcription with sentence grouping
                    if text and text.strip() and len(text.strip()) > 3:
                        # Process for sentence grouping (this will handle the display)
                        self.process_transcription(text.strip())
                        
                except Exception as e:
                    print(f"❌ Transcription error: {e}")
                
                # Clean up temporary file
                try:
                    os.unlink(temp_filename)
                except:
                    pass
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")

    def process_transcription(self, text):
        """Process transcription with advanced sentence grouping and duplicate filtering."""
        # Check for duplicates
        if self.is_duplicate(text):
            return
            
        # Add to sentence buffer
        self.sentence_buffer.append(text)
        
        # Try to extract complete sentences
        complete_sentences = self.extract_complete_sentences()
        
        # Display complete sentences
        for sentence in complete_sentences:
            if sentence and len(sentence.strip()) > 15:  # Only show substantial sentences
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] {sentence.strip()}")
                self.last_transcription = sentence.strip()

    def is_duplicate(self, text):
        """Enhanced duplicate detection."""
        if not self.last_transcription:
            return False
            
        # Normalize text for comparison
        text_words = set(text.lower().split())
        last_words = set(self.last_transcription.lower().split())
        
        if not text_words:
            return True
            
        # If more than 80% overlap, consider duplicate
        overlap = len(text_words & last_words) / len(text_words)
        
        # Also check if new text is just a subset of previous
        if text.lower().strip() in self.last_transcription.lower():
            return True
            
        return overlap > 0.8

    def extract_complete_sentences(self):
        """Extract and return multiple complete sentences from buffer."""
        if not self.sentence_buffer:
            return []
            
        # Join all buffer text
        full_text = " ".join(self.sentence_buffer).strip()
        sentences = []
        
        # Split on sentence endings while preserving the punctuation
        import re
        sentence_parts = re.split(r'([.!?])', full_text)
        
        current_sentence = ""
        for i in range(0, len(sentence_parts), 2):
            if i < len(sentence_parts):
                current_sentence += sentence_parts[i]
                # Add punctuation if it exists
                if i + 1 < len(sentence_parts):
                    current_sentence += sentence_parts[i + 1]
                    # We have a complete sentence
                    if current_sentence.strip() and len(current_sentence.strip()) >= self.min_sentence_length:
                        sentences.append(current_sentence.strip())
                    current_sentence = ""
        
        # Handle remaining incomplete text
        if current_sentence.strip():
            # If it's substantial but incomplete, keep it in buffer
            if len(current_sentence.strip()) >= self.min_sentence_length:
                self.sentence_buffer = [current_sentence.strip()]
            else:
                self.sentence_buffer = []
        else:
            self.sentence_buffer = []
            
        return sentences
    
    def start_transcription(self, device=None):
        """
        Start real-time audio transcription.
        
        Args:
            device: Audio input device ID (None for default)
        """
        print("\n" + "="*60)
        print("REAL-TIME AUDIO TRANSCRIPTION")
        print("="*60)
        print(f"Sample Rate: {self.sample_rate} Hz")
        print(f"Max Segment Duration: {self.max_segment_duration} seconds")
        print(f"Min Segment Duration: {self.min_segment_duration} seconds")
        print("Press Ctrl+C to stop")
        print("-"*60)
        
        self.is_running = True
        
        # Start transcription worker thread
        transcription_thread = threading.Thread(target=self.transcribe_worker)
        transcription_thread.daemon = True
        transcription_thread.start()
        
        try:
            # Start audio input stream
            with sd.InputStream(
                callback=self.audio_callback,
                channels=1,
                samplerate=self.sample_rate,
                device=device,
                blocksize=1024
            ):
                print("Recording... (listening for audio)")
                
                # Keep the main thread alive
                while self.is_running:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\nStopping transcription...")
        except Exception as e:
            print(f"\nError: {e}")
        finally:
            self.is_running = False
            print("Transcription stopped.")

def list_audio_devices():
    """List available audio input devices."""
    print("\nAvailable Audio Input Devices:")
    print("-" * 40)
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device.get('max_input_channels', 0) > 0:
            print(f"{i}: {device.get('name', 'Unknown')} (max channels: {device.get('max_input_channels', 0)})")

def main():
    """Main function to run the audio transcriber."""
    print("Parakeet Real-time Audio Transcriber")
    print("=====================================")
    
    # List available devices
    list_audio_devices()
    
    # Ask user for device selection
    print("\nDevice Selection:")
    device_input = input("Enter device ID (or press Enter for default): ").strip()
    device = int(device_input) if device_input.isdigit() else None
    
    # Create and start transcriber
    print("\nInitializing transcriber...")
    transcriber = AudioTranscriber()
    
    print("\nEverything ready! Starting Parakeet-optimized transcription...")
    print("Features enabled:")
    print("   • Parakeet best practices (5-20 second segments)")
    print("   • Voice Activity Detection (VAD)")
    print("   • Smart pause detection (0.8s triggers processing)")
    print("   • Silence-based segmentation (1.5s full reset)")
    print("   • Sentence grouping & duplicate filtering")
    print("Optimized for complete sentences and better context")
    print("Press Ctrl+C to stop\n")
    
    transcriber.start_transcription(device=device)

if __name__ == "__main__":
    main()
