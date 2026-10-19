import React, { useState, useEffect } from 'react';
import { ReviewStudio } from './components/ReviewStudio';
import { ScanHistoryPage } from './pages/ScanHistoryPage';
import { AboutPage } from './pages/AboutPage';
import { PrivacyPolicyPage } from './pages/PrivacyPolicyPage';
import { AuthModal } from './components/AuthModal';
import { api } from './services/api';
import { User } from './types';
import {
  ShieldCheck,
  Code2,
  History,
  Info,
  FileText,
  LogIn,
  LogOut,
} from 'lucide-react';

type TabType = 'studio' | 'history' | 'about' | 'privacy';

export function App() {
  const [activeTab, setActiveTab] = useState<TabType>('studio');
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);

  useEffect(() => {
    api.getMe()
      .then(setCurrentUser)
      .catch(() => setCurrentUser(null));
  }, []);

  useEffect(() => {
    if (!currentUser && activeTab === 'history') {
      setActiveTab('studio');
    }
  }, [currentUser, activeTab]);

  const handleLogout = () => {
    api.logout();
    setCurrentUser(null);
    setActiveTab('studio');
  };

  return (
    <div className="min-h-screen bg-[#000000] text-[#EDEDED] flex flex-col font-sans selection:bg-white selection:text-black">
      {/* Sleek Top Navigation Bar */}
      <header className="h-16 px-6 md:px-10 border-b border-[#1A1A1A] bg-[#000000]/95 backdrop-blur sticky top-0 z-40 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('studio')}>
          <div className="p-2 bg-white text-black rounded-lg shadow-sm">
            <ShieldCheck className="w-5 h-5 fill-black text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-bold text-white tracking-wide">CodeGuard AI</span>
              <span className="hidden sm:inline-block px-1.5 py-0.5 rounded text-[10px] font-mono bg-[#141414] text-[#888888] border border-[#222222]">
                v1.0
              </span>
            </div>
            <p className="text-[10px] text-[#666666]">Intelligent Code Review & Security</p>
          </div>
        </div>

        {/* Dynamic Navigation Tabs */}
        <nav className="flex items-center space-x-1 bg-[#0A0A0A] p-1 rounded-xl border border-[#1A1A1A]">
          {/* Review Studio */}
          <button
            onClick={() => setActiveTab('studio')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
              activeTab === 'studio'
                ? 'bg-[#1C1C1C] text-white shadow-sm'
                : 'text-[#888888] hover:text-white hover:bg-[#121212]'
            }`}
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>Review Studio</span>
          </button>

          {/* Audit History (Visible to authenticated users) */}
          {currentUser && (
            <button
              onClick={() => setActiveTab('history')}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                activeTab === 'history'
                  ? 'bg-[#1C1C1C] text-white shadow-sm'
                  : 'text-[#888888] hover:text-white hover:bg-[#121212]'
              }`}
            >
              <History className="w-3.5 h-3.5" />
              <span>Audit History</span>
            </button>
          )}

          {/* About Page */}
          <button
            onClick={() => setActiveTab('about')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
              activeTab === 'about'
                ? 'bg-[#1C1C1C] text-white shadow-sm'
                : 'text-[#888888] hover:text-white hover:bg-[#121212]'
            }`}
          >
            <Info className="w-3.5 h-3.5" />
            <span>About</span>
          </button>

          {/* Privacy Policy Page */}
          <button
            onClick={() => setActiveTab('privacy')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
              activeTab === 'privacy'
                ? 'bg-[#1C1C1C] text-white shadow-sm'
                : 'text-[#888888] hover:text-white hover:bg-[#121212]'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Privacy Policy</span>
          </button>
        </nav>

        {/* User Authentication Menu */}
        <div className="flex items-center space-x-3">
          {currentUser ? (
            <div className="flex items-center space-x-2.5 bg-[#0A0A0A] border border-[#1F1F1F] px-3 py-1.5 rounded-xl">
              <div className="w-6 h-6 rounded-lg bg-white text-black font-bold flex items-center justify-center text-[11px]">
                {currentUser.username[0].toUpperCase()}
              </div>
              <div className="hidden sm:block text-left">
                <span className="text-xs font-semibold text-white block leading-tight">
                  {currentUser.username}
                </span>
                <span className="text-[10px] text-[#666666] block leading-none">{currentUser.email}</span>
              </div>
              <button
                onClick={handleLogout}
                className="text-[#666666] hover:text-red-400 p-1 rounded-md transition ml-1 cursor-pointer"
                title="Sign Out"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => setIsAuthOpen(true)}
              className="flex items-center space-x-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-[#141414] hover:bg-[#202020] text-white border border-[#262626] transition cursor-pointer shadow-sm active:scale-95"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Sign In</span>
            </button>
          )}
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8">
        {activeTab === 'studio' && (
          <ReviewStudio
            currentUser={currentUser}
            onRequireAuth={() => setIsAuthOpen(true)}
          />
        )}
        {activeTab === 'history' && currentUser && (
          <ScanHistoryPage onNavigate={() => setActiveTab('studio')} />
        )}
        {activeTab === 'about' && <AboutPage />}
        {activeTab === 'privacy' && <PrivacyPolicyPage />}
      </main>

      {/* Minimalist Footer */}
      <footer className="border-t border-[#141414] py-4 px-6 md:px-10 flex flex-col sm:flex-row items-center justify-between text-[11px] text-[#555555] gap-3">
        <div>
          CodeGuard AI &bull; Air-Gapped Static Analysis Engine &bull; Zero Third-Party Cloud Data Leakage
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setActiveTab('about')}
            className="hover:text-white transition cursor-pointer"
          >
            About
          </button>
          <button
            onClick={() => setActiveTab('privacy')}
            className="hover:text-white transition cursor-pointer"
          >
            Privacy Policy
          </button>
        </div>
      </footer>

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onSuccess={(user) => setCurrentUser(user)}
      />
    </div>
  );
}

export default App;
