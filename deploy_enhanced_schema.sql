-- Enhanced Supabase Schema for Vedic Astrology Database
-- Copy and paste this entire script into Supabase SQL Editor

-- Drop existing table if it exists
DROP TABLE IF EXISTS astrology_charts;

-- Create enhanced astrology_charts table
CREATE TABLE astrology_charts (
    id SERIAL PRIMARY KEY,
    
    -- Basic Information
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    date_of_birth DATE NOT NULL,
    time_of_birth TIME NOT NULL,
    place_of_birth VARCHAR(255) NOT NULL,
    
    -- Location and Timezone
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    timezone_name VARCHAR(100) NOT NULL,
    
    -- Research Categories
    primary_category VARCHAR(100),
    sub_category VARCHAR(100),
    specific_condition VARCHAR(100),
    description TEXT,
    outcome VARCHAR(50),
    severity VARCHAR(50),
    timing VARCHAR(50),
    
    -- Research Metadata
    researcher_id VARCHAR(100),
    consent_given BOOLEAN DEFAULT false,
    anonymize BOOLEAN DEFAULT false,
    
    -- Travel Information
    travel_country VARCHAR(100),
    travel_city VARCHAR(100),
    travel_purpose VARCHAR(100),
    travel_outcome VARCHAR(100),
    
    -- Planetary Positions (Individual Columns)
    sun_longitude DECIMAL(10, 6),
    sun_rasi VARCHAR(50),
    sun_rasi_lord VARCHAR(50),
    sun_nakshatra VARCHAR(50),
    sun_nakshatra_lord VARCHAR(50),
    sun_pada INTEGER,
    sun_degrees_in_rasi DECIMAL(10, 6),
    sun_retrograde BOOLEAN,
    
    moon_longitude DECIMAL(10, 6),
    moon_rasi VARCHAR(50),
    moon_rasi_lord VARCHAR(50),
    moon_nakshatra VARCHAR(50),
    moon_nakshatra_lord VARCHAR(50),
    moon_pada INTEGER,
    moon_degrees_in_rasi DECIMAL(10, 6),
    moon_retrograde BOOLEAN,
    
    mars_longitude DECIMAL(10, 6),
    mars_rasi VARCHAR(50),
    mars_rasi_lord VARCHAR(50),
    mars_nakshatra VARCHAR(50),
    mars_nakshatra_lord VARCHAR(50),
    mars_pada INTEGER,
    mars_degrees_in_rasi DECIMAL(10, 6),
    mars_retrograde BOOLEAN,
    
    mercury_longitude DECIMAL(10, 6),
    mercury_rasi VARCHAR(50),
    mercury_rasi_lord VARCHAR(50),
    mercury_nakshatra VARCHAR(50),
    mercury_nakshatra_lord VARCHAR(50),
    mercury_pada INTEGER,
    mercury_degrees_in_rasi DECIMAL(10, 6),
    mercury_retrograde BOOLEAN,
    
    jupiter_longitude DECIMAL(10, 6),
    jupiter_rasi VARCHAR(50),
    jupiter_rasi_lord VARCHAR(50),
    jupiter_nakshatra VARCHAR(50),
    jupiter_nakshatra_lord VARCHAR(50),
    jupiter_pada INTEGER,
    jupiter_degrees_in_rasi DECIMAL(10, 6),
    jupiter_retrograde BOOLEAN,
    
    venus_longitude DECIMAL(10, 6),
    venus_rasi VARCHAR(50),
    venus_rasi_lord VARCHAR(50),
    venus_nakshatra VARCHAR(50),
    venus_nakshatra_lord VARCHAR(50),
    venus_pada INTEGER,
    venus_degrees_in_rasi DECIMAL(10, 6),
    venus_retrograde BOOLEAN,
    
    saturn_longitude DECIMAL(10, 6),
    saturn_rasi VARCHAR(50),
    saturn_rasi_lord VARCHAR(50),
    saturn_nakshatra VARCHAR(50),
    saturn_nakshatra_lord VARCHAR(50),
    saturn_pada INTEGER,
    saturn_degrees_in_rasi DECIMAL(10, 6),
    saturn_retrograde BOOLEAN,
    
    rahu_longitude DECIMAL(10, 6),
    rahu_rasi VARCHAR(50),
    rahu_rasi_lord VARCHAR(50),
    rahu_nakshatra VARCHAR(50),
    rahu_nakshatra_lord VARCHAR(50),
    rahu_pada INTEGER,
    rahu_degrees_in_rasi DECIMAL(10, 6),
    rahu_retrograde BOOLEAN,
    
    ketu_longitude DECIMAL(10, 6),
    ketu_rasi VARCHAR(50),
    ketu_rasi_lord VARCHAR(50),
    ketu_nakshatra VARCHAR(50),
    ketu_nakshatra_lord VARCHAR(50),
    ketu_pada INTEGER,
    ketu_degrees_in_rasi DECIMAL(10, 6),
    ketu_retrograde BOOLEAN,
    
    ascendant_longitude DECIMAL(10, 6),
    ascendant_rasi VARCHAR(50),
    ascendant_rasi_lord VARCHAR(50),
    ascendant_nakshatra VARCHAR(50),
    ascendant_nakshatra_lord VARCHAR(50),
    ascendant_pada INTEGER,
    ascendant_degrees_in_rasi DECIMAL(10, 6),
    ascendant_retrograde BOOLEAN,
    
    -- House Positions (12 Houses)
    house_1_longitude DECIMAL(10, 6),
    house_1_rasi VARCHAR(50),
    house_1_degrees DECIMAL(10, 6),
    
    house_2_longitude DECIMAL(10, 6),
    house_2_rasi VARCHAR(50),
    house_2_degrees DECIMAL(10, 6),
    
    house_3_longitude DECIMAL(10, 6),
    house_3_rasi VARCHAR(50),
    house_3_degrees DECIMAL(10, 6),
    
    house_4_longitude DECIMAL(10, 6),
    house_4_rasi VARCHAR(50),
    house_4_degrees DECIMAL(10, 6),
    
    house_5_longitude DECIMAL(10, 6),
    house_5_rasi VARCHAR(50),
    house_5_degrees DECIMAL(10, 6),
    
    house_6_longitude DECIMAL(10, 6),
    house_6_rasi VARCHAR(50),
    house_6_degrees DECIMAL(10, 6),
    
    house_7_longitude DECIMAL(10, 6),
    house_7_rasi VARCHAR(50),
    house_7_degrees DECIMAL(10, 6),
    
    house_8_longitude DECIMAL(10, 6),
    house_8_rasi VARCHAR(50),
    house_8_degrees DECIMAL(10, 6),
    
    house_9_longitude DECIMAL(10, 6),
    house_9_rasi VARCHAR(50),
    house_9_degrees DECIMAL(10, 6),
    
    house_10_longitude DECIMAL(10, 6),
    house_10_rasi VARCHAR(50),
    house_10_degrees DECIMAL(10, 6),
    
    house_11_longitude DECIMAL(10, 6),
    house_11_rasi VARCHAR(50),
    house_11_degrees DECIMAL(10, 6),
    
    house_12_longitude DECIMAL(10, 6),
    house_12_rasi VARCHAR(50),
    house_12_degrees DECIMAL(10, 6),
    
    -- Enhanced Features (JSON)
    yogas JSONB,  -- Store yogas as JSON
    shadbala JSONB,  -- Store Shadbala calculations as JSON
    aspects JSONB,  -- Store planetary aspects as JSON
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_astrology_charts_date_of_birth ON astrology_charts(date_of_birth);
CREATE INDEX idx_astrology_charts_primary_category ON astrology_charts(primary_category);
CREATE INDEX idx_astrology_charts_place_of_birth ON astrology_charts(place_of_birth);
CREATE INDEX idx_astrology_charts_created_at ON astrology_charts(created_at);

-- Create index for JSON fields
CREATE INDEX idx_astrology_charts_yogas ON astrology_charts USING GIN (yogas);
CREATE INDEX idx_astrology_charts_shadbala ON astrology_charts USING GIN (shadbala);
CREATE INDEX idx_astrology_charts_aspects ON astrology_charts USING GIN (aspects);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_astrology_charts_updated_at 
    BEFORE UPDATE ON astrology_charts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust as needed for your setup)
GRANT ALL PRIVILEGES ON TABLE astrology_charts TO authenticated;
GRANT ALL PRIVILEGES ON SEQUENCE astrology_charts_id_seq TO authenticated; 