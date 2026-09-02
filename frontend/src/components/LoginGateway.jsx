import React, { useState } from 'react';
import { ShieldAlert, Shield, Lock, UserCheck, ArrowRight, Activity, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

export default function LoginGateway({ systemOnline, onLogin }) {
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
      role: 'INVESTIGATOR',
      desc: 'Full forensic access: Multi-hop graph, SHAP explainability, and what-if simulation'
    },
    {
      label: 'Central Operations Admin',
      badge: 'ADMIN-001 (Command Oversight)',
      user: 'admin',
      pass: 'admin123',
      role: 'ADMIN',
      desc: 'High-level strategic KPI command: 600 complaints, statewide surveillance monitoring'
    },
    {
      label: 'SI Rajesh Gowda',
      badge: 'FIELD-501 (Tactical Patrol Unit)',
      user: 'field_unit_blr',
      pass: 'patrol123',
      role: 'FIELD_OFFICER',
      desc: 'Ground patrol mode: Top-priority urgent alert dispatches & on-site interception'
    }
  ];

  const handleManualLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setLoginError(null);

    try {
      const res = await api.login(username, password);
      onLogin(res.user, res.access_token);
    } catch (err) {
      setLoginError('Invalid officer credentials. Please check your username and password.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoSelect = async (demo) => {
    setUsername(demo.user);
    setPassword(demo.pass);
    setIsLoading(true);
    setLoginError(null);

    try {
      const res = await api.login(demo.user, demo.pass);
      onLogin(res.user, res.access_token);
    } catch (err) {
      setLoginError('Failed to authenticate with demo profile.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem 1rem',
      background: 'radial-gradient(ellipse at center, rgba(14, 165, 233, 0.12) 0%, rgba(7, 10, 18, 0.95) 70%)'
    }}>
      {/* Portal Branding Badge */}
      <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '64px',
          height: '64px',
          borderRadius: '16px',
          background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.25), rgba(59, 130, 246, 0.25))',
          border: '1px solid var(--border-glow)',
          boxShadow: '0 0 30px rgba(6, 182, 212, 0.35)',
          marginBottom: '1rem'
        }}>
          <ShieldAlert size={36} color="#06b6d4" />
        </div>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }}>
          SIH26184 <span style={{ color: '#38bdf8' }}>Forecasting Portal</span>
        </h1>
        <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', maxWidth: '480px', margin: '0.4rem auto 0 auto' }}>
          Predictive Analytics Framework for Cybercrime Complaints to Forecast Likely Cash-Withdrawal ATM Clusters
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '0.75rem', marginTop: '0.85rem' }}>
          <span className="badge badge-cyan">🔒 Law Enforcement Restricted</span>
          <span className="badge" style={{
            background: systemOnline ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
            color: systemOnline ? '#34d399' : '#fb7185',
            border: systemOnline ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid rgba(244, 63, 94, 0.4)'
          }}>
            {systemOnline ? '● Backend Operational' : '○ Connecting Backend...'}
          </span>
        </div>
      </div>

      {/* Main Authentication Card */}
      <div className="glass-card" style={{
        maxWidth: '520px',
        width: '100%',
        background: 'rgba(15, 23, 42, 0.9)',
        border: '1px solid rgba(56, 189, 248, 0.3)',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.75)',
        padding: '2rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <Lock size={20} color="#38bdf8" />
          <h2 style={{ fontSize: '1.2rem', color: '#f8fafc' }}>Officer Sign-In</h2>
        </div>

        {/* 1-Click Demo Profiles */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ fontSize: '0.72rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.6rem', fontWeight: 700, letterSpacing: '0.05em' }}>
            SELECT OPERATIONAL ROLE (1-CLICK DEMO):
          </label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {demoAccounts.map(demo => (
              <button
                key={demo.user}
                type="button"
                onClick={() => handleDemoSelect(demo)}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.75rem 1rem',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(30, 41, 59, 0.7)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  color: '#f8fafc',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'var(--transition)'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = 'var(--cyan)';
                  e.currentTarget.style.background = 'rgba(6, 182, 212, 0.15)';
                  e.currentTarget.style.transform = 'translateX(4px)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
                  e.currentTarget.style.background = 'rgba(30, 41, 59, 0.7)';
                  e.currentTarget.style.transform = 'none';
                }}
              >
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.88rem', color: '#f8fafc' }}>
                    {demo.label}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginBottom: '0.2rem' }}>
                    {demo.badge}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    {demo.desc}
                  </div>
                </div>
                <ArrowRight size={16} color="#38bdf8" />
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
          <span>OR SIGN IN WITH CREDENTIALS</span>
          <div style={{ flex: 1, height: '1px', background: 'rgba(255, 255, 255, 0.1)' }} />
        </div>

        {/* Manual Login Form */}
        <form onSubmit={handleManualLogin}>
          <div style={{ marginBottom: '0.85rem' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.35rem' }}>
              OFFICER USERNAME:
            </label>
            <input
              type="text"
              placeholder="e.g. officer_sharma"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.35rem' }}>
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
              padding: '0.65rem 0.85rem',
              background: 'rgba(244, 63, 94, 0.15)',
              border: '1px solid rgba(244, 63, 94, 0.4)',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.78rem',
              color: '#fb7185',
              marginBottom: '1rem'
            }}>
              {loginError}
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.75rem', fontSize: '0.9rem' }}
            disabled={isLoading}
          >
            {isLoading ? 'Verifying Credentials...' : 'Authenticate & Access Portal'}
          </button>
        </form>
      </div>

      <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.72rem', color: 'var(--text-dim)' }}>
        Smart India Hackathon 2024 • Team Apex Pointers (Problem Statement #184)
      </div>
    </div>
  );
}
