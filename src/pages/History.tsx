import React, { useEffect, useState } from 'react';
import { Post } from '../types';
import { RefreshCw, Search, Youtube, Instagram, Linkedin, Twitter, Eye, Heart, MessageCircle, Brain, Loader2 } from 'lucide-react';
import { apiUrl } from '../api';

const platformConfig: Record<string, { icon: any; color: string; bg: string }> = {
  YouTube:   { icon: Youtube,   color: '#DC2626', bg: '#FEF2F2' },
  Instagram: { icon: Instagram, color: '#DB2777', bg: '#FDF2F8' },
  LinkedIn:  { icon: Linkedin,  color: '#2563EB', bg: '#EFF6FF' },
  Twitter:   { icon: Twitter,   color: '#0284C7', bg: '#F0F9FF' },
};

export default function History() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [analyzeMsg, setAnalyzeMsg] = useState<string | null>(null);

  useEffect(() => { fetchPosts(); }, []);

  const fetchPosts = (withSync = false) => {
    setLoading(true);
    const url = withSync ? apiUrl('/api/posts?sync=true') : apiUrl('/api/posts');
    fetch(url)
      .then(res => res.json())
      .then(data => {
        const posts = (data.statusCode && data.body) ? JSON.parse(data.body) : data;
        setPosts(Array.isArray(posts) ? posts : []);
        setLoading(false);
        setSyncing(false);
      })
      .catch(() => { setLoading(false); setSyncing(false); });
  };

  const handleSync = () => { setSyncing(true); fetchPosts(true); };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setAnalyzeMsg(null);
    try {
      const res = await fetch(apiUrl('/api/analyze'), { method: 'POST' });
      if (res.ok) setAnalyzeMsg('Analysis complete! Check Creator Intelligence.');
      else setAnalyzeMsg('Analysis failed. Please try again.');
    } catch {
      setAnalyzeMsg('Network error. Check your connection.');
    } finally {
      setAnalyzing(false);
    }
  };

  const filtered = posts.filter(p => {
    const text = [p.content, p.title, p.platform, p.topic].join(' ').toLowerCase();
    return text.includes(searchTerm.toLowerCase());
  });

  const fmt = (n: number | string | undefined) => {
    const num = Number(n || 0);
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
    if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
    return num.toLocaleString();
  };

  return (
    <div className="space-y-7">
      {/* Header */}
      <div className="animate-fade-up flex items-start justify-between gap-4 flex-wrap">
        <div className="space-y-1">
          <p className="page-eyebrow"><Youtube size={12} className="inline" /> YouTube API</p>
          <h1 className="page-title">Content History</h1>
          <p className="page-sub">Your last {posts.length} published videos with real-time metrics.</p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0 flex-wrap">
          <button onClick={handleSync} disabled={syncing} className="btn btn-secondary gap-2">
            <RefreshCw size={13} className={syncing ? 'animate-spin' : ''} />
            {syncing ? 'Syncing...' : 'Sync Live'}
          </button>
          <button onClick={handleAnalyze} disabled={analyzing} className="btn btn-primary gap-2">
            {analyzing ? <Loader2 size={13} className="animate-spin" /> : <Brain size={13} />}
            {analyzing ? 'Analyzing...' : 'Run AI Analysis'}
          </button>
        </div>
      </div>

      {analyzeMsg && (
        <div className="flex items-center gap-3 p-4 rounded-xl animate-fade-in" style={{ background: '#F0FDF4', border: '1px solid #BBF7D0' }}>
          <span style={{ color: '#16A34A' }}>✓</span>
          <span className="text-[13.5px] font-medium" style={{ color: '#166534' }}>{analyzeMsg}</span>
        </div>
      )}

      {/* Search + table */}
      <div className="section-panel animate-fade-up-delay-1">
        <div className="section-panel-header gap-4 flex-wrap">
          <div className="relative flex-1 min-w-[200px]">
            <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
            <input
              className="input pl-8 py-2"
              placeholder="Search videos, topics..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              style={{ fontSize: '13px' }}
            />
          </div>
          <span className="badge badge-neutral badge-mono">{filtered.length} VIDEOS</span>
        </div>

        {loading ? (
          <div className="p-8 flex items-center justify-center">
            <div className="flex flex-col items-center gap-4">
              <div className="w-8 h-8 rounded-full border-2 animate-spin" style={{ borderColor: 'rgba(0,0,0,0.1)', borderTopColor: 'var(--text-primary)' }} />
              <span className="section-label">Loading videos...</span>
            </div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 flex flex-col items-center text-center">
            <div className="icon-box mb-4" style={{ background: 'var(--bg-tag)', width: 52, height: 52, borderRadius: 14 }}>
              <Youtube size={22} style={{ color: 'var(--text-muted)' }} />
            </div>
            <p className="text-[15px] font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>No videos found</p>
            <p className="text-[13px]" style={{ color: 'var(--text-secondary)' }}>Try syncing your YouTube channel or adjusting your search.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Platform</th>
                  <th>Title</th>
                  <th>Views</th>
                  <th>Likes</th>
                  <th>Comments</th>
                  <th>Published</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((post, i) => {
                  const pc = platformConfig[post.platform] || platformConfig.YouTube;
                  const Icon = pc.icon;
                  return (
                    <tr key={i}>
                      <td>
                        <div className="flex items-center gap-2">
                          <div className="w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0" style={{ background: pc.bg }}>
                            <Icon size={12} style={{ color: pc.color }} />
                          </div>
                          <span className="text-[11px] font-semibold badge-mono" style={{ color: pc.color }}>{post.platform || 'YT'}</span>
                        </div>
                      </td>
                      <td>
                        <p className="font-medium text-[13px] max-w-xs truncate" style={{ color: 'var(--text-primary)' }} title={post.title}>
                          {post.title || post.topic || 'Untitled'}
                        </p>
                      </td>
                      <td>
                        <div className="flex items-center gap-1.5">
                          <Eye size={12} style={{ color: 'var(--text-muted)' }} />
                          <span className="font-semibold text-[13px] stat-number" style={{ color: 'var(--text-primary)' }}>{fmt(post.views)}</span>
                        </div>
                      </td>
                      <td>
                        <div className="flex items-center gap-1.5">
                          <Heart size={12} style={{ color: 'var(--text-muted)' }} />
                          <span className="text-[13px] stat-number" style={{ color: 'var(--text-secondary)' }}>{fmt(post.likes)}</span>
                        </div>
                      </td>
                      <td>
                        <div className="flex items-center gap-1.5">
                          <MessageCircle size={12} style={{ color: 'var(--text-muted)' }} />
                          <span className="text-[13px] stat-number" style={{ color: 'var(--text-secondary)' }}>{fmt(post.comments)}</span>
                        </div>
                      </td>
                      <td>
                        <span className="text-[12px]" style={{ color: 'var(--text-muted)' }}>
                          {post.timestamp ? new Date(post.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' }) : '—'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
