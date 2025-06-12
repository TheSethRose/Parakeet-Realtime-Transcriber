#!/usr/bin/env python3
"""
Export Combined Recordings to Markdown Files

Interactive script to export full transcriptions from the combined_recordings table
to markdown files with proper naming conventions.

Usage:
    python export.py                           # Interactive mode
    python export.py "Recording Title"         # Direct mode
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from dotenv import load_dotenv

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager

# Load environment variables
load_dotenv()


def sanitize_filename(name: str) -> str:
    """
    Convert recording name to a valid filename.
    
    Args:
        name: The recording name to sanitize
        
    Returns:
        Sanitized filename with .md extension
    """
    if not name:
        return "untitled-recording.md"
    
    # Convert to lowercase and replace spaces with dashes
    filename = name.lower()
    
    # Replace multiple spaces/whitespace with single dash
    filename = re.sub(r'\s+', '-', filename)
    
    # Remove special characters except dashes and alphanumeric
    filename = re.sub(r'[^a-z0-9\-]', '', filename)
    
    # Remove multiple consecutive dashes
    filename = re.sub(r'-+', '-', filename)
    
    # Remove leading/trailing dashes
    filename = filename.strip('-')
    
    # Ensure we have something left
    if not filename:
        filename = "untitled-recording"
    
    return f"{filename}.md"


def create_markdown_content(recording: Dict[str, Any]) -> str:
    """
    Create properly formatted markdown content for the recording.
    
    Args:
        recording: Dictionary containing recording data
        
    Returns:
        Formatted markdown content
    """
    title = recording.get('recording_name', 'Untitled Recording')
    content = recording.get('full_transcription', '')
    created_at = recording.get('created_at')
    segment_count = recording.get('segment_count', 0)
    total_duration = recording.get('total_duration')
    
    # Format the date
    date_str = "Unknown"
    if created_at:
        try:
            if isinstance(created_at, str):
                date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                date_obj = created_at
            date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
        except:
            date_str = str(created_at)
    
    # Format duration
    duration_str = "Unknown"
    if total_duration:
        try:
            if isinstance(total_duration, str):
                duration_str = total_duration
            else:
                duration_str = str(total_duration)
        except:
            duration_str = "Unknown"
    
    # Create markdown with front matter
    markdown_content = f"""---
title: "{title}"
date: "{date_str}"
segments: {segment_count}
duration: "{duration_str}"
source: "Audio Transcription"
---

# {title}

{content}

---

*Transcribed from {segment_count} audio segments*  
*Total Duration: {duration_str}*  
*Created: {date_str}*
"""
    
    return markdown_content


def display_combined_recordings(db: DatabaseManager) -> List[Dict[str, Any]]:
    """Display all combined recordings and return the list."""
    print("\n📚 Available Combined Recordings:")
    print("=" * 70)
    
    try:
        combined_recordings = db.get_combined_recordings()
        
        if not combined_recordings:
            print("   No combined recordings found in the database.")
            return []
        
        for i, recording in enumerate(combined_recordings, 1):
            title = recording.get('recording_name', 'Untitled Recording')
            segment_count = recording.get('segment_count', 0)
            created_at = recording.get('created_at', 'Unknown')
            
            # Format date for display
            date_str = "Unknown"
            if created_at and created_at != 'Unknown':
                try:
                    if isinstance(created_at, str):
                        date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        date_obj = created_at
                    date_str = date_obj.strftime("%Y-%m-%d")
                except:
                    date_str = str(created_at)
            
            # Get content preview
            content = recording.get('full_transcription', '')
            preview = content[:150] + "..." if len(content) > 150 else content
            
            print(f"   {i:2d}. {title}")
            print(f"       📊 {segment_count} segments | 📅 {date_str}")
            print(f"       📝 {preview}")
            print()
        
        return combined_recordings
        
    except Exception as e:
        print(f"   Error retrieving combined recordings: {e}")
        return []


def export_recording_interactive(db: DatabaseManager) -> bool:
    """Interactive mode to select and export a recording."""
    recordings = display_combined_recordings(db)
    
    if not recordings:
        return False
    
    try:
        # Get user selection
        while True:
            try:
                choice = input(f"\nSelect a recording to export (1-{len(recordings)}) or 'q' to quit: ").strip()
                
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
        title = selected_recording.get('recording_name', 'Untitled Recording')
        
        # Create export directory if it doesn't exist
        export_dir = Path('export')
        export_dir.mkdir(exist_ok=True)
        
        # Generate filename with export directory
        filename = sanitize_filename(title)
        filepath = export_dir / filename
        
        print(f"\n📋 Selected Recording: {title}")
        print(f"📄 Export filename: {filename}")
        print(f"📁 Export path: {filepath}")
        
        # Check if file exists
        if filepath.exists():
            overwrite = input(f"\n⚠️  File '{filepath}' already exists. Overwrite? (y/N): ").strip().lower()
            if overwrite != 'y':
                print("Export cancelled.")
                return False
        
        # Confirm export
        confirm = input(f"\nProceed with export? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Export cancelled.")
            return False
        
        # Create markdown content
        print("\n📝 Creating markdown content...")
        markdown_content = create_markdown_content(selected_recording)
        
        # Write to file
        print(f"💾 Saving to {filepath}...")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✅ Successfully exported to {filepath}")
        print(f"📏 File size: {len(markdown_content)} characters")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return False
    except Exception as e:
        print(f"\nError during export: {e}")
        return False


def export_recording_direct(db: DatabaseManager, recording_title: str) -> bool:
    """Direct mode to export a specific recording by title."""
    print(f"\n🔍 Looking for recording: '{recording_title}'")
    
    try:
        # Get all combined recordings
        recordings = db.get_combined_recordings()
        
        if not recordings:
            print("❌ No combined recordings found in database")
            return False
        
        # Find matching recording
        matching_recording = None
        for recording in recordings:
            if recording.get('recording_name', '').lower() == recording_title.lower():
                matching_recording = recording
                break
        
        if not matching_recording:
            print(f"❌ No recording found with title: '{recording_title}'")
            print("\n💡 Available recordings:")
            for recording in recordings:
                title = recording.get('recording_name', 'Untitled')
                print(f"   - {title}")
            return False
        
        # Create export directory if it doesn't exist
        export_dir = Path('export')
        export_dir.mkdir(exist_ok=True)
        
        # Generate filename with export directory
        filename = sanitize_filename(recording_title)
        filepath = export_dir / filename
        
        print(f"📋 Found recording: {recording_title}")
        print(f"📄 Export filename: {filename}")
        print(f"📁 Export path: {filepath}")
        
        # Check if file exists
        if filepath.exists():
            overwrite = input(f"\n⚠️  File '{filepath}' already exists. Overwrite? (y/N): ").strip().lower()
            if overwrite != 'y':
                print("Export cancelled.")
                return False
        
        # Create and save content
        print("\n📝 Creating markdown content...")
        markdown_content = create_markdown_content(matching_recording)
        
        print(f"💾 Saving to {filepath}...")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✅ Successfully exported to {filepath}")
        print(f"📏 File size: {len(markdown_content)} characters")
        
        return True
        
    except Exception as e:
        print(f"Error during direct export: {e}")
        return False


def main():
    """Main function to run the export script."""
    print("📤 Recording Export Tool")
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
            # Direct mode - recording title provided
            recording_title = sys.argv[1]
            success = export_recording_direct(db, recording_title)
        else:
            # Interactive mode
            success = export_recording_interactive(db)
        
        if success:
            print(f"\n🎉 Export completed successfully!")
            print("📁 Markdown file created in export/ directory")
        else:
            print(f"\n❌ Export failed or was cancelled")
            
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
