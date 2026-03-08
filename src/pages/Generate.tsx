import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Sparkles, Youtube, Instagram, MessageSquare, Loader2, ChevronRight, Hash, Zap, Twitter } from 'lucide-react';
import { apiUrl } from '../api';

const PLATFORMS = [
  { id: 'YouTube',   icon: Youtube,        color: '#DC2626', bg: '#FEF2F2', label: 'YouTube' },
  { id: 'Instagram', icon: Instagram,      color: '#DB2777', bg: '#FDF2F8', label: 'Instagram' },
  { id: 'TikTok',   icon: MessageSquare,  color: '#111113', bg: '#F3F4F6', label: 'TikTok' },
  { id: 'LinkedIn', icon: MessageSquare,  color: '#2563EB', bg: '#EFF6FF', label: 'LinkedIn' },
  { id: 'Twitter',  icon: Twitter,        color: '#0284C7', bg: '#F0F9FF', label: 'Twitter / X' },
];

const QUICK_TOPICS = ['Python AI Tutorial', 'Machine Learning in 2025', 'Build a SaaS MVP', 'Career in Tech', 'Open Source Projects'];

export default function Generate() {
  const [topic, setTopic] = useState('');
  const [platform, setPlatform] = useState('YouTube');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ideas, setIdeas] = useState<{ title: string; reason: string }[]>([]);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setError(null);
    setIdeas([]);
    try {
      const res = await fetch(apiUrl('/api/generate'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, platform, creator_id: 'techwithtim' }),
      });
      const data = await res.json();
      const payload = (data.statusCode && data.body) ? JSON.parse(data.body) : data;
      if (payload.ideas) {
        setIdeas(payload.ideas.map((idea: any) => ({
          title: idea.title,
          reason: idea.explanation || idea.reason || idea.performance_reasoning || '',
        })));
      } else {
        setError(payload.error || 'Failed to generate ideas.');
      }
    } catch {
      setError('Connection error. Check your API gateway.');
    } finally {
      setLoading(false);
    }
  };

  const currentPlatform = PLATFORMS.find(p => p.id === platform)!;

  return (
    <div className="max-w-2xl mx-auto space-y-7">
      {/* Header */}
      <div className="animate-fade-up space-y-1">
        <p className="page-eyebrow"><Sparkles size={12} className="inline" /> AWS Bedrock</p>
        <h1 className="page-title">AI Idea Generator</h1>
        <p className="page-sub">Get 5 high-performing content ideas tailored to your niche and platform.</p>
      </div>

      {/* Input panel */}
      <div className="section-panel animate-fade-up-delay-1">
        <div className="section-panel-header">
          <div className="flex items-center gap-3">
            <div className="icon-box-sm" style={{ background: '#EEF2FF' }}>
              <Zap size={14} style={{ color: '#4F46E5' }} />
            </div>
            <p className="font-semibold text-[14px]" style={{ color: 'var(--text-primary)' }}>Generate Ideas</p>
          </div>
          <span className="badge badge-indigo badge-mono">Nova Lite</span>
        </div>

        <div className="p-6 space-y-5">
          {/* Platform selector */}
          <div className="space-y-2">
            <label className="section-label">Platform</label>
            <div className="flex flex-wrap gap-2 mt-2">
              {PLATFORMS.map(p => {
                const Icon = p.icon;
                const isSelected = platform === p.id;
                return (
                  <button
                    key={p.id}
                    onClick={() => setPlatform(p.id)}
                    className="flex items-center gap-2 px-3 py-2 rounded-xl text-[12.5px] font-medium transition-all"
                    style={{
                      background: isSelected ? p.bg : 'var(--bg-main)',
                      color: isSelected ? p.color : 'var(--text-secondary)',
                      border: isSelected ? `1.5px solid ${p.color}30` : '1.5px solid var(--border-card)',
                      transform: isSelected ? 'scale(1.02)' : 'scale(1)',
                    }}
                  >
                    <Icon size={13} />
                    {p.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Topic input */}
          <div className="space-y-2">
            <label className="section-label">Topic or Niche</label>
            <input
              className="input"
              placeholder="e.g. Python AI Tutorial, Machine Learning trends..."
              value={topic}
              onChange={e => setTopic(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleGenerate()}
            />
            {/* Quick suggestions */}
            <div className="flex flex-wrap gap-1.5 mt-2">
              {QUICK_TOPICS.map(t => (
                <button
                  key={t}
                  onClick={() => setTopic(t)}
                  className="flex items-center gap-1 text-[11.5px] px-2.5 py-1 rounded-full transition-colors"
                  style={{ background: 'var(--bg-tag)', color: 'var(--text-secondary)', border: '1px solid var(--border-card)' }}
                  onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-primary)'; }}
                  onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-secondary)'; }}
                >
                  <Hash size={9} /> {t}
                </button>
              ))}
            </div>
          </div>

          {/* Generate button */}
          <button
            onClick={handleGenerate}
            disabled={loading || !topic.trim()}
            className="btn btn-primary btn-lg w-full justify-center gap-3"
          >
            {loading ? (
              <><Loader2 size={16} className="animate-spin" /> Generating Ideas...</>
            ) : (
              <><Sparkles size={16} /> Generate 5 Ideas</>
            )}
          </button>

          {error && (
            <div className="flex items-start gap-3 p-3 rounded-xl" style={{ background: '#FEF2F2', border: '1px solid #FECACA' }}>
              <span style={{ color: '#DC2626', fontSize: 13 }}>⚠ {error}</span>
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      <AnimatePresence>
        {ideas.length > 0 && (
          <div className="space-y-3 animate-fade-up">
            <div className="flex items-center justify-between">
              <p className="section-label">Generated Ideas — {currentPlatform.label}</p>
              <span className="badge badge-green badge-mono">{ideas.length} IDEAS</span>
            </div>
            {ideas.map((idea, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.07, duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
                className="section-panel hover:shadow-md transition-shadow cursor-pointer group"
              >
                <div className="p-5">
                  <div className="flex items-start gap-4">
                    {/* Number badge */}
                    <div
                      className="w-7 h-7 rounded-lg flex items-center justify-center text-[12px] font-bold flex-shrink-0 mt-0.5"
                      style={{ background: currentPlatform.bg, color: currentPlatform.color }}
                    >
                      {i + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-[14px] leading-snug group-hover:text-indigo-600 transition-colors" style={{ color: 'var(--text-primary)' }}>
                        {idea.title}
                      </h3>
                      {idea.reason && (
                        <p className="text-[13px] leading-relaxed mt-2" style={{ color: 'var(--text-secondary)' }}>
                          {idea.reason}
                        </p>
                      )}
                    </div>
                    <ChevronRight size={15} style={{ color: 'var(--text-muted)', flexShrink: 0 }} className="mt-1 group-hover:text-indigo-500 transition-colors" />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
