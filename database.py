#!/usr/bin/env python3
"""
Database Module

Handles Neon PostgreSQL database connections and recording storage
for the audio transcription system.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection as PostgresConnection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    """Manages Neon PostgreSQL database operations for transcription recordings."""
    
    def __init__(self):
        """Initialize database connection using Neon DATABASE_URL."""
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required for Neon connection")
        
        self.connection: Optional[PostgresConnection] = None
        self._setup_logging()
        self.connect()  # Establish connection during initialization
    
    def _setup_logging(self):
        """Setup logging for database operations."""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            # Set to WARNING to suppress INFO messages during normal operation
            self.logger.setLevel(logging.WARNING)
    
    def connect(self) -> bool:
        """
        Establish database connection using Neon DATABASE_URL.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = psycopg2.connect(self.database_url)
            # Silent connection - only log errors
            return True
        except psycopg2.Error as e:
            self.logger.error(f"Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            # Silent disconnection - only log errors
    
    def insert_recording_segment(
        self, 
        recording_name: Optional[str], 
        segment_timestamp: float, 
        segment_text: str, 
        category: Optional[str] = None
    ) -> Optional[int]:
        """
        Insert a transcription segment into the database.
        
        Args:
            recording_name: Name of the recording session (None for no name)
            segment_timestamp: Timestamp in seconds from recording start
            segment_text: Transcribed text segment
            category: Optional category for the recording
            
        Returns:
            int: ID of inserted record, None if failed
        """
        if not self.connection:
            if not self.connect():
                return None
        
        if self.connection is None:
            return None
        
        try:
            # Convert timestamp to PostgreSQL interval
            interval = timedelta(seconds=segment_timestamp)
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO recordings (recording_name, segment_timestamp, segment_text, category)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (recording_name, interval, segment_text, category))
                
                result = cursor.fetchone()
                if result:
                    record_id = result[0]
                    self.connection.commit()
                    # Silent successful insert - only log errors
                    return record_id
                return None
                
        except psycopg2.Error as e:
            self.logger.error(f"Failed to insert recording segment: {e}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def insert_recording_segment_smart(
        self, 
        recording_name: Optional[str], 
        segment_timestamp: float, 
        segment_text: str, 
        category: Optional[str] = None
    ) -> Optional[int]:
        """
        Insert a transcription segment with intelligent second-based combination.
        
        If a segment already exists for the same second, append the new text to it.
        Otherwise, create a new segment.
        
        Args:
            recording_name: Name of the recording session (None for no name)
            segment_timestamp: Timestamp in seconds from recording start
            segment_text: Transcribed text segment
            category: Optional category for the recording
            
        Returns:
            int: ID of inserted/updated record, None if failed
        """
        if not self.connection:
            if not self.connect():
                return None
        
        if self.connection is None:
            return None
        
        try:
            # Extract the second portion of the timestamp (ignore subseconds)
            timestamp_seconds = int(segment_timestamp)
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Check if there's already a segment for this second
                if recording_name is None:
                    cursor.execute("""
                        SELECT id, segment_text 
                        FROM recordings 
                        WHERE recording_name IS NULL 
                        AND EXTRACT(EPOCH FROM segment_timestamp)::INTEGER = %s
                        ORDER BY id ASC
                        LIMIT 1
                    """, (timestamp_seconds,))
                else:
                    cursor.execute("""
                        SELECT id, segment_text 
                        FROM recordings 
                        WHERE recording_name = %s 
                        AND EXTRACT(EPOCH FROM segment_timestamp)::INTEGER = %s
                        ORDER BY id ASC
                        LIMIT 1
                    """, (recording_name, timestamp_seconds))
                
                existing_segment = cursor.fetchone()
                
                if existing_segment:
                    # Append to existing segment
                    existing_text = existing_segment['segment_text']
                    combined_text = f"{existing_text} {segment_text}".strip()
                    
                    cursor.execute("""
                        UPDATE recordings 
                        SET segment_text = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        RETURNING id
                    """, (combined_text, existing_segment['id']))
                    
                    result = cursor.fetchone()
                    self.connection.commit()
                    return result['id'] if result else None
                    
                else:
                    # Create new segment
                    return self.insert_recording_segment(recording_name, segment_timestamp, segment_text, category)
                    
        except psycopg2.Error as e:
            self.logger.error(f"Failed to insert/update recording segment: {e}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def get_recordings_by_name(self, recording_name: Optional[str]) -> List[Dict[str, Any]]:
        """
        Get all segments for a specific recording.
        
        Args:
            recording_name: Name of the recording (None for no name)
            
        Returns:
            List of recording segments as dictionaries
        """
        if not self.connection:
            if not self.connect():
                return []
        
        if self.connection is None:
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if recording_name is None:
                    cursor.execute("""
                        SELECT id, date, recording_name, segment_timestamp, segment_text, 
                               category, created_at, updated_at,
                               EXTRACT(EPOCH FROM segment_timestamp)::INTEGER as segment_seconds
                        FROM recordings 
                        WHERE recording_name IS NULL 
                        ORDER BY segment_timestamp
                    """)
                else:
                    cursor.execute("""
                        SELECT id, date, recording_name, segment_timestamp, segment_text, 
                               category, created_at, updated_at,
                               EXTRACT(EPOCH FROM segment_timestamp)::INTEGER as segment_seconds
                        FROM recordings 
                        WHERE recording_name = %s 
                        ORDER BY segment_timestamp
                    """, (recording_name,))
                
                return [dict(record) for record in cursor.fetchall()]
                
        except psycopg2.Error as e:
            self.logger.error(f"Failed to fetch recordings: {e}")
            return []
    
    def get_recent_recordings(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get recordings from the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of recent recordings
        """
        if not self.connection:
            if not self.connect():
                return []
        
        if self.connection is None:
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT DISTINCT recording_name, date, category, 
                           COUNT(*) as segment_count,
                           MIN(created_at) as started_at,
                           MAX(created_at) as last_updated
                    FROM recordings 
                    WHERE date >= CURRENT_DATE - INTERVAL '%s days'
                    GROUP BY recording_name, date, category
                    ORDER BY date DESC, started_at DESC
                """, (days,))
                
                return [dict(record) for record in cursor.fetchall()]
                
        except psycopg2.Error as e:
            self.logger.error(f"Failed to fetch recent recordings: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test database connection and basic functionality.
        
        Returns:
            bool: True if test successful
        """
        if not self.connect():
            return False
        
        if self.connection is None:
            return False
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM recordings")
                result = cursor.fetchone()
                if result:
                    count = result[0]
                    # For test output, we'll use print instead of logger
                    print(f"✅ Database connection and schema working correctly! Found {count} recording segments.")
                    return True
                return False
        except psycopg2.Error as e:
            self.logger.error(f"Database test failed: {e}")
            return False
        finally:
            self.disconnect()
    
    def combine_recording_segments(self, recording_name: Optional[str], combined_title: str) -> Optional[int]:
        """
        Combine all segments for a recording into a single entry in combined_recordings table.
        
        Args:
            recording_name: Name of the recording to combine (None for unnamed recordings)
            combined_title: Title for the combined recording
            
        Returns:
            ID of the combined recording entry, or None if failed
        """
        if self.connection is None:
            return None
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get all segments for this recording, ordered by timestamp
                if recording_name is None:
                    cursor.execute("""
                        SELECT segment_text, segment_timestamp, 
                               EXTRACT(EPOCH FROM segment_timestamp)::INTEGER as segment_seconds
                        FROM recordings 
                        WHERE recording_name IS NULL 
                        ORDER BY segment_timestamp
                    """)
                else:
                    cursor.execute("""
                        SELECT segment_text, segment_timestamp,
                               EXTRACT(EPOCH FROM segment_timestamp)::INTEGER as segment_seconds
                        FROM recordings 
                        WHERE recording_name = %s 
                        ORDER BY segment_timestamp
                    """, (recording_name,))
                
                segments = cursor.fetchall()
                
                if not segments:
                    self.logger.warning(f"No segments found for recording: {recording_name}")
                    return None
                
                # Combine all segment texts with newlines for better readability
                full_transcription = "\n".join([segment['segment_text'] for segment in segments])
                
                # Calculate total duration (last timestamp)
                max_timestamp = max(segments, key=lambda x: x['segment_seconds'])['segment_timestamp']
                segment_count = len(segments)
                
                # Insert into combined_recordings table
                cursor.execute("""
                    INSERT INTO combined_recordings 
                    (recording_name, full_transcription, total_duration, segment_count)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (combined_title, full_transcription, max_timestamp, segment_count))
                
                result = cursor.fetchone()
                self.connection.commit()
                
                combined_id = result['id'] if result else None
                
                if combined_id:
                    self.logger.info(f"Successfully combined {segment_count} segments into recording ID {combined_id}")
                
                return combined_id
                
        except psycopg2.Error as e:
            self.logger.error(f"Failed to combine recording segments: {e}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def delete_recording_segments(self, recording_name: Optional[str]) -> int:
        """
        Delete all segments for a specific recording.
        
        Args:
            recording_name: Name of the recording to delete (None for no name)
            
        Returns:
            Number of segments deleted, or -1 if failed
        """
        if self.connection is None:
            return -1
        
        try:
            with self.connection.cursor() as cursor:
                # Delete all segments for this recording
                if recording_name is None:
                    cursor.execute("""
                        DELETE FROM recordings 
                        WHERE recording_name IS NULL
                    """)
                else:
                    cursor.execute("""
                        DELETE FROM recordings 
                        WHERE recording_name = %s
                    """, (recording_name,))
                
                deleted_count = cursor.rowcount
                self.connection.commit()
                
                if deleted_count > 0:
                    self.logger.info(f"Successfully deleted {deleted_count} segments for recording: {recording_name or '(No name)'}")
                
                return deleted_count
                
        except psycopg2.Error as e:
            self.logger.error(f"Failed to delete recording segments: {e}")
            if self.connection:
                self.connection.rollback()
            return -1
    
    def get_combined_recordings(self) -> List[Dict[str, Any]]:
        """
        Get all combined recordings.
        
        Returns:
            List of combined recording dictionaries
        """
        if self.connection is None:
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, recording_name, full_transcription, total_duration, 
                           segment_count, created_at, updated_at
                    FROM combined_recordings 
                    ORDER BY created_at DESC
                """)
                
                return [dict(record) for record in cursor.fetchall()]
                
        except psycopg2.Error as e:
            self.logger.error(f"Failed to fetch combined recordings: {e}")
            return []
    
    def get_combined_recording_by_name(self, recording_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific combined recording by name.
        
        Args:
            recording_name: Name of the combined recording
            
        Returns:
            Combined recording dictionary or None if not found
        """
        if self.connection is None:
            return None
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, recording_name, full_transcription, total_duration, 
                           segment_count, created_at, updated_at
                    FROM combined_recordings 
                    WHERE recording_name = %s
                """, (recording_name,))
                
                result = cursor.fetchone()
                return dict(result) if result else None
                
        except psycopg2.Error as e:
            self.logger.error(f"Failed to fetch combined recording: {e}")
            return None
        

# Convenience functions for easy import
def save_transcription_segment(recording_name: Optional[str], timestamp: float, text: str, category: Optional[str] = None) -> bool:
    """
    Convenience function to save a transcription segment.
    
    Args:
        recording_name: Name of the recording (None for no name)
        timestamp: Timestamp in seconds
        text: Transcribed text
        category: Optional category
        
    Returns:
        bool: True if saved successfully
    """
    db = DatabaseManager()
    record_id = db.insert_recording_segment(recording_name, timestamp, text, category)
    db.disconnect()
    return record_id is not None


def get_recording_history(recording_name: Optional[str]) -> List[Dict]:
    """
    Get all segments for a recording.
    
    Args:
        recording_name: Name of the recording (None for no name)
        
    Returns:
        List of recording segments
    """
    db = DatabaseManager()
    segments = db.get_recordings_by_name(recording_name)
    db.disconnect()
    return segments


def delete_recording_segments_by_name(recording_name: Optional[str]) -> int:
    """
    Convenience function to delete all segments for a recording.
    
    Args:
        recording_name: Name of the recording to delete (None for no name)
        
    Returns:
        Number of segments deleted, or -1 if failed
    """
    db = DatabaseManager()
    deleted_count = db.delete_recording_segments(recording_name)
    db.disconnect()
    return deleted_count


if __name__ == "__main__":
    # Test the database connection
    db = DatabaseManager()
    if not db.test_connection():
        print("❌ Database connection failed!")
