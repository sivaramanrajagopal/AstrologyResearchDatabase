-- Run this in Supabase SQL Editor so the app (anon key) can read/write data.
-- Without these, the app gets empty results or 403 even though SQL Editor shows data.

-- 1. Grant schema and table usage to anon
GRANT USAGE ON SCHEMA public TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.astrology_charts TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.career_predictions TO anon;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon;

-- 2. Enable RLS on tables (if not already)
ALTER TABLE public.astrology_charts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.career_predictions ENABLE ROW LEVEL SECURITY;

-- 3. Policies so anon can do everything (app uses anon key)
DROP POLICY IF EXISTS "anon_select_astrology_charts" ON public.astrology_charts;
DROP POLICY IF EXISTS "anon_insert_astrology_charts" ON public.astrology_charts;
DROP POLICY IF EXISTS "anon_update_astrology_charts" ON public.astrology_charts;
DROP POLICY IF EXISTS "anon_delete_astrology_charts" ON public.astrology_charts;

CREATE POLICY "anon_select_astrology_charts" ON public.astrology_charts FOR SELECT TO anon USING (true);
CREATE POLICY "anon_insert_astrology_charts" ON public.astrology_charts FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "anon_update_astrology_charts" ON public.astrology_charts FOR UPDATE TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_delete_astrology_charts" ON public.astrology_charts FOR DELETE TO anon USING (true);

DROP POLICY IF EXISTS "anon_select_career_predictions" ON public.career_predictions;
DROP POLICY IF EXISTS "anon_insert_career_predictions" ON public.career_predictions;
DROP POLICY IF EXISTS "anon_update_career_predictions" ON public.career_predictions;
DROP POLICY IF EXISTS "anon_delete_career_predictions" ON public.career_predictions;

CREATE POLICY "anon_select_career_predictions" ON public.career_predictions FOR SELECT TO anon USING (true);
CREATE POLICY "anon_insert_career_predictions" ON public.career_predictions FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "anon_update_career_predictions" ON public.career_predictions FOR UPDATE TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_delete_career_predictions" ON public.career_predictions FOR DELETE TO anon USING (true);
