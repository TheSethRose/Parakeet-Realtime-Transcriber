#!/usr/bin/env python3
"""
Recording Combination Script

Combines all segments for a recording into a single entry in the combined_recordings table.
Optionally deletes the original segments after combining.

Usage:
    python combine.py                                    # Interactive mode
    python combine.py "The Evolution of Thoughtful Online Search"  # Direct mode
"""

import os
import sys
from typing import Optional, List, Dict, Any, Tuple
from datetime import timedelta, datetime
from dotenv import load_dotenv

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager

# Load environment variables
load_dotenv()


def format_time_display(time_value) -> str:
    """Format time value for display, handling both datetime and timedelta objects."""
    if time_value is None:
        return "Unknown"
    
    # Handle timedelta objects (segment_timestamp)
    if isinstance(time_value, timedelta):
        total_seconds = int(time_value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    # Handle datetime objects
    if hasattr(time_value, 'strftime'):
        return time_value.strftime("%H:%M:%S")
    
    # Handle string values
    if isinstance(time_value, str):
        return time_value
    
    # Fallback
    return str(time_value)


def display_available_recordings(db: DatabaseManager) -> List[Tuple[Any, ...]]:
    """Display all available recordings and return the list."""
    print("\n📋 Available Recording Sessions:")
    print("=" * 70)
    
    # Get distinct recording names with segment counts
    try:
        if db.connection is None:
            print("   No database connection.")
            return []
            
        with db.connection.cursor() as cursor:
            cursor.execute("""
                SELECT recording_name, 
                       COUNT(*) as segment_count,
                       MIN(segment_timestamp) as first_segment,
                       MAX(segment_timestamp) as last_segment,
                       DATE(MIN(created_at)) as date
                FROM recordings 
                GROUP BY recording_name
                ORDER BY DATE(MIN(created_at)) DESC, MIN(segment_timestamp) DESC
            """)
            
            recordings = cursor.fetchall()
            
            if not recordings:
                print("   No recordings found in the database.")
                return []
            
            for i, record in enumerate(recordings, 1):
                name = record[0] if record[0] else "(No name)"
                count = record[1]
                first_time = format_time_display(record[2])
                last_time = format_time_display(record[3])
                date = record[4].strftime("%Y-%m-%d") if record[4] else "Unknown"
                
                print(f"   {i:2d}. {name}")
                print(f"       📊 {count} segments | 📅 {date} | ⏰ {first_time} - {last_time}")
                print()
                
            return recordings
            
    except Exception as e:
        print(f"   Error retrieving recordings: {e}")
        return []


def get_recording_details(db: DatabaseManager, recording_name: Optional[str]) -> Dict[str, Any]:
    """Get detailed information about a recording's segments."""
    try:
        if db.connection is None:
            return {}
            
        with db.connection.cursor() as cursor:
            if recording_name is None:
                cursor.execute("""
                    SELECT COUNT(*) as total_segments,
                           MIN(segment_timestamp) as first_segment,
                           MAX(segment_timestamp) as last_segment,
                           STRING_AGG(segment_text, ' ' ORDER BY segment_timestamp) as preview
                    FROM recordings 
                    WHERE recording_name IS NULL
                """)
            else:
                cursor.execute("""
                    SELECT COUNT(*) as total_segments,
                           MIN(segment_timestamp) as first_segment,
                           MAX(segment_timestamp) as last_segment,
                           STRING_AGG(segment_text, ' ' ORDER BY segment_timestamp) as preview
                    FROM recordings 
                    WHERE recording_name = %s
                """, (recording_name,))
            
            result = cursor.fetchone()
            
            if result and result[0] > 0:
                preview_text = result[3][:200] + "..." if result[3] and len(result[3]) > 200 else result[3] or ""
                
                return {
                    'total_segments': result[0],
                    'first_segment': result[1],
                    'last_segment': result[2],
                    'preview': preview_text
                }
            
            return {}
            
    except Exception as e:
        print(f"Error getting recording details: {e}")
        return {}


def combine_recording_interactive(db: DatabaseManager) -> bool:
    """Interactive mode to select and combine a recording."""
    recordings = display_available_recordings(db)
    
    if not recordings:
        return False
    
    try:
        # Get user selection
        while True:
            try:
                choice = input(f"\nSelect a recording to combine (1-{len(recordings)}) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    print("Operation cancelled.")
                    return False
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(recordings):
                    break
                else:
                    print(f"Please enter a number between 1 and {len(recordings)}")
                    
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
        
        # Get selected recording
        selected_recording = recordings[choice_num - 1]
        recording_name = selected_recording[0]
        
        # Show recording details
        print(f"\n📋 Selected Recording: {recording_name or '(No name)'}")
        print("-" * 50)
        
        details = get_recording_details(db, recording_name)
        if details:
            print(f"📊 Total segments: {details['total_segments']}")
            print(f"⏰ Duration: {details['first_segment']} - {details['last_segment']}")
            print(f"📝 Preview: {details['preview']}")
        
        # Get title for combined recording
        print(f"\n📝 Enter title for combined recording:")
        default_title = recording_name if recording_name else "Combined Recording"
        combined_title = input(f"Title (default: '{default_title}'): ").strip()
        
        if not combined_title:
            combined_title = default_title
        
        # Confirm combination
        print(f"\n🔄 Ready to combine:")
        print(f"   Recording: {recording_name or '(No name)'}")
        print(f"   Title: {combined_title}")
        print(f"   Segments: {details.get('total_segments', 'Unknown')}")
        
        confirm = input("\nProceed with combination? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled.")
            return False
        
        # Perform combination
        print("\n🔄 Combining segments...")
        combined_id = db.combine_recording_segments(recording_name, combined_title)
        
        if combined_id:
            print(f"✅ Successfully combined into record ID: {combined_id}")
            
            # Ask about deleting original segments
            delete_confirm = input("\n🗑️  Delete original segments? (y/N): ").strip().lower()
            if delete_confirm == 'y':
                print("🗑️  Deleting original segments...")
                deleted_count = db.delete_recording_segments(recording_name)
                
                if deleted_count > 0:
                    print(f"✅ Successfully deleted {deleted_count} original segments")
                else:
                    print("❌ Failed to delete original segments")
            else:
                print("ℹ️  Original segments preserved")
            
            return True
        else:
            print("❌ Failed to combine segments")
            return False
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return False
    except Exception as e:
        print(f"\nError during combination: {e}")
        return False


def combine_recording_direct(db: DatabaseManager, recording_name: str) -> bool:
    """Direct mode to combine a specific recording by name."""
    print(f"\n🔍 Looking for recording: '{recording_name}'")
    
    # Check if recording exists
    details = get_recording_details(db, recording_name)
    if not details:
        print(f"❌ No segments found for recording: '{recording_name}'")
        return False
    
    print(f"📊 Found {details['total_segments']} segments")
    print(f"📝 Preview: {details['preview']}")
    
    # Use recording name as title
    combined_title = f"{recording_name} - Complete Transcript"
    
    print(f"\n🔄 Combining segments into: '{combined_title}'")
    combined_id = db.combine_recording_segments(recording_name, combined_title)
    
    if combined_id:
        print(f"✅ Successfully combined into record ID: {combined_id}")
        
        # Ask about deleting original segments
        delete_confirm = input("\n🗑️  Delete original segments? (y/N): ").strip().lower()
        if delete_confirm == 'y':
            print("🗑️  Deleting original segments...")
            deleted_count = db.delete_recording_segments(recording_name)
            
            if deleted_count > 0:
                print(f"✅ Successfully deleted {deleted_count} original segments")
            else:
                print("❌ Failed to delete original segments")
        else:
            print("ℹ️  Original segments preserved")
        
        return True
    else:
        print("❌ Failed to combine segments")
        return False


def main():
    """Main function to run the combination script."""
    print("🎙️  Recording Combination Tool")
    print("=" * 50)
    
    # Initialize database connection
    db = DatabaseManager()
    if not db.connection:
        print("❌ Failed to connect to database")
        print("   Please check your .env file and database configuration")
        sys.exit(1)
    
    try:
        # Check for command line argument
        if len(sys.argv) > 1:
            # Direct mode - recording name provided
            recording_name = sys.argv[1]
            success = combine_recording_direct(db, recording_name)
        else:
            # Interactive mode
            success = combine_recording_interactive(db)
        
        if success:
            print(f"\n🎉 Combination completed successfully!")
        else:
            print(f"\n❌ Combination failed or was cancelled")
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        # Close database connection
        if db.connection:
            db.connection.close()


if __name__ == "__main__":
    main()
