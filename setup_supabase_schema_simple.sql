-- Simplified Supabase Schema for Global Astrology Database
-- Run this in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS astrology_charts (
    id SERIAL PRIMARY KEY,
    
    -- Personal Information
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    time_of_birth TIME NOT NULL,
    place_of_birth VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    timezone_name VARCHAR(100) NOT NULL,
    
    -- Categories (simplified)
    primary_category VARCHAR(100),
    sub_category VARCHAR(100),
    specific_condition VARCHAR(100),
    
    -- Additional Details
    description TEXT,
    outcome VARCHAR(50) DEFAULT 'unknown',
    severity VARCHAR(50) DEFAULT 'unknown',
    timing VARCHAR(50) DEFAULT 'unknown',
    
    -- Travel Specific
    travel_country VARCHAR(100),
    travel_city VARCHAR(100),
    travel_purpose VARCHAR(255),
    travel_outcome VARCHAR(255),
    
    -- Research Details
    researcher_id VARCHAR(100),
    consent_given BOOLEAN DEFAULT FALSE,
    anonymize BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(100) DEFAULT 'system',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Planetary Positions - Core planets only
    sun_longitude DECIMAL(10, 6),
    sun_rasi VARCHAR(50),
    sun_rasi_lord VARCHAR(50),
    sun_nakshatra VARCHAR(50),
    sun_nakshatra_lord VARCHAR(50),
    sun_pada INTEGER,
    sun_retrograde BOOLEAN DEFAULT FALSE,
    sun_degrees_in_rasi DECIMAL(10, 6),
    
    moon_longitude DECIMAL(10, 6),
    moon_rasi VARCHAR(50),
    moon_rasi_lord VARCHAR(50),
    moon_nakshatra VARCHAR(50),
    moon_nakshatra_lord VARCHAR(50),
    moon_pada INTEGER,
    moon_retrograde BOOLEAN DEFAULT FALSE,
    moon_degrees_in_rasi DECIMAL(10, 6),
    
    mars_longitude DECIMAL(10, 6),
    mars_rasi VARCHAR(50),
    mars_rasi_lord VARCHAR(50),
    mars_nakshatra VARCHAR(50),
    mars_nakshatra_lord VARCHAR(50),
    mars_pada INTEGER,
    mars_retrograde BOOLEAN DEFAULT FALSE,
    mars_degrees_in_rasi DECIMAL(10, 6),
    
    mercury_longitude DECIMAL(10, 6),
    mercury_rasi VARCHAR(50),
    mercury_rasi_lord VARCHAR(50),
    mercury_nakshatra VARCHAR(50),
    mercury_nakshatra_lord VARCHAR(50),
    mercury_pada INTEGER,
    mercury_retrograde BOOLEAN DEFAULT FALSE,
    mercury_degrees_in_rasi DECIMAL(10, 6),
    
    jupiter_longitude DECIMAL(10, 6),
    jupiter_rasi VARCHAR(50),
    jupiter_rasi_lord VARCHAR(50),
    jupiter_nakshatra VARCHAR(50),
    jupiter_nakshatra_lord VARCHAR(50),
    jupiter_pada INTEGER,
    jupiter_retrograde BOOLEAN DEFAULT FALSE,
    jupiter_degrees_in_rasi DECIMAL(10, 6),
    
    venus_longitude DECIMAL(10, 6),
    venus_rasi VARCHAR(50),
    venus_rasi_lord VARCHAR(50),
    venus_nakshatra VARCHAR(50),
    venus_nakshatra_lord VARCHAR(50),
    venus_pada INTEGER,
    venus_retrograde BOOLEAN DEFAULT FALSE,
    venus_degrees_in_rasi DECIMAL(10, 6),
    
    saturn_longitude DECIMAL(10, 6),
    saturn_rasi VARCHAR(50),
    saturn_rasi_lord VARCHAR(50),
    saturn_nakshatra VARCHAR(50),
    saturn_nakshatra_lord VARCHAR(50),
    saturn_pada INTEGER,
    saturn_retrograde BOOLEAN DEFAULT FALSE,
    saturn_degrees_in_rasi DECIMAL(10, 6),
    
    rahu_longitude DECIMAL(10, 6),
    rahu_rasi VARCHAR(50),
    rahu_rasi_lord VARCHAR(50),
    rahu_nakshatra VARCHAR(50),
    rahu_nakshatra_lord VARCHAR(50),
    rahu_pada INTEGER,
    rahu_retrograde BOOLEAN DEFAULT FALSE,
    rahu_degrees_in_rasi DECIMAL(10, 6),
    
    ketu_longitude DECIMAL(10, 6),
    ketu_rasi VARCHAR(50),
    ketu_rasi_lord VARCHAR(50),
    ketu_nakshatra VARCHAR(50),
    ketu_nakshatra_lord VARCHAR(50),
    ketu_pada INTEGER,
    ketu_retrograde BOOLEAN DEFAULT FALSE,
    ketu_degrees_in_rasi DECIMAL(10, 6),
    
    ascendant_longitude DECIMAL(10, 6),
    ascendant_rasi VARCHAR(50),
    ascendant_rasi_lord VARCHAR(50),
    ascendant_nakshatra VARCHAR(50),
    ascendant_nakshatra_lord VARCHAR(50),
    ascendant_pada INTEGER,
    ascendant_retrograde BOOLEAN DEFAULT FALSE,
    ascendant_degrees_in_rasi DECIMAL(10, 6)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_astrology_charts_primary_category ON astrology_charts(primary_category);
CREATE INDEX IF NOT EXISTS idx_astrology_charts_created_at ON astrology_charts(created_at);
CREATE INDEX IF NOT EXISTS idx_astrology_charts_researcher_id ON astrology_charts(researcher_id);

-- Enable Row Level Security (RLS)
ALTER TABLE astrology_charts ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations (for development)
CREATE POLICY "Allow all operations" ON astrology_charts
    FOR ALL USING (true);

COMMENT ON TABLE astrology_charts IS 'Global Astrology Research Database - Birth Charts with Planetary Positions'; 