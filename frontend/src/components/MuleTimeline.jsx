import React from 'react';
import { GitCommit, ArrowRight, CornerDownRight, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function MuleTimeline({ transactions, accounts, victimRegion }) {
  if (!transactions || transactions.length === 0) {
    return (
      <div className="glass-card" style={{ marginBottom: '1.25rem', textAlign: 'center', padding: '1.5rem', color: 'var(--text-dim)' }}>
        No transactions recorded yet for this case.
      </div>
    );
  }

  // Build account region map
  const accountRegionMap = {};
  (accounts || []).forEach(acc => {
    accountRegionMap[acc.account_id] = {
      type: acc.account_type,
      region: acc.region
    };
  });

  const formatINR = (amt) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amt);

  return (
    <div className="glass-card" style={{ marginBottom: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 style={{ fontSize: '1.05rem', color: '#93c5fd', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <GitCommit size={18} color="#38bdf8" /> Multi-Hop Mule Laundering Chain
        </h2>
        <span className="badge badge-medium">
          {transactions.length} Hops Detected
        </span>
      </div>

      <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
        Directed money flow tracing fund dissipation through intermediate mule accounts prior to ATM withdrawal:
      </p>

      <div style={{ position: 'relative', paddingLeft: '1.25rem' }}>
        {/* Vertical timeline line */}
        <div style={{
          position: 'absolute',
          left: '7px',
          top: '10px',
          bottom: '10px',
          width: '2px',
          background: 'linear-gradient(to bottom, #10b981, #06b6d4, #f43f5e)'
        }} />

        {/* Initial Victim Node */}
        <div style={{ position: 'relative', marginBottom: '1rem' }}>
          <div style={{
            position: 'absolute',
            left: '-1.25rem',
            top: '4px',
            width: '16px',
            height: '16px',
            borderRadius: '50%',
            background: '#10b981',
            border: '3px solid #070a12',
            boxShadow: '0 0 10px rgba(16, 185, 129, 0.6)'
          }} />
          <div style={{
            background: 'rgba(16, 185, 129, 0.08)',
            border: '1px solid rgba(16, 185, 129, 0.25)',
            borderRadius: 'var(--radius-md)',
            padding: '0.6rem 0.85rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
              <span style={{ fontWeight: 700, color: '#34d399' }}>Origin: Victim Account</span>
              <span style={{ color: 'var(--text-dim)' }}>City: <strong style={{ color: '#f8fafc' }}>{victimRegion}</strong></span>
            </div>
          </div>
        </div>

        {/* Transaction Hops */}
        {transactions.map((tx, idx) => {
          const isTerminal = idx === transactions.length - 1;
          const recvInfo = accountRegionMap[tx.receiver_account] || {};
          const recvRegion = recvInfo.region || 'Unknown';

          return (
            <div key={tx.transaction_id || idx} style={{ position: 'relative', marginBottom: '1rem' }}>
              {/* Hop Marker */}
              <div style={{
                position: 'absolute',
                left: '-1.25rem',
                top: '6px',
                width: '16px',
                height: '16px',
                borderRadius: '50%',
                background: isTerminal ? '#f43f5e' : '#06b6d4',
                border: '3px solid #070a12',
                boxShadow: isTerminal ? '0 0 12px rgba(244, 63, 94, 0.8)' : 'none'
              }} className={isTerminal ? 'pulse-target' : ''} />

              <div style={{
                background: isTerminal ? 'rgba(244, 63, 94, 0.08)' : 'rgba(15, 23, 42, 0.85)',
                border: isTerminal ? '1px solid rgba(244, 63, 94, 0.35)' : '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '0.65rem 0.85rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem' }}>
                    <span style={{ fontWeight: 700, color: isTerminal ? '#fb7185' : '#38bdf8' }}>
                      Hop {idx + 1}:
                    </span>
                    <span style={{ color: 'var(--text-muted)' }}>{tx.sender_account}</span>
                    <ArrowRight size={13} color="var(--text-dim)" />
                    <strong style={{ color: '#f8fafc' }}>{tx.receiver_account}</strong>
                  </div>
                  <span style={{ fontWeight: 800, color: '#f8fafc', fontSize: '0.85rem' }}>
                    {formatINR(tx.amount)}
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                  <span>Beneficiary City: <strong style={{ color: '#e2e8f0' }}>{recvRegion}</strong></span>
                  <span>{new Date(tx.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>

                {isTerminal && (
                  <div style={{
                    marginTop: '0.4rem',
                    padding: '0.35rem 0.5rem',
                    background: 'rgba(244, 63, 94, 0.15)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.7rem',
                    color: '#fda4af',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem'
                  }}>
                    <AlertTriangle size={13} color="#f43f5e" />
                    <strong>Terminal Active Mule:</strong> Funds currently held here. Awaiting ATM cash-out.
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
