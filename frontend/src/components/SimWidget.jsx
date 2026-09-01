import React, { useState } from 'react';
import { Play, Zap, CheckCircle, RefreshCw } from 'lucide-react';

export default function SimWidget({
  caseId,
  onTransactionInjected,
  isSimulating,
  currentTransactions,
  currentCaseMeta
}) {
  const [amount, setAmount] = useState(35000);
  const [receiverRegion, setReceiverRegion] = useState('Mumbai');
  const [simStatus, setSimStatus] = useState(null);

  const indianCities = [
    'Mumbai', 'Delhi', 'Bengaluru', 'Hyderabad', 'Chennai', 
    'Ahmedabad', 'Pune', 'Kochi', 'Lucknow', 'Jaipur', 'Coimbatore', 'Bhubaneswar'
  ];

  const handleSimulate = async (e) => {
    e.preventDefault();
    setSimStatus('Simulating downstream hop...');

    // Pick true active terminal sender account from the latest hop
    const lastTx = currentTransactions && currentTransactions.length > 0 
      ? currentTransactions[currentTransactions.length - 1] 
      : null;

    const senderAcc = lastTx ? lastTx.receiver_account : (currentCaseMeta?.victim_account_id || `A_${caseId}_1`);
    const hopNumber = (currentTransactions?.length || 0) + 1;
    const receiverAcc = `A_${caseId}_MULE_${hopNumber}`;

    // Chronological timestamp sequentially after the previous hop (+20 mins)
    let nextTimestampStr;
    if (lastTx && lastTx.timestamp) {
      const lastDate = new Date(lastTx.timestamp);
      const nextDate = new Date(lastDate.getTime() + 20 * 60 * 1000);
      const pad = (n) => String(n).padStart(2, '0');
      nextTimestampStr = `${nextDate.getFullYear()}-${pad(nextDate.getMonth() + 1)}-${pad(nextDate.getDate())} ${pad(nextDate.getHours())}:${pad(nextDate.getMinutes())}:${pad(nextDate.getSeconds())}`;
    } else {
      nextTimestampStr = "2026-06-13 06:15:00";
    }

    const payload = {
      case_id: caseId,
      sender_account: senderAcc,
      receiver_account: receiverAcc,
      receiver_region: receiverRegion,
      amount: parseFloat(amount),
      timestamp: nextTimestampStr,
      transaction_type: 'Transfer'
    };

    try {
      await onTransactionInjected(payload);
      setSimStatus(`New transfer injected to ${receiverRegion}! Re-ranking complete.`);
      setTimeout(() => setSimStatus(null), 5000);
    } catch (err) {
      setSimStatus('Simulation failed: ' + err.message);
    }
  };

  return (
    <div className="glass-card" style={{ marginBottom: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <h2 style={{ fontSize: '1.05rem', color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Zap size={18} color="#f59e0b" /> Real-Time Evidence Simulation
        </h2>
        <span className="badge badge-medium">Live Stream</span>
      </div>

      <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.85rem' }}>
        Simulate an incoming downstream mule transfer to watch the ML model re-evaluate the case graph and update rankings dynamically without retraining:
      </p>

      <form onSubmit={handleSimulate}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem', marginBottom: '0.75rem' }}>
          <div>
            <label style={{ fontSize: '0.72rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.25rem' }}>
              TRANSFER AMOUNT (INR):
            </label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
              min="1000"
            />
          </div>
          <div>
            <label style={{ fontSize: '0.72rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.25rem' }}>
              BENEFICIARY CITY:
            </label>
            <select
              value={receiverRegion}
              onChange={(e) => setReceiverRegion(e.target.value)}
            >
              {indianCities.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        </div>

        <button
          type="submit"
          className="btn btn-warning"
          style={{ width: '100%', gap: '0.4rem' }}
          disabled={isSimulating}
        >
          {isSimulating ? <RefreshCw size={16} className="pulse-target" /> : <Play size={16} />}
          {isSimulating ? 'Evaluating Graph Dynamics...' : 'Inject New Transfer & Re-Score'}
        </button>
      </form>

      {simStatus && (
        <div style={{
          marginTop: '0.75rem',
          padding: '0.5rem 0.75rem',
          background: 'rgba(245, 158, 11, 0.15)',
          borderRadius: 'var(--radius-sm)',
          fontSize: '0.75rem',
          color: '#fbbf24',
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem'
        }}>
          <CheckCircle size={14} color="#f59e0b" />
          {simStatus}
        </div>
      )}
    </div>
  );
}
