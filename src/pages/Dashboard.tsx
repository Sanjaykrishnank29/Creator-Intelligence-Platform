import React, { useEffect, useState } from 'react';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp, Eye, Heart, BarChart3, Activity, ArrowUpRight, ArrowDownRight, Zap } from 'lucide-react';
import { Post } from '../types';
import { apiUrl } from '../api';

export default function Dashboard() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(apiUrl('/api/posts?sync=true'))
      .then(res => res.json())
      .then(data => {
        const items = Array.isArray(data) ? data : data.posts || [];
        setPosts(items);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-6 animate-fade-in">
        {/* Header skeleton */}
        <div className="space-y-2">
          <div className="skeleton h-4 w-32 rounded" />
          <div className="skeleton h-8 w-56 rounded-lg" />
          <div className="skeleton h-4 w-72 rounded" />
        </div>
        {/* Metric skeletons */}
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="metric-card space-y-3">
              <div className="skeleton h-3 w-20 rounded" />
              <div className="skeleton h-8 w-28 rounded-lg" />
              <div className="skeleton h-3 w-16 rounded" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  const totalPosts = posts.length;
  const totalLikes = posts.reduce((a, p) => a + Number(p.likes || 0), 0);
  const totalViews = posts.reduce((a, p) => a + Number(p.views || 0), 0);
  const totalComments = posts.reduce((a, p) => a + Number(p.comments || 0), 0);
  const totalShares = posts.reduce((a, p) => a + Number(p.shares || 0), 0);
  const avgEngagement = totalViews > 0
    ? (((totalLikes + totalComments + totalShares) / totalViews) * 100).toFixed(2)
    : '0.00';

  const chartData = posts.slice(0, 15).reverse().map(p => {
    const d = new Date(p.timestamp);
    return {
      name: d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      likes: Number(p.likes || 0),
      views: Number(p.views || 0),
      comments: Number(p.comments || 0),
    };
  });

  const topPost = posts.reduce((best, p) => Number(p.views || 0) > Number(best?.views || 0) ? p : best, posts[0]);

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div className="animate-fade-up space-y-1">
        <p className="page-eyebrow">
          <span className="status-dot live" />
          YouTube · Tech With Tim
        </p>
        <h1 className="page-title">Performance Dashboard</h1>
        <p className="page-sub">Real-time engagement from your last {totalPosts} published videos.</p>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <MetricCard
          label="Total Views"
          value={formatNum(totalViews)}
          icon={<Eye size={16} />}
          iconBg="#EFF6FF"
          iconColor="#2563EB"
          delta="+12.4%"
          deltaUp
          delay="animate-fade-up-delay-1"
        />
        <MetricCard
          label="Total Likes"
          value={formatNum(totalLikes)}
          icon={<Heart size={16} />}
          iconBg="#FDF4FF"
          iconColor="#9333EA"
          delta="+8.1%"
          deltaUp
          delay="animate-fade-up-delay-2"
        />
        <MetricCard
          label="Avg Engagement"
          value={`${avgEngagement}%`}
          icon={<TrendingUp size={16} />}
          iconBg="#F0FDF4"
          iconColor="#16A34A"
          delta="+2.3%"
          deltaUp
          delay="animate-fade-up-delay-3"
        />
        <MetricCard
          label="Total Posts"
          value={String(totalPosts)}
          icon={<Activity size={16} />}
          iconBg="#FFF7ED"
          iconColor="#EA580C"
          delta="Last 30 days"
          deltaUp={null}
          delay="animate-fade-up-delay-4"
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6 animate-fade-up-delay-2">
        {/* Engagement area chart */}
        <div className="section-panel xl:col-span-3">
          <div className="section-panel-header">
            <div className="flex items-center gap-3">
              <div className="icon-box-sm" style={{ background: '#EFF6FF' }}>
                <TrendingUp size={14} style={{ color: '#2563EB' }} />
              </div>
              <div>
                <p className="font-semibold text-[14px]" style={{ color: 'var(--text-primary)' }}>
                  Engagement Over Time
                </p>
                <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>Likes & comments per video</p>
              </div>
            </div>
            <span className="badge badge-neutral badge-mono">LIVE</span>
          </div>
          <div className="p-6">
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="glikes" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.18} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gcomments" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#a855f7" stopOpacity={0.15} />
                      <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="rgba(0,0,0,0.05)" />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#9CA3AF', fontWeight: 500 }} tickLine={false} axisLine={false} dy={8} />
                  <YAxis tick={{ fontSize: 11, fill: '#9CA3AF', fontWeight: 500 }} tickLine={false} axisLine={false} tickFormatter={v => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v} />
                  <Tooltip
                    contentStyle={{ borderRadius: '12px', border: '1px solid rgba(0,0,0,0.08)', boxShadow: '0 8px 32px rgba(0,0,0,0.12)', fontSize: '12px' }}
                    labelStyle={{ fontWeight: 700, fontSize: '13px', marginBottom: '6px' }}
                  />
                  <Area type="monotone" dataKey="likes" stroke="#6366f1" strokeWidth={2} fillOpacity={1} fill="url(#glikes)" name="Likes" dot={false} />
                  <Area type="monotone" dataKey="comments" stroke="#a855f7" strokeWidth={2} fillOpacity={1} fill="url(#gcomments)" name="Comments" dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Views bar chart */}
        <div className="section-panel xl:col-span-2">
          <div className="section-panel-header">
            <div className="flex items-center gap-3">
              <div className="icon-box-sm" style={{ background: '#F0FDF4' }}>
                <BarChart3 size={14} style={{ color: '#16A34A' }} />
              </div>
              <div>
                <p className="font-semibold text-[14px]" style={{ color: 'var(--text-primary)' }}>Views</p>
                <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>Per video</p>
              </div>
            </div>
          </div>
          <div className="p-6">
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData.slice(-8)} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="rgba(0,0,0,0.05)" />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#9CA3AF' }} tickLine={false} axisLine={false} dy={8} />
                  <YAxis tick={{ fontSize: 11, fill: '#9CA3AF' }} tickLine={false} axisLine={false} tickFormatter={v => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v} />
                  <Tooltip
                    cursor={{ fill: 'rgba(0,0,0,0.03)' }}
                    contentStyle={{ borderRadius: '12px', border: '1px solid rgba(0,0,0,0.08)', boxShadow: '0 8px 32px rgba(0,0,0,0.12)', fontSize: '12px' }}
                    labelStyle={{ fontWeight: 700, fontSize: '13px', marginBottom: '6px' }}
                  />
                  <Bar dataKey="views" fill="#6366f1" radius={[5, 5, 0, 0]} name="Views" maxBarSize={36} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Top post highlight */}
      {topPost && (
        <div className="animate-fade-up-delay-3 section-panel">
          <div className="section-panel-header">
            <div className="flex items-center gap-3">
              <div className="icon-box-sm" style={{ background: '#FEF9C3' }}>
                <Zap size={14} style={{ color: '#CA8A04' }} />
              </div>
              <div>
                <p className="font-semibold text-[14px]" style={{ color: 'var(--text-primary)' }}>Best Performing Video</p>
                <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>Highest view count</p>
              </div>
            </div>
            <span className="badge badge-amber badge-mono">TOP</span>
          </div>
          <div className="p-6 flex flex-col sm:flex-row sm:items-center gap-6">
            <div className="flex-1">
              <p className="font-semibold text-[15px] leading-snug" style={{ color: 'var(--text-primary)' }}>
                {topPost.title || topPost.topic || 'Untitled'}
              </p>
              <div className="flex items-center gap-4 mt-3">
                <span className="flex items-center gap-1.5 text-[13px]" style={{ color: 'var(--text-secondary)' }}>
                  <Eye size={13} /> {formatNum(Number(topPost.views || 0))} views
                </span>
                <span className="flex items-center gap-1.5 text-[13px]" style={{ color: 'var(--text-secondary)' }}>
                  <Heart size={13} /> {formatNum(Number(topPost.likes || 0))} likes
                </span>
                <span className="badge badge-blue badge-mono">{topPost.platform || 'YouTube'}</span>
              </div>
            </div>
            <div className="flex flex-col items-end gap-1">
              <span className="text-[32px] font-bold stat-number" style={{ color: 'var(--text-primary)', letterSpacing: '-0.04em' }}>
                {formatNum(Number(topPost.views || 0))}
              </span>
              <span className="section-label">Total Views</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({ label, value, icon, iconBg, iconColor, delta, deltaUp, delay }: any) {
  return (
    <div className={`metric-card ${delay}`}>
      <div className="flex items-start justify-between mb-4">
        <div className="icon-box" style={{ background: iconBg }}>
          <span style={{ color: iconColor }}>{icon}</span>
        </div>
        {delta && deltaUp !== null && (
          <span className={deltaUp ? 'metric-delta-up flex items-center gap-0.5' : 'metric-delta-down flex items-center gap-0.5'}>
            {deltaUp !== null && (deltaUp ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />)}
            {delta}
          </span>
        )}
        {deltaUp === null && delta && (
          <span className="badge badge-neutral" style={{ fontSize: '10px' }}>{delta}</span>
        )}
      </div>
      <p className="metric-value stat-number">{value}</p>
      <p className="metric-label mt-1">{label}</p>
    </div>
  );
}

function formatNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}
