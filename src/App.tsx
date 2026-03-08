import React, { useState, useEffect } from 'react';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Intelligence from './pages/Intelligence';
import NewPost from './pages/NewPost';
import CreatorEngine from './pages/CreatorEngine';
import Generate from './pages/Generate';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    const path = window.location.pathname;
    if (path === '/generate') {
      setActiveTab('generate');
    }
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'creator-engine':
        return <CreatorEngine />;
      case 'history':
        return <History />;
      case 'intelligence':
        return <Intelligence />;
      case 'new-post':
        return <NewPost />;
      case 'generate':
        return <Generate />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <Layout activeTab={activeTab} onTabChange={setActiveTab}>
      {renderContent()}
    </Layout>
  );
}
