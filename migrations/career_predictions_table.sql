-- Career predictions storage for validation and research
CREATE TABLE IF NOT EXISTS career_predictions (
    id BIGSERIAL PRIMARY KEY,
    chart_id BIGINT NOT NULL REFERENCES astrology_charts(id) ON DELETE CASCADE,
    career_strength VARCHAR(20) NOT NULL,
    factors JSONB DEFAULT '[]',
    scores JSONB DEFAULT '{}',
    d10_snapshot JSONB,
    dasha_bukti_snapshot JSONB,
    bav_sav_snapshot JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(chart_id)
);

CREATE INDEX IF NOT EXISTS idx_career_predictions_chart_id ON career_predictions(chart_id);
