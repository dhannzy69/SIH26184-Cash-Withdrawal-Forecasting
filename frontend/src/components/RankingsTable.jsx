import React from 'react';
import { Target, Send, CheckCircle2 } from 'lucide-react';

export default function RankingsTable({ predictions, onDispatchAlert }) {
  if (!predictions || predictions.length === 0) {
    return (
      <div className="glass-card" style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-dim)' }}>
        Loading predictive rankings...
      </div>
    );
  }

  return (
    <div className="glass-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 style={{ fontSize: '1.05rem', color: '#93c5fd', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Target size={18} color="#38bdf8" /> Probabilistic Cash-Out Location Rankings
        </h2>
        <span className="badge badge-cyan">Model: Random Forest</span>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.84rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)', color: 'var(--text-dim)', textAlign: 'left' }}>
              <th style={{ padding: '0.6rem 0.5rem' }}>RANK</th>
              <th style={{ padding: '0.6rem 0.5rem' }}>CLUSTER / CITY</th>
              <th style={{ padding: '0.6rem 0.5rem', width: '35%' }}>MODEL LIKELIHOOD</th>
              <th style={{ padding: '0.6rem 0.5rem' }}>SURVEILLANCE RISK</th>
              <th style={{ padding: '0.6rem 0.5rem', textAlign: 'right' }}>ACTION</th>
            </tr>
          </thead>
          <tbody>
            {predictions.slice(0, 5).map((loc) => {
              const isRank1 = loc.rank === 1;
              const badgeClass = loc.risk === 'HIGH' ? 'badge-high' : (loc.risk === 'MEDIUM' ? 'badge-medium' : 'badge-low');
              const barColor = isRank1 ? 'linear-gradient(90deg, #f43f5e, #fb7185)' : (loc.risk === 'MEDIUM' ? 'linear-gradient(90deg, #f59e0b, #fbbf24)' : 'linear-gradient(90deg, #06b6d4, #38bdf8)');

              return (
                <tr
                  key={loc.location_id}
                  style={{
                    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                    background: isRank1 ? 'rgba(244, 63, 94, 0.06)' : 'transparent',
                    transition: 'var(--transition)'
                  }}
                >
                  <td style={{ padding: '0.75rem 0.5rem' }}>
                    <div style={{
                      width: '24px',
                      height: '24px',
                      borderRadius: '50%',
                      background: isRank1 ? '#f43f5e' : 'rgba(255, 255, 255, 0.08)',
                      color: isRank1 ? '#ffffff' : 'var(--text-main)',
                      fontWeight: 800,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.75rem'
                    }}>
                      {loc.rank}
                    </div>
                  </td>
                  <td style={{ padding: '0.75rem 0.5rem' }}>
                    <div style={{ fontWeight: 700, color: '#f8fafc', fontSize: '0.9rem' }}>
                      {loc.city}
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                      {loc.atm_cluster_name} ({loc.location_id})
                    </div>
                  </td>
                  <td style={{ padding: '0.75rem 0.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem', fontSize: '0.75rem' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Confidence</span>
                      <strong style={{ color: '#f8fafc' }}>{(loc.score * 100).toFixed(1)}%</strong>
                    </div>
                    <div style={{ width: '100%', height: '7px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                      <div style={{
                        width: `${Math.min(100, loc.score * 400)}%`,
                        height: '100%',
                        background: barColor,
                        borderRadius: 'var(--radius-full)'
                      }} />
                    </div>
                  </td>
                  <td style={{ padding: '0.75rem 0.5rem' }}>
                    <span className={`badge ${badgeClass}`}>
                      {loc.risk}
                    </span>
                  </td>
                  <td style={{ padding: '0.75rem 0.5rem', textAlign: 'right' }}>
                    <button
                      onClick={() => onDispatchAlert(loc)}
                      className="btn btn-ghost"
                      style={{
                        padding: '0.35rem 0.65rem',
                        fontSize: '0.72rem',
                        gap: '0.3rem'
                      }}
                    >
                      <Send size={12} color="#06b6d4" /> Alert Field
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
