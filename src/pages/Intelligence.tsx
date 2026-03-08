import React, { useEffect, useState } from 'react';
import { Brain, TrendingUp, Lightbulb, Youtube, Users, Eye, AlertCircle, Zap, BarChart3 } from 'lucide-react';
import { motion } from 'motion/react';
import { apiUrl } from '../api';

export default function Intelligence() {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(apiUrl('/api/profile'))
      .then(res => res.json())
      .then(data => {
        const profileData = (data.statusCode && data.body) ? JSON.parse(data.body) : data;
        setProfile(profileData);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="space-y-2">
          <div className="skeleton h-3 w-24 rounded" />
          <div className="skeleton h-8 w-52 rounded-lg" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => <div key={i} className="metric-card skeleton h-24 rounded-xl" />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(2)].map((_, i) => <div key={i} className="h-48 skeleton rounded-xl" />)}
        </div>
      </div>
    );
  }

  if (!profile || Object.keys(profile).length === 0 || profile.error) {
    return (
      <div className="space-y-6">
        <div>
          <p className="page-eyebrow mb-1"><Brain size={12} /> Creator Profile</p>
          <h1 className="page-title">Creator Intelligence</h1>
        </div>
        <div className="section-panel">
          <div className="flex flex-col items-center py-20 text-center">
            <div className="icon-box mb-4" style={{ background: 'var(--bg-tag)', width: 56, height: 56, borderRadius: 16 }}>
              <Brain size={24} style={{ color: 'var(--text-muted)' }} />
            </div>
            <h3 className="text-[16px] font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>No Intelligence Data Yet</h3>
            <p className="text-[13.5px] max-w-sm" style={{ color: 'var(--text-secondary)' }}>
              Sync your video history and run an analysis to generate your Creator Intelligence profile.
            </p>
            <button className="btn btn-primary mt-5">Go to History</button>
          </div>
        </div>
      </div>
    );
  }

  const topTopics: string[] = Array.isArray(profile.top_topics) ? profile.top_topics :
    (typeof profile.top_topics === 'string' ? JSON.parse(profile.top_topics) : []);
  const patterns: string[] = Array.isArray(profile.performance_patterns) ? profile.performance_patterns :
    (typeof profile.performance_patterns === 'string' ? JSON.parse(profile.performance_patterns) : []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-up space-y-1">
        <p className="page-eyebrow">
          <Brain size={12} className="inline" /> AI-Powered Profile
        </p>
        <h1 className="page-title">Creator Intelligence</h1>
        <p className="page-sub">Your AI-generated insight profile, built from real performance data.</p>
      </div>

      {/* Channel stats row */}
      {profile.name && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-fade-up-delay-1">
          <ChannelCard icon={<Youtube size={18} />} iconBg="#FEF2F2" iconColor="#DC2626" label="Channel" value={profile.name} />
          <ChannelCard icon={<Users size={18} />} iconBg="#F0FDF4" iconColor="#16A34A" label="Subscribers" value={(profile.subscriber_count || 0).toLocaleString()} />
          <ChannelCard icon={<Eye size={18} />} iconBg="#EFF6FF" iconColor="#2563EB" label="Avg Views / Video" value={(profile.average_views || 0).toLocaleString()} />
        </div>
      )}

      {/* Three-column insight grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-up-delay-2">
        {/* Niche & Style — spans 2 cols */}
        <motion.div
          initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
          className="section-panel lg:col-span-2"
        >
          <div className="section-panel-header">
            <div className="flex items-center gap-3">
              <div className="icon-box-sm" style={{ background: '#EEF2FF' }}>
                <Brain size={14} style={{ color: '#4F46E5' }} />
              </div>
              <div>
                <p className="font-semibold text-[14px]" style={{ color: 'var(--text-primary)' }}>Your Focus Niche & Style</p>
                <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>AI-analyzed content pattern</p>
              </div>
            </div>
            <span className="badge badge-indigo badge-mono">PROFILE</span>
          </div>
          <div className="p-6">
            <p className="text-[14.5px] leading-relaxed" style={{ color: 'var(--text-primary)', lineHeight: '1.75' }}>
              {profile.niche || profile.style_description || 'Specializing in tech content and software engineering tutorials.'}
            </p>
            {profile.platform && (
              <div className="flex items-center gap-2 mt-4">
                <span className="badge badge-neutral">Platform: {profile.platform}</span>
                {profile.subscriber_count > 1_000_000 && <span className="badge badge-green">1M+ Creator</span>}
              </div>
            )}
          </div>
        </motion.div>

        {/* Top Topics */}
        <motion.div
          initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.1 }}
          className="section-panel"
        >
          <div className="section-panel-header">
            <div className="flex items-center gap-3">
              <div className="icon-box-sm" style={{ background: '#F0FDF4' }}>
                <TrendingUp size={14} style={{ color: '#16A34A' }} />
              </div>
              <p className="font-semibold text-[14px]" style={{ color: 'var(--text-primary)' }}>Top Topics</p>
            </div>
          </div>
          <div className="p-4">
            {topTopics.length > 0 ? (
              <ul className="space-y-2">
                {topTopics.map((topic, i) => (
                  <li key={i} className="flex items-center justify-between px-3 py-2.5 rounded-xl" style={{ background: 'var(--bg-main)', border: '1px solid var(--border-card)' }}>
                    <span className="text-[13px] font-medium" style={{ color: 'var(--text-primary)' }}>{topic}</span>
                    <span className="badge badge-mono badge-neutral">#{i + 1}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-[13px] italic py-6 text-center" style={{ color: 'var(--text-muted)' }}>
                No topics analyzed yet.
              </p>
            )}
          </div>
        </motion.div>
      </div>

      {/* Performance Patterns */}
      {patterns.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.2 }}
          className="section-panel animate-fade-up-delay-3"
        >
          <div className="section-panel-header">
            <div className="flex items-center gap-3">
              <div className="icon-box-sm" style={{ background: '#FFFBEB' }}>
                <Lightbulb size={14} style={{ color: '#D97706' }} />
              </div>
              <div>
                <p className="font-semibold text-[14px]" style={{ color: 'var(--text-primary)' }}>Performance Patterns</p>
                <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>AI-detected behavioral insights</p>
              </div>
            </div>
            <span className="badge badge-amber badge-mono">{patterns.length} INSIGHTS</span>
          </div>
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-3">
            {patterns.map((pattern, i) => (
              <div
                key={i}
                className="flex items-start gap-3 p-4 rounded-xl"
                style={{ background: 'var(--bg-main)', border: '1px solid var(--border-card)' }}
              >
                <AlertCircle size={14} style={{ color: '#D97706', marginTop: 2, flexShrink: 0 }} />
                <p className="text-[13px] leading-relaxed" style={{ color: 'var(--text-primary)' }}>{pattern}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}

function ChannelCard({ icon, iconBg, iconColor, label, value }: any) {
  return (
    <div className="metric-card flex items-center gap-4">
      <div className="icon-box flex-shrink-0" style={{ background: iconBg }}>
        <span style={{ color: iconColor }}>{icon}</span>
      </div>
      <div>
        <p className="metric-label">{label}</p>
        <p className="text-[18px] font-bold mt-0.5 stat-number" style={{ color: 'var(--text-primary)', letterSpacing: '-0.03em' }}>{value}</p>
      </div>
    </div>
  );
}
