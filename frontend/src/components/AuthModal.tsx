import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { User } from '../types';
import { ShieldCheck, X, LogIn, UserPlus, KeyRound, Mail, User as UserIcon, AlertCircle } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (user: User) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [tab, setTab] = useState<'login' | 'register'>('login');
  
  // Login Form
  const [loginIdent, setLoginIdent] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register Form
  const [regFullName, setRegFullName] = useState('');
  const [regUsername, setRegUsername] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resetForms = () => {
    setLoginIdent('');
    setLoginPassword('');
    setRegFullName('');
    setRegUsername('');
    setRegEmail('');
    setRegPassword('');
    setError(null);
  };

  // Automatically clear all input fields whenever the modal opens or closes
  useEffect(() => {
    if (isOpen) {
      resetForms();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleModalClose = () => {
    resetForms();
    onClose();
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!loginIdent.trim() || !loginPassword) {
      setError('Please provide your username or email and password.');
      return;
    }
    try {
      setLoading(true);
      const res = await api.login({
        username_or_email: loginIdent.trim(),
        password: loginPassword,
      });
      resetForms();
      onSuccess(res.user);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Invalid credentials. Please verify your details.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!regUsername.trim() || !regEmail.trim() || !regPassword) {
      setError('Please fill in all required fields.');
      return;
    }
    if (regPassword.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    try {
      setLoading(true);
      const res = await api.register({
        email: regEmail.trim(),
        username: regUsername.trim(),
        password: regPassword,
        full_name: regFullName.trim() || undefined,
      });
      resetForms();
      onSuccess(res.user);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-sm animate-fadeIn">
      <div className="bg-[#0A0A0A] border border-[#222222] rounded-2xl w-full max-w-md p-6 shadow-2xl relative space-y-6">
        {/* Close Button */}
        <button
          onClick={handleModalClose}
          className="absolute top-4 right-4 text-[#666666] hover:text-white p-1 rounded-lg hover:bg-[#1A1A1A] transition cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Brand Header */}
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-white text-black rounded-lg">
            <ShieldCheck className="w-5 h-5 fill-black text-white" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">CodeGuard AI Security</h3>
            <p className="text-xs text-[#777777]">Account Authentication & Scan Privacy</p>
          </div>
        </div>

        {/* Tab Toggle */}
        <div className="flex bg-[#050505] p-1 rounded-xl border border-[#1A1A1A]">
          <button
            type="button"
            onClick={() => { setTab('login'); resetForms(); }}
            className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition cursor-pointer ${
              tab === 'login'
                ? 'bg-[#1C1C1C] text-white shadow-sm'
                : 'text-[#888888] hover:text-white'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setTab('register'); resetForms(); }}
            className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition cursor-pointer ${
              tab === 'register'
                ? 'bg-[#1C1C1C] text-white shadow-sm'
                : 'text-[#888888] hover:text-white'
            }`}
          >
            Create Account
          </button>
        </div>

        {error && (
          <div className="p-3 bg-red-950/20 border border-red-800/40 rounded-xl flex items-center space-x-2 text-red-400 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Tab: Sign In */}
        {tab === 'login' ? (
          <form onSubmit={handleLogin} autoComplete="off" className="space-y-4">
            <div className="space-y-1">
              <label className="text-xs font-semibold text-[#AAAAAA]">Username or Email</label>
              <div className="relative">
                <UserIcon className="w-3.5 h-3.5 absolute left-3 top-3 text-[#555555]" />
                <input
                  type="text"
                  placeholder="Enter username or email"
                  value={loginIdent}
                  onChange={(e) => setLoginIdent(e.target.value)}
                  autoComplete="off"
                  className="w-full bg-[#050505] border border-[#222222] rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-[#555555] focus:outline-none focus:border-[#444444]"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-[#AAAAAA]">Password</label>
              <div className="relative">
                <KeyRound className="w-3.5 h-3.5 absolute left-3 top-3 text-[#555555]" />
                <input
                  type="password"
                  placeholder="••••••••"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  autoComplete="new-password"
                  className="w-full bg-[#050505] border border-[#222222] rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-[#555555] focus:outline-none focus:border-[#444444]"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-white hover:bg-[#E5E5E5] text-black font-bold text-xs rounded-xl transition flex items-center justify-center space-x-2 disabled:opacity-50 cursor-pointer shadow-lg active:scale-98"
            >
              <LogIn className="w-3.5 h-3.5 fill-black" />
              <span>{loading ? 'Signing in...' : 'Sign In'}</span>
            </button>
          </form>
        ) : (
          /* Tab: Create Account */
          <form onSubmit={handleRegister} autoComplete="off" className="space-y-4">
            <div className="space-y-1">
              <label className="text-xs font-semibold text-[#AAAAAA]">Display Name (Optional)</label>
              <input
                type="text"
                placeholder="Alex Developer"
                value={regFullName}
                onChange={(e) => setRegFullName(e.target.value)}
                autoComplete="off"
                className="w-full bg-[#050505] border border-[#222222] rounded-lg px-3 py-2 text-xs text-white placeholder-[#555555] focus:outline-none focus:border-[#444444]"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-[#AAAAAA]">Username *</label>
              <div className="relative">
                <UserIcon className="w-3.5 h-3.5 absolute left-3 top-3 text-[#555555]" />
                <input
                  type="text"
                  placeholder="alex24"
                  value={regUsername}
                  onChange={(e) => setRegUsername(e.target.value)}
                  autoComplete="off"
                  className="w-full bg-[#050505] border border-[#222222] rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-[#555555] focus:outline-none focus:border-[#444444]"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-[#AAAAAA]">Email *</label>
              <div className="relative">
                <Mail className="w-3.5 h-3.5 absolute left-3 top-3 text-[#555555]" />
                <input
                  type="email"
                  placeholder="alex@example.com"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  autoComplete="off"
                  className="w-full bg-[#050505] border border-[#222222] rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-[#555555] focus:outline-none focus:border-[#444444]"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-[#AAAAAA]">Password *</label>
              <div className="relative">
                <KeyRound className="w-3.5 h-3.5 absolute left-3 top-3 text-[#555555]" />
                <input
                  type="password"
                  placeholder="At least 6 characters"
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  autoComplete="new-password"
                  className="w-full bg-[#050505] border border-[#222222] rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-[#555555] focus:outline-none focus:border-[#444444]"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-white hover:bg-[#E5E5E5] text-black font-bold text-xs rounded-xl transition flex items-center justify-center space-x-2 disabled:opacity-50 cursor-pointer shadow-lg active:scale-98"
            >
              <UserPlus className="w-3.5 h-3.5" />
              <span>{loading ? 'Creating Account...' : 'Create Account'}</span>
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
