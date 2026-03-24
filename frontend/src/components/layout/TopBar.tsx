import { Menu } from 'lucide-react';

export function TopBar() {
  return (
    <header className="h-[60px] w-full border-b-[0.5px] border-border bg-surface/80 backdrop-blur-md flex items-center justify-between px-4 sticky top-0 z-10">
      <div className="flex items-center gap-3">
        {/* Hambúrguer para Mobile (visível apenas em MD para baixo) */}
        <button className="md:hidden text-text-ghost hover:text-text-primary">
          <Menu className="w-5 h-5" />
        </button>
        <div className="flex flex-col">
          <h2 className="text-sm font-medium text-text-primary">Análise Imobiliária</h2>
          <span className="text-[10px] text-text-ghost tracking-widest uppercase">Consultor Digital</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {/* Status Pill */}
        <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-green-light/50 border-[0.5px] border-green/20">
          <div className="w-1.5 h-1.5 rounded-full bg-green animate-pulse"></div>
          <span className="text-[10px] text-green font-medium tracking-wide uppercase">Online</span>
        </div>
      </div>
    </header>
  );
}
