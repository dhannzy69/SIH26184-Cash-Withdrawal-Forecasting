import React, { useState } from 'react';
import { ShieldAlert, UserCheck, UserX, LogIn, LogOut, Key, Shield, User } from 'lucide-react';
import { api } from '../services/api';

export default function Header({ systemStatus, currentUser, onLogin, onLogout }) {
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const demoAccounts = [
    {
      label: 'Insp. Vikram Sharma',
      badge: 'CYBER-108 (Investigator)',
      user: 'officer_sharma',
      pass: 'investigator123',
      role: 'INVESTIGATOR'
    },
    {
      label: 'Central Admin',
      badge: 'ADMIN-001 (Operations)',
      user: 'admin',
      pass: 'admin123',
      role: 'ADMIN'
    },
    {
      label: 'SI Rajesh Gowda',
      badge: 'FIELD-501 (Bengaluru Tactical)',
      user: 'field_unit_blr',
      pass: 'patrol123',
      role: 'FIELD_OFFICER'
    }
  ];

  const handleLoginSubmit = async (e) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setLoginError(null);

    try {
      const res = await api.login(username, password);
      onLogin(res.user, res.access_token);
      setShowLoginModal(false);
      setUsername('');
      setPassword('');
    } catch (err) {
      setLoginError('Invalid username or password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickDemoLogin = async (demo) => {
    setUsername(demo.user);
    setPassword(demo.pass);
    setIsLoading(true);
    setLoginError(null);

    try {
      const res = await api.login(demo.user, demo.pass);
      onLogin(res.user, res.access_token);
      setShowLoginModal(false);
      setUsername('');
      setPassword('');
    } catch (err) {
      setLoginError('Failed to login with demo account.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <header style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 0 1.5rem 0',
        borderBottom: '1px solid var(--border-subtle)',
        marginBottom: '1.5rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: 'var(--radius-md)',
            background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(59, 130, 246, 0.2))',
            border: '1px solid var(--border-glow)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px var(--cyan-glow)'
          }}>
            <ShieldAlert size={26} color="#06b6d4" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <h1 style={{ fontSize: '1.35rem', color: '#f8fafc' }}>
                SIH26184 <span style={{ color: '#38bdf8' }}>Forecaster</span>
              </h1>
              <span className="badge badge-cyan">Cyber Intervention</span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Predictive Analytics Framework to Forecast Likely Cash-Withdrawal ATM Clusters
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* Backend Connectivity Status */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.4rem 0.85rem',
            background: 'rgba(15, 23, 42, 0.8)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.78rem'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: systemStatus ? '#10b981' : '#ef4444',
              boxShadow: systemStatus ? '0 0 8px #10b981' : '0 0 8px #ef4444'
            }} />
            <span style={{ color: systemStatus ? '#34d399' : '#f87171', fontWeight: 600 }}>
              {systemStatus ? 'Backend Connected' : 'Connecting...'}
            </span>
            <span style={{ color: 'var(--text-dim)', fontSize: '0.72rem' }}>| 180m Horizon</span>
          </div>

          {/* Officer Profile & Authentication Control */}
          {currentUser ? (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.65rem',
              padding: '0.35rem 0.65rem 0.35rem 0.85rem',
              background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95))',
              border: '1px solid rgba(56, 189, 248, 0.3)',
              borderRadius: 'var(--radius-md)',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
            }}>
              <UserCheck size={18} color="#38bdf8" />
              <div style={{ fontSize: '0.78rem', lineHeight: '1.2' }}>
                <div style={{ fontWeight: 700, color: '#f8fafc' }}>
                  {currentUser.full_name || currentUser.username}
                </div>
                <div style={{ color: '#94a3b8', fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span>{currentUser.badge_number || 'OFFICER'}</span>
                  <span className="badge" style={{
                    fontSize: '0.6rem',
                    padding: '0.1rem 0.35rem',
                    background: currentUser.role === 'ADMIN' ? 'rgba(168, 85, 247, 0.2)' : 'rgba(6, 182, 212, 0.2)',
                    color: currentUser.role === 'ADMIN' ? '#c084fc' : '#22d3ee'
                  }}>
                    {currentUser.role}
                  </span>
                </div>
              </div>

              {/* Logout Button */}
              <button
                onClick={onLogout}
                title="Logout of current officer account"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.3rem',
                  marginLeft: '0.4rem',
                  padding: '0.3rem 0.6rem',
                  borderRadius: 'var(--radius-sm)',
                  background: 'rgba(244, 63, 94, 0.15)',
                  border: '1px solid rgba(244, 63, 94, 0.4)',
                  color: '#fb7185',
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'var(--transition)'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = 'rgba(244, 63, 94, 0.3)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = 'rgba(244, 63, 94, 0.15)';
                }}
              >
                <LogOut size={13} color="#f43f5e" />
                <span>Logout</span>
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowLoginModal(true)}
              className="btn btn-primary"
              style={{
                padding: '0.45rem 0.95rem',
                fontSize: '0.8rem',
                gap: '0.4rem'
              }}
            >
              <LogIn size={15} />
              <span>Officer Login</span>
            </button>
          )}
        </div>
      </header>

      {/* Login & Account Switcher Modal */}
      {showLoginModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(7, 10, 18, 0.85)',
          backdropFilter: 'blur(8px)',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '1rem'
        }}>
          <div className="glass-card" style={{
            maxWidth: '440px',
            width: '100%',
            background: 'rgba(15, 23, 42, 0.95)',
            border: '1px solid var(--border-glow)',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.8)',
            padding: '1.75rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Shield size={20} color="#38bdf8" />
                <h2 style={{ fontSize: '1.15rem', color: '#f8fafc' }}>Officer Authentication</h2>
              </div>
              <button
                onClick={() => setShowLoginModal(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-dim)',
                  fontSize: '1.25rem',
                  cursor: 'pointer'
                }}
              >
                ✕
              </button>
            </div>

            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
              Access authorized predictive analytics dossiers and surveillance dispatch capabilities.
            </p>

            {/* Quick Demo Login Presets */}
            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ fontSize: '0.72rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
                QUICK DEMO PRESETS (ONE-CLICK LOGIN):
              </label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
                {demoAccounts.map(demo => (
                  <button
                    key={demo.user}
                    type="button"
                    onClick={() => handleQuickDemoLogin(demo)}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '0.55rem 0.85rem',
                      borderRadius: 'var(--radius-sm)',
                      background: 'rgba(30, 41, 59, 0.6)',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      color: '#f8fafc',
                      fontSize: '0.78rem',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'var(--transition)'
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.borderColor = 'var(--cyan)';
                      e.currentTarget.style.background = 'rgba(6, 182, 212, 0.15)';
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
                      e.currentTarget.style.background = 'rgba(30, 41, 59, 0.6)';
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 600 }}>{demo.label}</div>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>{demo.badge}</div>
                    </div>
                    <span className="badge badge-cyan" style={{ fontSize: '0.62rem' }}>
                      {demo.role}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              margin: '1.25rem 0',
              color: 'var(--text-dim)',
              fontSize: '0.72rem'
            }}>
              <div style={{ flex: 1, height: '1px', background: 'rgba(255, 255, 255, 0.1)' }} />
              <span>OR MANUAL CREDENTIALS</span>
              <div style={{ flex: 1, height: '1px', background: 'rgba(255, 255, 255, 0.1)' }} />
            </div>

            {/* Manual Form */}
            <form onSubmit={handleLoginSubmit}>
              <div style={{ marginBottom: '0.85rem' }}>
                <label style={{ fontSize: '0.72rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.3rem' }}>
                  USERNAME:
                </label>
                <input
                  type="text"
                  placeholder="e.g. officer_sharma"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ fontSize: '0.72rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.3rem' }}>
                  PASSWORD:
                </label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              {loginError && (
                <div style={{
                  padding: '0.5rem 0.75rem',
                  background: 'rgba(244, 63, 94, 0.15)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.75rem',
                  color: '#fb7185',
                  marginBottom: '1rem'
                }}>
                  {loginError}
                </div>
              )}

              <button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%' }}
                disabled={isLoading}
              >
                {isLoading ? 'Authenticating...' : 'Sign In as Officer'}
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
