#!/usr/bin/env python3
"""
Sentence Processing Module

Handles sentence grouping, duplicate filtering, console output formatting,
and database storage of transcribed segments.
"""

import time
import re
from typing import Optional
from typing import List, Optional
from database import DatabaseManager


class SentenceProcessor:
    """Manages sentence grouping and duplicate filtering."""
    
    def __init__(self, recording_name: Optional[str] = None, min_sentence_length=10):
        """
        Initialize the sentence processor.
        
        Args:
            recording_name: Name of the recording session (None for no name)
            min_sentence_length: Minimum characters for a valid sentence
        """
        self.recording_name = recording_name
        self.min_sentence_length = min_sentence_length
        
        # Database manager for smart insertion
        self.db_manager = DatabaseManager()
        
        # Sentence processing state
        self.sentence_buffer = []
        self.last_transcription = ""
        
        # Timing for database timestamps
        self.session_start_time = time.time()
        
        print("Sentence processor initialized!")
    
    def is_duplicate(self, text: str) -> bool:
        """
        Enhanced duplicate detection.
        
        Args:
            text: New transcribed text
            
        Returns:
            True if text is considered a duplicate
        """
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
    
    def extract_complete_sentences(self) -> List[str]:
        """
        Extract and return multiple complete sentences from buffer.
        
        Returns:
            List of complete sentences
        """
        if not self.sentence_buffer:
            return []
            
        # Join all buffer text
        full_text = " ".join(self.sentence_buffer).strip()
        sentences = []
        
        # Split on sentence endings while preserving the punctuation
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
    
    def process_transcription(self, text: str):
        """
        Process transcription with sentence grouping and duplicate filtering.
        
        Args:
            text: Transcribed text to process
        """
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
                self.display_sentence(sentence.strip())
                self.save_to_database(sentence.strip())
                self.last_transcription = sentence.strip()
    
    def display_sentence(self, sentence: str):
        """
        Display a complete sentence with timestamp and recording name.
        
        Args:
            sentence: Complete sentence to display
        """
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{self.recording_name}] {sentence}")
    
    def save_to_database(self, sentence: str):
        """
        Save a transcribed sentence to the database.
        
        Args:
            sentence: Complete sentence to save
        """
        try:
            # Calculate timestamp from session start
            current_time = time.time()
            segment_timestamp = current_time - self.session_start_time
            
            # Save to database with smart combination
            record_id = self.db_manager.insert_recording_segment_smart(
                recording_name=self.recording_name,
                segment_timestamp=segment_timestamp,
                segment_text=sentence,
                category="transcription"  # You could make this configurable
            )
            
            if not record_id:
                print(f"⚠️  Warning: Failed to save segment to database")
            
        except Exception as e:
            print(f"⚠️  Database error: {e}")
    
    def get_recording_name(self) -> Optional[str]:
        """Get the current recording name."""
        return self.recording_name
    
    def set_recording_name(self, recording_name: Optional[str]):
        """Set a new recording name."""
        self.recording_name = recording_name
