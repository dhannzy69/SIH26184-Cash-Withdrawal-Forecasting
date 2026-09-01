import React from 'react';
import { BellRing, Check, CheckCheck, MapPin } from 'lucide-react';

export default function AlertsPanel({ alerts, onAcknowledgeAlert }) {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="glass-card" style={{ padding: '1.25rem', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.8rem' }}>
        No active surveillance alerts at this time.
      </div>
    );
  }

  return (
    <div className="glass-card" style={{ marginBottom: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
        <h2 style={{ fontSize: '1.05rem', color: '#f43f5e', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <BellRing size={18} color="#f43f5e" /> Active Field Surveillance Alerts
        </h2>
        <span className="badge badge-high">{alerts.length} Dispatched</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
        {alerts.slice(0, 4).map((alert) => {
          const isAck = alert.status === 'ACKNOWLEDGED';

          return (
            <div
              key={alert.id}
              style={{
                background: isAck ? 'rgba(15, 23, 42, 0.6)' : 'rgba(244, 63, 94, 0.08)',
                border: isAck ? '1px solid var(--border-subtle)' : '1px solid rgba(244, 63, 94, 0.35)',
                borderRadius: 'var(--radius-md)',
                padding: '0.75rem 0.85rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.2rem' }}>
                  <span className="badge badge-high" style={{ fontSize: '0.65rem', padding: '0.15rem 0.45rem' }}>
                    Alert #{alert.id}
                  </span>
                  <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#f8fafc' }}>
                    Case {alert.case_id} ➔ {alert.city}
                  </span>
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  Cluster: <strong style={{ color: '#e2e8f0' }}>{alert.atm_cluster_name}</strong> | Window: <strong style={{ color: '#38bdf8' }}>{alert.estimated_time_window}</strong>
                </div>
              </div>

              <div>
                {isAck ? (
                  <span style={{ fontSize: '0.72rem', color: '#34d399', display: 'flex', alignItems: 'center', gap: '0.3rem', fontWeight: 600 }}>
                    <CheckCheck size={14} color="#10b981" /> Patrol On-Site
                  </span>
                ) : (
                  <button
                    onClick={() => onAcknowledgeAlert(alert.id)}
                    className="btn btn-ghost"
                    style={{
                      padding: '0.35rem 0.65rem',
                      fontSize: '0.72rem',
                      gap: '0.3rem',
                      borderColor: 'rgba(244, 63, 94, 0.4)',
                      color: '#f87171'
                    }}
                  >
                    <Check size={13} color="#f43f5e" /> Acknowledge
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
