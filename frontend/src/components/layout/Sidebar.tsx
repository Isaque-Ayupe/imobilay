import { Plus, Bell, MessageSquare, Menu } from 'lucide-react';
import { MOCK_HISTORY } from '../../data/mock';

export function Sidebar() {
  const todaySessions = MOCK_HISTORY.filter(s => s.isToday);
  const yesterdaySessions = MOCK_HISTORY.filter(s => s.isYesterday);
  const olderSessions = MOCK_HISTORY.filter(s => !s.isToday && !s.isYesterday);

  return (
    <aside className="w-[220px] h-screen bg-surface border-r-[0.5px] border-border flex flex-col hidden md:flex shrink-0">
      {/* Header / Logo */}
      <div className="p-4 flex items-center justify-between">
        <h1 className="font-display text-lg tracking-wider font-semibold text-text-primary">
          IMOBILAY
        </h1>
        <button className="text-text-ghost hover:text-text-primary transition-colors">
          <Menu className="w-5 h-5" />
        </button>
      </div>

      {/* Ações Fixas */}
      <div className="px-3 pb-4 space-y-1 border-b-[0.5px] border-border">
        <button className="w-full flex items-center gap-2 px-3 py-2 rounded-md hover:bg-[var(--gold)] hover:bg-opacity-10 hover:text-[var(--gold)] transition-colors text-sm text-text-primary group">
          <Plus className="w-4 h-4 group-hover:text-[var(--gold)] text-text-muted" />
          <span>Nova análise</span>
        </button>
        <button className="w-full flex items-center gap-2 px-3 py-2 rounded-md hover:bg-surface-alt transition-colors text-sm text-text-primary group">
          <Bell className="w-4 h-4 text-text-muted group-hover:text-text-primary" />
          <span>Alertas</span>
        </button>
      </div>

      {/* Histórico Scrollable */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden p-3 space-y-4">
        {todaySessions.length > 0 && (
          <div>
            <h3 className="text-[10px] uppercase tracking-widest text-text-ghost font-medium mb-1 px-3">Hoje</h3>
            {todaySessions.map(sess => (
              <button key={sess.id} className="w-full flex items-start gap-2 px-3 py-2 rounded-md hover:bg-surface-alt text-left group">
                <MessageSquare className="w-3.5 h-3.5 mt-1 shrink-0 text-text-ghost group-hover:text-text-muted" />
                <span className="text-xs text-text-muted group-hover:text-text-primary truncate">{sess.title}</span>
              </button>
            ))}
          </div>
        )}

        {yesterdaySessions.length > 0 && (
          <div>
            <h3 className="text-[10px] uppercase tracking-widest text-text-ghost font-medium mb-1 px-3">Ontem</h3>
            {yesterdaySessions.map(sess => (
              <button key={sess.id} className="w-full flex items-start gap-2 px-3 py-2 rounded-md hover:bg-surface-alt text-left group">
                <MessageSquare className="w-3.5 h-3.5 mt-1 shrink-0 text-text-ghost group-hover:text-text-muted" />
                <span className="text-xs text-text-muted group-hover:text-text-primary truncate">{sess.title}</span>
              </button>
            ))}
          </div>
        )}

        {olderSessions.length > 0 && (
          <div>
            <h3 className="text-[10px] uppercase tracking-widest text-text-ghost font-medium mb-1 px-3">Esta semana</h3>
            {olderSessions.map(sess => (
              <button key={sess.id} className="w-full flex items-start gap-2 px-3 py-2 rounded-md hover:bg-surface-alt text-left group">
                <MessageSquare className="w-3.5 h-3.5 mt-1 shrink-0 text-text-ghost group-hover:text-text-muted" />
                <span className="text-xs text-text-muted group-hover:text-text-primary truncate">{sess.title}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* User Footer */}
      <div className="p-3 border-t-[0.5px] border-border">
        <button className="w-full flex items-center justify-between px-3 py-2 rounded-md hover:bg-surface-alt transition-colors">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-navy text-surface flex items-center justify-center text-[10px] font-medium">
              RC
            </div>
            <span className="text-sm font-medium text-text-primary">Rafael Costa</span>
          </div>
          <span className="text-text-ghost text-xs tracking-widest">···</span>
        </button>
      </div>
    </aside>
  );
}
