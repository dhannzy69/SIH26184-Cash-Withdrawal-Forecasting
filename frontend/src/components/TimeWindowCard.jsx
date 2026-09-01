import React from 'react';
import { Clock, ShieldAlert, Timer } from 'lucide-react';

export default function TimeWindowCard({ timeWindow, predictionTime, txCount }) {
  return (
    <div className="glass-card" style={{
      background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9))',
      border: '1px solid rgba(56, 189, 248, 0.3)',
      marginBottom: '1.25rem'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.65rem' }}>
        <h3 style={{ fontSize: '0.9rem', color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Timer size={16} color="#38bdf8" /> Projected Cash-Out Time Window
        </h3>
        <span className="badge badge-cyan">180m Horizon</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.75rem', marginBottom: '0.5rem' }}>
        <div style={{
          fontSize: '1.65rem',
          fontWeight: 800,
          letterSpacing: '-0.03em',
          background: 'linear-gradient(135deg, #f8fafc, #38bdf8)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          {timeWindow || 'Calculating...'}
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
        <span>Prediction Cut-off (T): <strong style={{ color: '#e2e8f0' }}>{predictionTime ? new Date(predictionTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '-'}</strong></span>
        <span>Observed Transfers at T: <strong style={{ color: '#38bdf8' }}>{txCount || 0}</strong></span>
      </div>

      <div style={{
        marginTop: '0.65rem',
        padding: '0.45rem 0.65rem',
        background: 'rgba(6, 182, 212, 0.08)',
        borderRadius: 'var(--radius-sm)',
        fontSize: '0.7rem',
        color: '#94a3b8',
        border: '1px solid rgba(6, 182, 212, 0.2)'
      }}>
        💡 <strong>Operational Window:</strong> Field surveillance teams should prioritize ATM patrols in the target sector within this high-probability window.
      </div>
    </div>
  );
}
