import React, { useState } from 'react';
import { Search, FileText, AlertCircle, IndianRupee, MapPin, Clock } from 'lucide-react';

export default function CaseSelector({ cases, selectedCaseId, onSelectCase, currentCaseMeta }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('ALL');

  const fraudTypes = ['ALL', 'Investment Fraud', 'Job Scam', 'Phishing', 'UPI Fraud'];

  const filteredCases = cases.filter(c => {
    const matchesSearch = c.case_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          c.victim_region.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'ALL' || c.fraud_type === filterType;
    return matchesSearch && matchesType;
  });

  const formatINR = (amt) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amt || 0);
  };

  return (
    <div className="glass-card" style={{ marginBottom: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <h2 style={{ fontSize: '1.05rem', color: '#93c5fd', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <FileText size={18} color="#38bdf8" /> Active Complaint Dossier
        </h2>
        <span className="badge badge-cyan">{filteredCases.length} Cases Available</span>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '0.35rem', overflowX: 'auto', paddingBottom: '0.5rem', marginBottom: '0.75rem' }}>
        {fraudTypes.map(t => (
          <button
            key={t}
            onClick={() => setFilterType(t)}
            style={{
              padding: '0.3rem 0.65rem',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.72rem',
              fontWeight: 600,
              background: filterType === t ? 'rgba(6, 182, 212, 0.25)' : 'rgba(255, 255, 255, 0.04)',
              color: filterType === t ? '#22d3ee' : 'var(--text-muted)',
              border: filterType === t ? '1px solid var(--cyan)' : '1px solid transparent',
              cursor: 'pointer',
              whiteSpace: 'nowrap'
            }}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Case Selector Dropdown */}
      <div style={{ marginBottom: '1rem' }}>
        <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '0.35rem', display: 'block' }}>
          SELECT ACTIVE CASE:
        </label>
        <select
          value={selectedCaseId}
          onChange={(e) => onSelectCase(e.target.value)}
          style={{ cursor: 'pointer', fontWeight: 600 }}
        >
          {filteredCases.map(c => (
            <option key={c.case_id} value={c.case_id}>
              {c.case_id} — {c.fraud_type} ({c.victim_region})
            </option>
          ))}
        </select>
      </div>

      {/* Dossier Card */}
      {currentCaseMeta && (
        <div style={{
          background: 'rgba(15, 23, 42, 0.9)',
          borderRadius: 'var(--radius-md)',
          padding: '1rem',
          border: '1px solid var(--border-subtle)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.85rem' }}>
            <div>
              <span className="badge badge-cyan" style={{ marginBottom: '0.35rem' }}>
                {currentCaseMeta.case_id}
              </span>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc' }}>
                {currentCaseMeta.fraud_type}
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>DISPUTED AMOUNT</div>
              <div style={{
                fontSize: '1.25rem',
                fontWeight: 800,
                background: 'linear-gradient(135deg, #38bdf8, #818cf8)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                {formatINR(currentCaseMeta.amount)}
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.78rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)' }}>
              <MapPin size={14} color="#f59e0b" />
              <span>Victim City: <strong style={{ color: '#f8fafc' }}>{currentCaseMeta.victim_region}</strong></span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)' }}>
              <Clock size={14} color="#06b6d4" />
              <span>Filing: <strong style={{ color: '#f8fafc' }}>{new Date(currentCaseMeta.complaint_time).toLocaleDateString()}</strong></span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
