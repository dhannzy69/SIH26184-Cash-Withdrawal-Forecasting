import React from 'react';
import { ShieldAlert, Activity, UserCheck, Shield } from 'lucide-react';

export default function Header({ systemStatus }) {
  return (
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

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
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

        {/* Officer Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.6rem',
          padding: '0.35rem 0.85rem',
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9))',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 'var(--radius-md)'
        }}>
          <UserCheck size={18} color="#60a5fa" />
          <div style={{ fontSize: '0.78rem', lineHeight: '1.2' }}>
            <div style={{ fontWeight: 600, color: '#f8fafc' }}>Insp. Vikram Sharma</div>
            <div style={{ color: 'var(--text-dim)', fontSize: '0.7rem' }}>CYBER-108 (Investigator)</div>
          </div>
        </div>
      </div>
    </header>
  );
}
