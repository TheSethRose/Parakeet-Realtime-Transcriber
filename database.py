#!/usr/bin/env python3
"""
Database Module

Handles PostgreSQL database connections and recording storage
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
    """Manages PostgreSQL database operations for transcription recordings."""
    
    def __init__(self):
        """Initialize database connection using environment variables."""
        self.connection_params = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5433'),
            'database': os.getenv('POSTGRES_DB', 'transcription_db'),
            'user': os.getenv('POSTGRES_USER'),
            'password': os.getenv('POSTGRES_PASSWORD')
        }
        
        self.connection: Optional[PostgresConnection] = None
        self._setup_logging()
    
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
        Establish database connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = psycopg2.connect(**self.connection_params)
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
        recording_name: str, 
        segment_timestamp: float, 
        segment_text: str, 
        category: Optional[str] = None
    ) -> Optional[int]:
        """
        Insert a transcription segment into the database.
        
        Args:
            recording_name: Name of the recording session
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
    
    def get_recordings_by_name(self, recording_name: str) -> List[Dict[str, Any]]:
        """
        Get all segments for a specific recording.
        
        Args:
            recording_name: Name of the recording
            
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
                cursor.execute("""
                    SELECT * FROM recordings_formatted 
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


# Convenience functions for easy import
def save_transcription_segment(recording_name: str, timestamp: float, text: str, category: Optional[str] = None) -> bool:
    """
    Convenience function to save a transcription segment.
    
    Args:
        recording_name: Name of the recording
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


def get_recording_history(recording_name: str) -> List[Dict]:
    """
    Get all segments for a recording.
    
    Args:
        recording_name: Name of the recording
        
    Returns:
        List of recording segments
    """
    db = DatabaseManager()
    segments = db.get_recordings_by_name(recording_name)
    db.disconnect()
    return segments


if __name__ == "__main__":
    # Test the database connection
    db = DatabaseManager()
    if not db.test_connection():
        print("❌ Database connection failed!")
