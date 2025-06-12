#!/usr/bin/env python3
"""
Real-time Audio Transcriber

Main orchestration module that coordinates audio capture, transcription,
and sentence processing for real-time audio transcription.
"""

import sys
import time
import threading
import queue
import numpy as np
import sounddevice as sd
from typing import Optional

# Import our modules
from audio_capture import AudioCapture, AudioSegmentManager
from transcription import TranscriptionEngine
from sentence_processor import SentenceProcessor

print("Starting Parakeet Audio Transcriber...")
print("Loading dependencies (this may take 30-60 seconds)...")

# Show progress while loading
loading_start = time.time()
print("Loading audio libraries...")
print("Loading NeMo ASR toolkit (this is the slow part)...")

loading_time = time.time() - loading_start
print(f"All dependencies loaded in {loading_time:.1f} seconds")


class RealTimeTranscriber:
    """Main orchestrator for real-time audio transcription."""
    
    def __init__(self, recording_name: Optional[str] = None, sample_rate=16000, 
                 max_segment_duration=20, min_segment_duration=5, vad_aggressiveness=2):
        """
        Initialize the real-time transcriber.
        
        Args:
            recording_name: Name of the recording session (None for no name)
            sample_rate: Audio sampling rate (16kHz for Parakeet)
            max_segment_duration: Maximum audio segment length (seconds)
            min_segment_duration: Minimum segment length before forcing transcription
            vad_aggressiveness: VAD sensitivity (0=least, 3=most aggressive)
        """
        self.sample_rate = sample_rate
        self.is_running = False
        
        # Audio queue for transcription worker
        self.audio_queue = queue.Queue()
        
        # Initialize components
        self.audio_capture = AudioCapture(sample_rate, vad_aggressiveness)
        self.segment_manager = AudioSegmentManager(sample_rate, max_segment_duration, min_segment_duration)
        self.transcription_engine = TranscriptionEngine(sample_rate)
        self.sentence_processor = SentenceProcessor(recording_name)
        
        print("Real-time transcriber initialized!")
    
    def audio_callback(self, indata, frames, time_info, status):
        """
        Audio callback function for processing incoming audio data.
        
        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Timing information
            status: Stream status
        """
        if status:
            print(f"Audio status: {status}")
        
        # Convert to mono and normalize
        audio_data = indata[:, 0] if indata.ndim > 1 else indata.flatten()
        current_time = time.time()
        
        # Add audio to current segment buffer
        self.segment_manager.add_audio_data(audio_data)
        
        # Process VAD for speech detection
        speech_detected_in_chunk = self.audio_capture.process_vad_frames(audio_data, current_time)
        
        # Check if we should transcribe current segment
        should_transcribe, transcribe_reason = self.segment_manager.should_transcribe_segment(
            self.audio_capture, current_time
        )
        
        # Trigger transcription
        if should_transcribe and len(self.segment_manager.current_segment) > 0:
            # Send segment for transcription
            self.audio_queue.put(self.segment_manager.get_segment_copy())
            
            # Reset segment buffer
            self.segment_manager.reset_segment()
            
            # Reset speech detection if we hit a pause/silence
            if transcribe_reason in ["natural pause", "silence timeout"]:
                self.segment_manager.reset_speech_state(self.audio_capture)
    
    def transcribe_worker(self):
        """Worker thread that processes audio chunks and transcribes them."""
        while self.is_running:
            try:
                # Get audio chunk from queue (with timeout)
                audio_chunk = self.audio_queue.get(timeout=1.0)
                
                # Transcribe the audio
                text = self.transcription_engine.transcribe_audio_chunk(audio_chunk)
                
                # Process transcription if we got valid text
                if text:
                    self.sentence_processor.process_transcription(text)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")
    
    def start_transcription(self, device: Optional[int] = None):
        """
        Start real-time audio transcription.
        
        Args:
            device: Audio input device ID (None for default)
        """
        print("\n" + "="*60)
        print("REAL-TIME AUDIO TRANSCRIPTION")
        print("="*60)
        print(f"Sample Rate: {self.sample_rate} Hz")
        print(f"Max Segment Duration: {self.segment_manager.max_segment_duration} seconds")
        print(f"Min Segment Duration: {self.segment_manager.min_segment_duration} seconds")
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


def get_user_input():
    """Get device selection and recording name from user."""
    print("Parakeet Real-time Audio Transcriber")
    print("=====================================")
    
    # Create audio capture instance to list devices
    audio_capture = AudioCapture()
    device = audio_capture.get_device_selection()
    
    # Ask for recording name
    print("\nRecording Information:")
    recording_name = input("Enter recording name (leave empty for no name): ").strip()
    if not recording_name:
        recording_name = None
    
    return device, recording_name

def display_session_info(recording_name: Optional[str]):
    """Display session information and features."""
    if recording_name:
        print(f"\n📝 Recording: {recording_name}")
        print("=" * (len(recording_name) + 13))
    else:
        print(f"\n📝 Recording: (No name)")
        print("=" * 19)
    print("\nEverything ready! Starting Parakeet-optimized transcription...")
    print("Features enabled:")
    print("   • Parakeet best practices (5-20 second segments)")
    print("   • Voice Activity Detection (VAD)")
    print("   • Smart pause detection (0.8s triggers processing)")
    print("   • Silence-based segmentation (1.5s full reset)")
    print("   • Sentence grouping & duplicate filtering")
    print("Optimized for complete sentences and better context")
    print("Press Ctrl+C to stop\n")


def main():
    """Main function to run the audio transcriber."""
    try:
        # Get user input
        device, recording_name = get_user_input()
        
        # Create transcriber
        print("\nInitializing transcriber...")
        transcriber = RealTimeTranscriber(recording_name=recording_name)
        
        # Display session info
        display_session_info(recording_name)
        
        # Start transcription
        transcriber.start_transcription(device=device)
        
    except KeyboardInterrupt:
        print("\nTranscription stopped by user.")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
