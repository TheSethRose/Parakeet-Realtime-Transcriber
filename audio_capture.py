#!/usr/bin/env python3
"""
Audio Capture Module

Handles audio device discovery, Voice Activity Detection (VAD),
and real-time audio stream management.
"""

import warnings
import sounddevice as sd
import numpy as np

# Suppress webrtcvad pkg_resources deprecation warning
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
    import webrtcvad

import time
import collections
from typing import Optional, Tuple


class AudioCapture:
    """Manages audio input devices and VAD processing."""
    
    def __init__(self, sample_rate=16000, vad_aggressiveness=2):
        """
        Initialize audio capture with VAD.
        
        Args:
            sample_rate: Audio sampling rate (16kHz for Parakeet)
            vad_aggressiveness: VAD sensitivity (0=least, 3=most aggressive)
        """
        self.sample_rate = sample_rate
        self.vad_aggressiveness = vad_aggressiveness
        
        # VAD setup
        self.vad = webrtcvad.Vad(vad_aggressiveness)
        self.vad_frame_duration = 30  # ms
        self.vad_frame_size = int(sample_rate * self.vad_frame_duration / 1000)
        
        # Speech detection state
        self.speech_detected = False
        self.last_speech_time = time.time()
        self.speech_start_time = None
        self.silence_frames = 0
        self.speech_frames = 0
        self.is_speech_active = False
        
        print("Audio capture and VAD initialized!")
    
    def list_devices(self):
        """List available audio input devices."""
        print("\nAvailable Audio Input Devices:")
        print("-" * 40)
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device.get('max_input_channels', 0) > 0:
                print(f"{i}: {device.get('name', 'Unknown')} (max channels: {device.get('max_input_channels', 0)})")
    
    def get_device_selection(self) -> Optional[int]:
        """Get device selection from user."""
        self.list_devices()
        print("\nDevice Selection:")
        device_input = input("Enter device ID (or press Enter for default): ").strip()
        return int(device_input) if device_input.isdigit() else None
    
    def process_vad_frames(self, audio_data, current_time) -> bool:
        """
        Process audio data through VAD and return speech detection results.
        
        Args:
            audio_data: Audio data as numpy array
            current_time: Current timestamp
            
        Returns:
            bool: True if speech detected in this chunk
        """
        speech_detected_in_chunk = False
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
        
        return speech_detected_in_chunk


class AudioSegmentManager:
    """Manages audio segmentation and timing logic."""
    
    def __init__(self, sample_rate=16000, max_segment_duration=20, min_segment_duration=5):
        """
        Initialize audio segment manager.
        
        Args:
            sample_rate: Audio sampling rate
            max_segment_duration: Maximum audio segment length (seconds)
            min_segment_duration: Minimum segment length before forcing transcription
        """
        self.sample_rate = sample_rate
        self.max_segment_duration = max_segment_duration
        self.min_segment_duration = min_segment_duration
        self.max_segment_size = int(sample_rate * max_segment_duration)
        self.min_segment_size = int(sample_rate * min_segment_duration)
        
        # Timing thresholds
        self.pause_threshold = 0.8  # seconds of pause to trigger processing
        self.silence_threshold = 1.5  # seconds of silence before processing
        
        # Current audio segment
        self.current_segment = np.array([], dtype=np.float32)
        
        # Rolling buffer for continuity
        self.overlap_duration = 3.0  # seconds of overlap between segments
        self.overlap_samples = int(sample_rate * self.overlap_duration)
        self.previous_segment = np.array([], dtype=np.float32)
        
        print("Audio segment manager ready!")
    
    def add_audio_data(self, audio_data):
        """Add audio data to current segment."""
        self.current_segment = np.append(self.current_segment, audio_data)
    
    def should_transcribe_segment(self, capture: AudioCapture, current_time) -> Tuple[bool, str]:
        """
        Determine if current audio segment should be transcribed.
        
        Args:
            capture: AudioCapture instance for timing information
            current_time: Current timestamp
            
        Returns:
            Tuple of (should_transcribe, reason)
        """
        segment_duration = len(self.current_segment) / self.sample_rate
        time_since_speech = current_time - capture.last_speech_time
        
        should_transcribe = False
        transcribe_reason = ""
        
        if capture.is_speech_active:
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
        
        return should_transcribe, transcribe_reason
    
    def get_segment_copy(self) -> np.ndarray:
        """Get a copy of the current segment."""
        return self.current_segment.copy()
    
    def reset_segment(self):
        """Reset the current segment buffer."""
        self.current_segment = np.array([], dtype=np.float32)
    
    def reset_speech_state(self, capture: AudioCapture):
        """Reset speech detection state."""
        capture.is_speech_active = False
        capture.speech_frames = 0
