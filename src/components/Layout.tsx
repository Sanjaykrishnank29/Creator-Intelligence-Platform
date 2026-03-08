import React, { useState } from 'react';
import {
  LayoutDashboard, History, Brain, PenTool, Menu, X,
  LayoutGrid, ChevronLeft, ChevronRight, Sparkles,
  Zap, TrendingUp, Bell, Search, Settings, Command
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const menuItems = [
  { id: 'dashboard',      label: 'Dashboard',       icon: LayoutDashboard, badge: null },
  { id: 'creator-engine', label: 'Creator Engine',  icon: LayoutGrid,      badge: 'AI' },
  { id: 'generate',       label: 'AI Ideas',         icon: Sparkles,        badge: null },
  { id: 'intelligence',   label: 'Intelligence',     icon: Brain,           badge: null },
  { id: 'new-post',       label: 'New Post',         icon: PenTool,         badge: null },
  { id: 'history',        label: 'History',          icon: History,         badge: null },
];

export default function Layout({ children, activeTab, onTabChange }: LayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const activeItem = menuItems.find(m => m.id === activeTab);

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--bg-main)' }}>
      {/* Mobile overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/50 backdrop-blur-sm lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* ── SIDEBAR ── */}
      <aside
        style={{ background: 'var(--bg-sidebar)', borderRight: '1px solid var(--sidebar-border)' }}
        className={[
          'fixed inset-y-0 left-0 z-30 flex flex-col',
          'transform transition-all duration-300 ease-in-out lg:static lg:inset-0 sidebar-scroll overflow-y-auto',
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
          isCollapsed ? 'w-[64px]' : 'w-[220px]',
        ].join(' ')}
      >
        {/* Logo */}
        <div
          className={['flex items-center h-[56px] flex-shrink-0 px-4', isCollapsed ? 'justify-center' : 'gap-2.5'].join(' ')}
          style={{ borderBottom: '1px solid var(--sidebar-border)' }}
        >
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ background: 'linear-gradient(135deg,#6366f1,#8b5cf6)' }}
          >
            <Zap size={13} className="text-white" />
          </div>
          {!isCollapsed && (
            <div className="flex flex-col">
              <span className="text-white font-semibold text-[14px] tracking-[-0.02em] leading-tight">CreatorAI</span>
              <span className="text-[10px] font-medium tracking-wide" style={{ color: 'rgba(255,255,255,0.3)', fontFamily: "'JetBrains Mono', monospace" }}>BETA</span>
            </div>
          )}
          <button
            onClick={() => setIsSidebarOpen(false)}
            className="lg:hidden ml-auto p-1 rounded-md transition-colors"
            style={{ color: 'rgba(255,255,255,0.4)' }}
          >
            <X size={15} />
          </button>
        </div>

        {/* Nav items */}
        <nav className="flex-1 py-4 px-2 space-y-0.5">
          {!isCollapsed && (
            <p className="px-3 pt-0 pb-2 section-label" style={{ color: 'rgba(255,255,255,0.2)' }}>
              Navigation
            </p>
          )}
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => { onTabChange(item.id); setIsSidebarOpen(false); }}
                title={isCollapsed ? item.label : undefined}
                style={{
                  background: isActive ? 'rgba(255,255,255,0.08)' : 'transparent',
                  color: isActive ? '#FFFFFF' : 'rgba(255,255,255,0.52)',
                  borderRadius: '9px',
                  border: `1px solid ${isActive ? 'rgba(255,255,255,0.1)' : 'transparent'}`,
                }}
                className={[
                  'w-full flex items-center gap-3 py-2.5 transition-all duration-150 text-[13.5px] font-medium group',
                  isCollapsed ? 'justify-center px-0' : 'px-3',
                ].join(' ')}
                onMouseEnter={e => {
                  if (!isActive) {
                    (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.05)';
                    (e.currentTarget as HTMLButtonElement).style.color = 'rgba(255,255,255,0.8)';
                  }
                }}
                onMouseLeave={e => {
                  if (!isActive) {
                    (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
                    (e.currentTarget as HTMLButtonElement).style.color = 'rgba(255,255,255,0.52)';
                  }
                }}
              >
                <Icon size={15} className="flex-shrink-0" />
                {!isCollapsed && (
                  <>
                    <span className="flex-1 text-left">{item.label}</span>
                    {item.badge && (
                      <span
                        className="text-[9px] font-bold tracking-wider px-1.5 py-0.5 rounded"
                        style={{ background: 'rgba(99,102,241,0.25)', color: '#A5B4FC', fontFamily: "'JetBrains Mono', monospace" }}
                      >
                        {item.badge}
                      </span>
                    )}
                    {isActive && !item.badge && (
                      <span className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: '#6366f1' }} />
                    )}
                  </>
                )}
              </button>
            );
          })}
        </nav>

        {/* Bottom: status + user + collapse */}
        <div className="flex-shrink-0 pb-3 px-2 space-y-1" style={{ borderTop: '1px solid var(--sidebar-border)' }}>
          {/* Live API status */}
          {!isCollapsed && (
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg mx-0 mb-1" style={{ background: 'rgba(22,163,74,0.08)', border: '1px solid rgba(22,163,74,0.14)' }}>
              <span className="status-dot live" />
              <span className="text-[11px] font-medium" style={{ color: 'rgba(134,239,172,0.9)', fontFamily: "'JetBrains Mono', monospace" }}>AWS Connected</span>
            </div>
          )}

          {/* User row */}
          <div className={['flex items-center gap-3 py-2.5 px-3', isCollapsed ? 'justify-center' : ''].join(' ')}>
            <div
              className="w-7 h-7 rounded-lg flex-shrink-0 flex items-center justify-center text-[10px] font-bold text-white"
              style={{ background: 'linear-gradient(135deg, #f472b6, #a855f7)' }}
            >
              {isCollapsed ? 'T' : 'TWT'}
            </div>
            {!isCollapsed && (
              <div className="overflow-hidden flex-1">
                <p className="text-[12.5px] font-semibold leading-tight truncate" style={{ color: '#FFFFFF' }}>
                  Tech With Tim
                </p>
                <p className="text-[10.5px] leading-tight truncate" style={{ color: 'rgba(255,255,255,0.3)', fontFamily: "'JetBrains Mono', monospace" }}>
                  PRO PLAN
                </p>
              </div>
            )}
          </div>

          {/* Collapse toggle */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hidden lg:flex w-full items-center justify-center gap-2 py-2 rounded-lg transition-all text-xs font-medium"
            style={{ color: 'rgba(255,255,255,0.25)', background: 'rgba(255,255,255,0.02)' }}
            onMouseEnter={e => {
              (e.currentTarget as HTMLButtonElement).style.color = 'rgba(255,255,255,0.6)';
              (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.05)';
            }}
            onMouseLeave={e => {
              (e.currentTarget as HTMLButtonElement).style.color = 'rgba(255,255,255,0.25)';
              (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.02)';
            }}
          >
            {isCollapsed ? <ChevronRight size={13} /> : <><ChevronLeft size={13} /><span>Collapse</span></>}
          </button>
        </div>
      </aside>

      {/* ── MAIN CONTENT ── */}
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Mobile topbar */}
        <header className="flex-shrink-0 flex items-center justify-between h-[56px] px-4 lg:hidden" style={{ background: 'var(--bg-card)', borderBottom: '1px solid var(--border-card)' }}>
          <button onClick={() => setIsSidebarOpen(true)} className="p-2 -ml-2 rounded-lg transition-colors" style={{ color: 'var(--text-secondary)' }}>
            <Menu size={19} />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md flex items-center justify-center" style={{ background: 'linear-gradient(135deg,#6366f1,#8b5cf6)' }}>
              <Zap size={11} className="text-white" />
            </div>
            <span className="font-semibold text-[14px]" style={{ color: 'var(--text-primary)' }}>CreatorAI</span>
          </div>
          <div className="w-8" />
        </header>

        {/* Desktop topbar */}
        <header
          className="hidden lg:flex flex-shrink-0 items-center justify-between h-[56px] px-6"
          style={{ background: 'var(--bg-card)', borderBottom: '1px solid var(--border-card)' }}
        >
          {/* Left: breadcrumb page name */}
          <div className="flex items-center gap-2">
            <span className="text-[13px] font-medium" style={{ color: 'var(--text-secondary)' }}>CreatorAI</span>
            <span style={{ color: 'var(--text-muted)' }}>/</span>
            <span className="text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>
              {activeItem?.label || 'Dashboard'}
            </span>
          </div>

          {/* Right: actions */}
          <div className="flex items-center gap-1">
            {/* Keyboard shortcut hint */}
            <div className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg mr-2" style={{ background: 'var(--bg-tag)', border: '1px solid var(--border-card)' }}>
              <Command size={11} style={{ color: 'var(--text-muted)' }} />
              <span className="text-[11px] font-medium" style={{ color: 'var(--text-muted)', fontFamily: "'JetBrains Mono', monospace" }}>K</span>
            </div>
            <button className="btn btn-ghost" style={{ padding: '7px' }}>
              <Search size={15} style={{ color: 'var(--text-muted)' }} />
            </button>
            <button className="btn btn-ghost" style={{ padding: '7px' }}>
              <Bell size={15} style={{ color: 'var(--text-muted)' }} />
            </button>
            <button className="btn btn-ghost" style={{ padding: '7px' }}>
              <Settings size={15} style={{ color: 'var(--text-muted)' }} />
            </button>
            <div className="w-px h-5 mx-1" style={{ background: 'var(--border-card)' }} />
            {/* Mini avatar */}
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-bold text-white cursor-pointer"
              style={{ background: 'linear-gradient(135deg, #f472b6, #a855f7)' }}
            >
              T
            </div>
          </div>
        </header>

        {/* Page content */}
        <main
          className={[
            'flex-1 overflow-y-auto',
            activeTab === 'creator-engine' ? 'p-0' : 'p-6 lg:p-8',
          ].join(' ')}
          style={{ background: 'var(--bg-main)' }}
        >
          <div className={activeTab === 'creator-engine' ? 'h-full w-full' : 'max-w-7xl mx-auto'}>
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
