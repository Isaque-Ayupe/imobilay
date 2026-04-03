-- ============================================================
-- IMOBILAY — Migration 002: Optimize RLS
-- ============================================================

-- Drop old policies
DROP POLICY "user vê e edita próprio perfil" ON user_profiles;
DROP POLICY "user vê e edita próprio perfil de investidor" ON investor_profiles;
DROP POLICY "user vê e edita próprias sessões" ON sessions;
DROP POLICY "user vê próprias mensagens" ON messages;
DROP POLICY "user vê próprio feedback" ON feedback_records;
DROP POLICY "user vê próprios imóveis salvos" ON saved_properties;

-- Create optimized policies
CREATE POLICY "user vê e edita próprio perfil"
    ON user_profiles FOR ALL
    USING ((select auth.uid()) = id);

CREATE POLICY "user vê e edita próprio perfil de investidor"
    ON investor_profiles FOR ALL
    USING ((select auth.uid()) = user_id);

CREATE POLICY "user vê e edita próprias sessões"
    ON sessions FOR ALL
    USING ((select auth.uid()) = user_id);

CREATE POLICY "user vê próprias mensagens"
    ON messages FOR ALL
    USING (
        session_id IN (
            SELECT id FROM sessions WHERE user_id = (select auth.uid())
        )
    );

CREATE POLICY "user vê próprio feedback"
    ON feedback_records FOR ALL
    USING ((select auth.uid()) = user_id);

CREATE POLICY "user vê próprios imóveis salvos"
    ON saved_properties FOR ALL
    USING ((select auth.uid()) = user_id);
