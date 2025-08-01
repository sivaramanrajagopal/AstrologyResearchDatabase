-- Safe Migration: Add Enhanced Columns to Existing Table
-- This script only adds missing columns without dropping existing data

-- Add House Positions (12 Houses) - Only if they don't exist
DO $$
BEGIN
    -- House 1
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_1_longitude') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_1_longitude DECIMAL(10, 6);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_1_rasi') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_1_rasi VARCHAR(50);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_1_degrees') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_1_degrees DECIMAL(10, 6);
    END IF;

    -- House 2
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_2_longitude') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_2_longitude DECIMAL(10, 6);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_2_rasi') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_2_rasi VARCHAR(50);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_2_degrees') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_2_degrees DECIMAL(10, 6);
    END IF;

    -- House 3
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_3_longitude') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_3_longitude DECIMAL(10, 6);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_3_rasi') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_3_rasi VARCHAR(50);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_3_degrees') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_3_degrees DECIMAL(10, 6);
    END IF;

    -- House 4
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_4_longitude') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_4_longitude DECIMAL(10, 6);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_4_rasi') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_4_rasi VARCHAR(50);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_4_degrees') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_4_degrees DECIMAL(10, 6);
    END IF;

    -- House 5
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_5_longitude') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_5_longitude DECIMAL(10, 6);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_5_rasi') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_5_rasi VARCHAR(50);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_5_degrees') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_5_degrees DECIMAL(10, 6);
    END IF;

    -- House 6
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_6_longitude') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_6_longitude DECIMAL(10, 6);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_6_rasi') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_6_rasi VARCHAR(50);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_6_degrees') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_6_degrees DECIMAL(10, 6);
    END IF;

    -- House 7
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_7_longitude') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_7_longitude DECIMAL(10, 6);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_7_rasi') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_7_rasi VARCHAR(50);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_7_degrees') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_7_degrees DECIMAL(10, 6);
    END IF;

    -- House 8
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_8_longitude') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_8_longitude DECIMAL(10, 6);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_8_rasi') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_8_rasi VARCHAR(50);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_8_degrees') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_8_degrees DECIMAL(10, 6);
    END IF;

    -- House 9
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_9_longitude') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_9_longitude DECIMAL(10, 6);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_9_rasi') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_9_rasi VARCHAR(50);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_9_degrees') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_9_degrees DECIMAL(10, 6);
    END IF;

    -- House 10
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_10_longitude') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_10_longitude DECIMAL(10, 6);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_10_rasi') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_10_rasi VARCHAR(50);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_10_degrees') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_10_degrees DECIMAL(10, 6);
    END IF;

    -- House 11
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_11_longitude') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_11_longitude DECIMAL(10, 6);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_11_rasi') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_11_rasi VARCHAR(50);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_11_degrees') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_11_degrees DECIMAL(10, 6);
    END IF;

    -- House 12
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_12_longitude') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_12_longitude DECIMAL(10, 6);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_12_rasi') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_12_rasi VARCHAR(50);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'house_12_degrees') THEN
        ALTER TABLE astrology_charts ADD COLUMN house_12_degrees DECIMAL(10, 6);
    END IF;

    -- Enhanced Features (JSON) - Only if they don't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'yogas') THEN
        ALTER TABLE astrology_charts ADD COLUMN yogas JSONB;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'shadbala') THEN
        ALTER TABLE astrology_charts ADD COLUMN shadbala JSONB;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'aspects') THEN
        ALTER TABLE astrology_charts ADD COLUMN aspects JSONB;
    END IF;

    -- Add updated_at column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'astrology_charts' AND column_name = 'updated_at') THEN
        ALTER TABLE astrology_charts ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;

END $$;

-- Create indexes for better performance (only if they don't exist)
DO $$
BEGIN
    -- Index for date_of_birth
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE tablename = 'astrology_charts' AND indexname = 'idx_astrology_charts_date_of_birth') THEN
        CREATE INDEX idx_astrology_charts_date_of_birth ON astrology_charts(date_of_birth);
    END IF;

    -- Index for primary_category
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE tablename = 'astrology_charts' AND indexname = 'idx_astrology_charts_primary_category') THEN
        CREATE INDEX idx_astrology_charts_primary_category ON astrology_charts(primary_category);
    END IF;

    -- Index for place_of_birth
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE tablename = 'astrology_charts' AND indexname = 'idx_astrology_charts_place_of_birth') THEN
        CREATE INDEX idx_astrology_charts_place_of_birth ON astrology_charts(place_of_birth);
    END IF;

    -- Index for created_at
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE tablename = 'astrology_charts' AND indexname = 'idx_astrology_charts_created_at') THEN
        CREATE INDEX idx_astrology_charts_created_at ON astrology_charts(created_at);
    END IF;

    -- Index for JSON fields
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE tablename = 'astrology_charts' AND indexname = 'idx_astrology_charts_yogas') THEN
        CREATE INDEX idx_astrology_charts_yogas ON astrology_charts USING GIN (yogas);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE tablename = 'astrology_charts' AND indexname = 'idx_astrology_charts_shadbala') THEN
        CREATE INDEX idx_astrology_charts_shadbala ON astrology_charts USING GIN (shadbala);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE tablename = 'astrology_charts' AND indexname = 'idx_astrology_charts_aspects') THEN
        CREATE INDEX idx_astrology_charts_aspects ON astrology_charts USING GIN (aspects);
    END IF;

END $$;

-- Create function to update updated_at timestamp (only if it doesn't exist)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at (only if it doesn't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_astrology_charts_updated_at') THEN
        CREATE TRIGGER update_astrology_charts_updated_at 
            BEFORE UPDATE ON astrology_charts 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- Grant permissions (adjust as needed for your setup)
GRANT ALL PRIVILEGES ON TABLE astrology_charts TO authenticated;
GRANT ALL PRIVILEGES ON SEQUENCE astrology_charts_id_seq TO authenticated;

-- Display success message
SELECT 'Migration completed successfully! Enhanced columns added to existing table.' as status; 