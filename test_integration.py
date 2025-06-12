#!/usr/bin/env python3
"""
Integration Test Script

Tests the complete transcription pipeline with database integration.
"""

import time
from sentence_processor import SentenceProcessor
from database import get_recording_history

def test_integration():
    """Test complete integration from processing to database storage."""
    print("🧪 Testing Complete Integration Pipeline")
    print("=" * 50)
    
    # Create test recording session
    test_recording = f"Integration Test {int(time.time())}"
    processor = SentenceProcessor(test_recording)
    
    print(f"\n📝 Testing recording: '{test_recording}'")
    
    # Simulate several transcription segments
    test_sentences = [
        "Welcome to the integration test.",
        "This is testing sentence grouping and database storage.",
        "Each sentence should be saved to PostgreSQL automatically.",
        "The system processes complete sentences and filters duplicates.",
        "Finally, we can verify everything is stored correctly."
    ]
    
    print("\n🎯 Processing test sentences...")
    for i, sentence in enumerate(test_sentences, 1):
        print(f"  {i}. Processing: '{sentence[:30]}...'")
        processor.process_transcription(sentence)
        time.sleep(0.5)  # Small delay between processing
    
    # Verify database storage
    print("\n🗄️  Verifying database storage...")
    time.sleep(1)  # Allow database operations to complete
    
    history = get_recording_history(test_recording)
    print(f"  Found {len(history)} segments in database")
    
    if history:
        print("\n📋 Database Contents:")
        for i, segment in enumerate(history, 1):
            print(f"  {i}. [{segment['segment_timestamp']}] {segment['segment_text'][:50]}...")
    
    # Test summary
    success = len(history) == len(test_sentences)
    print(f"\n{'✅' if success else '❌'} Integration Test {'PASSED' if success else 'FAILED'}")
    print(f"  Expected: {len(test_sentences)} segments")
    print(f"  Found: {len(history)} segments")
    
    return success

if __name__ == "__main__":
    try:
        test_integration()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
