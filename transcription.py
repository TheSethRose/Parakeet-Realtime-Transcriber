#!/usr/bin/env python3
"""
Transcription Module

Handles NeMo ASR model loading and audio transcription processing.
"""

import sys
import time
import tempfile
import os
from typing import List, Optional
from io import StringIO
import numpy as np
from scipy.io.wavfile import write
import nemo.collections.asr as nemo_asr


class TranscriptionEngine:
    """Manages NeMo ASR model and transcription processing."""
    
    def __init__(self, sample_rate=16000):
        """
        Initialize the transcription engine.
        
        Args:
            sample_rate: Audio sampling rate for transcription
        """
        self.sample_rate = sample_rate
        self.asr_model = None
        
        # Initialize model
        self._initialize_model()
        
        print("Transcription engine ready!")
    
    def _initialize_model(self):
        """Initialize the Parakeet model with suppressed output."""
        print("Initializing Parakeet TDT 0.6B V2 model...")
        print("   This will download ~600MB on first run...")
        model_start = time.time()
        
        # Suppress NeMo warnings and info messages
        import logging
        
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
    
    def transcribe_audio_chunk(self, audio_chunk: np.ndarray) -> Optional[str]:
        """
        Transcribe an audio chunk using the Parakeet model.
        
        Args:
            audio_chunk: Audio data as numpy array
            
        Returns:
            Transcribed text or None if transcription failed
        """
        if self.asr_model is None:
            print("❌ Model not initialized!")
            return None
        
        # Save audio chunk to temporary file
        temp_filename = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                # Convert to int16 for wav file
                audio_int16 = (audio_chunk * 32767).astype(np.int16)
                write(temp_file.name, self.sample_rate, audio_int16)
                temp_filename = temp_file.name
            
            # Transcribe the audio with suppressed tqdm output
            try:
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
                
                # Return cleaned text if substantial
                if text and text.strip() and len(text.strip()) > 3:
                    return text.strip()
                else:
                    return None
                    
            except Exception as e:
                print(f"❌ Transcription error: {e}")
                return None
        
        finally:
            # Clean up temporary file
            if temp_filename:
                try:
                    os.unlink(temp_filename)
                except:
                    pass
        
        return None
