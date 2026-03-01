-- Run in Supabase SQL Editor. Copy one block at a time.

-- All charts (basic)
SELECT id, name, gender, date_of_birth, time_of_birth, place_of_birth, timezone_name, primary_category, created_at
FROM astrology_charts
ORDER BY id
LIMIT 100;

-- Single chart by id (change 1 to your chart id)
SELECT * FROM astrology_charts WHERE id = 1;

-- Charts with key planetary data
SELECT id, name, date_of_birth, time_of_birth, place_of_birth, sun_rasi, moon_rasi, ascendant_rasi, moon_longitude
FROM astrology_charts
ORDER BY id
LIMIT 50;

-- Career predictions joined to charts
SELECT cp.chart_id, ac.name, cp.career_strength, cp.factors, cp.scores, cp.created_at
FROM career_predictions cp
JOIN astrology_charts ac ON ac.id = cp.chart_id
ORDER BY cp.created_at DESC
LIMIT 50;

-- Counts
SELECT (SELECT COUNT(*) FROM astrology_charts) AS total_charts,
       (SELECT COUNT(*) FROM career_predictions) AS total_career_predictions;

-- Charts by category
SELECT primary_category, COUNT(*) AS count
FROM astrology_charts
WHERE primary_category IS NOT NULL
GROUP BY primary_category
ORDER BY count DESC;

-- Recent charts (7 days)
SELECT id, name, date_of_birth, place_of_birth, created_at
FROM astrology_charts
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
