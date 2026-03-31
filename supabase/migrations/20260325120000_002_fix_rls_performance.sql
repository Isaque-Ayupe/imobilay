-- ============================================================
-- Fix RLS Performance Bottleneck (auth.uid() execution)
-- Avoids O(N) evaluation of auth.uid() function by wrapping it in a subselect
-- ============================================================

DROP POLICY "user vê e edita próprio perfil" ON user_profiles;
CREATE POLICY "user vê e edita próprio perfil" ON user_profiles FOR ALL USING ((select auth.uid()) = id);

DROP POLICY "user vê e edita próprio perfil de investidor" ON investor_profiles;
CREATE POLICY "user vê e edita próprio perfil de investidor" ON investor_profiles FOR ALL USING ((select auth.uid()) = user_id);

DROP POLICY "user vê e edita próprias sessões" ON sessions;
CREATE POLICY "user vê e edita próprias sessões" ON sessions FOR ALL USING ((select auth.uid()) = user_id);

DROP POLICY "user vê próprias mensagens" ON messages;
CREATE POLICY "user vê próprias mensagens" ON messages FOR ALL USING (session_id IN (SELECT id FROM sessions WHERE user_id = (select auth.uid())));

DROP POLICY "user vê próprio feedback" ON feedback_records;
CREATE POLICY "user vê próprio feedback" ON feedback_records FOR ALL USING ((select auth.uid()) = user_id);

DROP POLICY "user vê próprios imóveis salvos" ON saved_properties;
CREATE POLICY "user vê próprios imóveis salvos" ON saved_properties FOR ALL USING ((select auth.uid()) = user_id);
