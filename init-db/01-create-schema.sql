-- Initialize Transcription Database Schema
-- This script runs automatically when the PostgreSQL container starts

-- Create recordings table to store transcription data
CREATE TABLE IF NOT EXISTS recordings (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    recording_name VARCHAR(255) NOT NULL,
    segment_timestamp INTERVAL NOT NULL,
    segment_text TEXT NOT NULL,
    category VARCHAR(100) DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_recordings_date ON recordings(date);
CREATE INDEX IF NOT EXISTS idx_recordings_name ON recordings(recording_name);
CREATE INDEX IF NOT EXISTS idx_recordings_category ON recordings(category);
CREATE INDEX IF NOT EXISTS idx_recordings_created_at ON recordings(created_at);

-- Create a function to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_recordings_updated_at 
    BEFORE UPDATE ON recordings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert a sample record for testing
INSERT INTO recordings (recording_name, segment_timestamp, segment_text, category) 
VALUES (
    'Sample Recording', 
    INTERVAL '00:01:30', 
    'This is a sample transcription segment for testing the database schema.',
    'test'
) ON CONFLICT DO NOTHING;

-- Create a view for easy querying of recordings with formatted timestamps
CREATE OR REPLACE VIEW recordings_formatted AS
SELECT 
    id,
    date,
    recording_name,
    segment_timestamp,
    EXTRACT(EPOCH FROM segment_timestamp)::INTEGER as segment_seconds,
    segment_text,
    category,
    created_at,
    updated_at
FROM recordings
ORDER BY date DESC, segment_timestamp ASC;
