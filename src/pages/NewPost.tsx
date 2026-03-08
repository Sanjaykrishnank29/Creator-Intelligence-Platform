import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Zap, CheckCircle, AlertTriangle, Instagram, Linkedin, Twitter, Loader2, ChevronRight, Sparkles } from 'lucide-react';

interface Prediction {
  score: number;
  reasoning: string;
  improvements: string[];
}

interface Adaptation {
  instagram: string;
  linkedin: string;
  twitter: string;
}

function ScoreRing({ score }: { score: number }) {
  const r = 38;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const color = score >= 80 ? '#22c55e' : score >= 50 ? '#f59e0b' : '#ef4444';

  return (
    <div className="relative flex items-center justify-center w-24 h-24">
      <svg className="w-24 h-24 -rotate-90" viewBox="0 0 96 96">
        <circle cx="48" cy="48" r={r} fill="none" stroke="rgba(0,0,0,0.07)" strokeWidth="7" />
        <motion.circle
          cx="48" cy="48" r={r} fill="none" stroke={color} strokeWidth="7"
          strokeLinecap="round"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-xl font-bold stat-number" style={{ color: 'var(--text-primary)' }}>{score}</span>
        <span className="text-[10px] font-medium" style={{ color: 'var(--text-muted)' }}>/100</span>
      </div>
    </div>
  );
}

export default function NewPost() {
  const [idea, setIdea] = useState('');
  const [predicting, setPredicting] = useState(false);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [adapting, setAdapting] = useState(false);
  const [adaptation, setAdaptation] = useState<Adaptation | null>(null);

  const handlePredict = async () => {
    if (!idea.trim()) return;
    setPredicting(true);
    setPrediction(null);
    setAdaptation(null);
    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea })
      });
      const data = await res.json();
      res.ok ? setPrediction(data) : alert(data.error || 'Prediction failed');
    } catch { alert('Prediction failed'); }
    finally { setPredicting(false); }
  };

  const handleAdapt = async () => {
    if (!idea.trim()) return;
    setAdapting(true);
    try {
      const res = await fetch('/api/adapt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea })
      });
      const data = await res.json();
      res.ok ? setAdaptation(data) : alert(data.error || 'Adaptation failed');
    } catch { alert('Adaptation failed'); }
    finally { setAdapting(false); }
  };

  const scoreColor = prediction
    ? prediction.score >= 80 ? '#22c55e' : prediction.score >= 50 ? '#f59e0b' : '#ef4444'
    : '#22c55e';
  const scoreBg = prediction
    ? prediction.score >= 80 ? '#f0fdf4' : prediction.score >= 50 ? '#fffbeb' : '#fff1f2'
    : '#f0fdf4';

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="animate-fade-up">
        <p className="section-label mb-1">AI Scoring</p>
        <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>New Post</h1>
        <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>
          Test your content idea before you post it
        </p>
      </div>

      {/* Input card */}
      <div className="card p-6 space-y-4 animate-fade-up-delay-1">
        <label className="block text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}>
          Content Idea
        </label>
        <textarea
          rows={4}
          className="input resize-none"
          placeholder="e.g. A deep-dive tutorial on building AI agents with Python and LangChain…"
          value={idea}
          onChange={e => setIdea(e.target.value)}
        />
        <button
          onClick={handlePredict}
          disabled={predicting || !idea.trim()}
          className="btn btn-primary w-full justify-center py-2.5"
          style={{ background: '#18181b', borderRadius: '12px' }}
        >
          {predicting
            ? <><Loader2 size={15} className="animate-spin" />Analyzing…</>
            : <><Zap size={15} />Predict Performance<ChevronRight size={14} className="ml-auto" /></>}
        </button>
      </div>

      {/* Prediction result */}
      <AnimatePresence>
        {prediction && (
          <motion.div
            initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="card p-6 space-y-5"
          >
            {/* Score row */}
            <div className="flex items-center gap-5">
              <ScoreRing score={prediction.score} />
              <div>
                <p className="section-label mb-1">Engagement Score</p>
                <p className="text-2xl font-bold tracking-tight stat-number" style={{ color: scoreColor }}>
                  {prediction.score >= 80 ? 'Excellent' : prediction.score >= 50 ? 'Good' : 'Needs Work'}
                </p>
                <span className="inline-flex items-center gap-1 mt-1 px-2 py-0.5 rounded-full text-xs font-medium"
                  style={{ background: scoreBg, color: scoreColor }}>
                  {prediction.score}/100
                </span>
              </div>
            </div>

            <div className="divider" />

            {/* Reasoning */}
            <div className="p-4 rounded-xl" style={{ background: 'rgba(0,0,0,0.025)', border: '1px solid rgba(0,0,0,0.05)' }}>
              <p className="section-label mb-2">Why this score</p>
              <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{prediction.reasoning}</p>
            </div>

            {/* Improvements */}
            <div>
              <p className="section-label mb-3 flex items-center gap-1.5">
                <AlertTriangle size={12} style={{ color: '#f59e0b' }} />
                Suggested Improvements
              </p>
              <div className="space-y-2">
                {prediction.improvements.map((imp, i) => (
                  <motion.div key={i}
                    initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.07 }}
                    className="flex items-start gap-2.5 text-sm"
                    style={{ color: 'var(--text-secondary)' }}>
                    <CheckCircle size={14} style={{ color: '#22c55e', marginTop: 2, flexShrink: 0 }} />
                    {imp}
                  </motion.div>
                ))}
              </div>
            </div>

            <div className="divider" />

            <button
              onClick={handleAdapt}
              disabled={adapting}
              className="btn btn-secondary w-full justify-center py-2.5"
            >
              {adapting
                ? <><Loader2 size={14} className="animate-spin" />Adapting…</>
                : <><Sparkles size={14} />Adapt for All Platforms</>}
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Platform adaptations */}
      <AnimatePresence>
        {adaptation && (
          <motion.div
            initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            className="space-y-3"
          >
            <p className="section-label">Platform Adaptations</p>
            {[
              { key: 'instagram', label: 'Instagram', icon: Instagram, color: '#db2777', bg: '#fdf2f8', text: adaptation.instagram },
              { key: 'linkedin',  label: 'LinkedIn',  icon: Linkedin,  color: '#2563eb', bg: '#eff6ff', text: adaptation.linkedin },
              { key: 'twitter',   label: 'Twitter / X', icon: Twitter, color: '#0a0a0b', bg: '#f9fafb', text: adaptation.twitter },
            ].map((p, i) => {
              const Icon = p.icon;
              return (
                <motion.div key={p.key}
                  initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}
                  className="card p-5">
                  <div className="flex items-center gap-2.5 mb-3">
                    <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: p.bg }}>
                      <Icon size={14} style={{ color: p.color }} />
                    </div>
                    <p className="text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>{p.label}</p>
                  </div>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: 'var(--text-secondary)' }}>{p.text}</p>
                </motion.div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
