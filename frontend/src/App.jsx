import React, { useState, useEffect } from 'react';
import { api } from './services/api';
import Header from './components/Header';
import CaseSelector from './components/CaseSelector';
import MuleTimeline from './components/MuleTimeline';
import SurveillanceMap from './components/SurveillanceMap';
import RankingsTable from './components/RankingsTable';
import TimeWindowCard from './components/TimeWindowCard';
import ShapExplainer from './components/ShapExplainer';
import SimWidget from './components/SimWidget';
import AlertsPanel from './components/AlertsPanel';
import LoginGateway from './components/LoginGateway';

export default function App() {
  const [systemOnline, setSystemOnline] = useState(false);
  const [cases, setCases] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState('C0001');
  const [caseDossier, setCaseDossier] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isSimulating, setIsSimulating] = useState(false);

  // Authenticated Officer State (Restricted gatekeeper: null if no active session)
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem('sih_officer');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    return null;
  });


  const handleLogin = (user, token) => {
    setCurrentUser(user);
    localStorage.setItem('sih_officer', JSON.stringify(user));
    if (token) localStorage.setItem('sih_token', token);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('sih_officer');
    localStorage.removeItem('sih_token');
  };


  // Initial Load: Health, Cases, and Initial Alerts
  useEffect(() => {
    async function initPortal() {
      try {
        const health = await api.getHealth();
        setSystemOnline(health.status === 'healthy');

        const caseList = await api.getCases(150);
        setCases(caseList);

        const alertList = await api.getAlerts();
        setAlerts(alertList);

        await loadCaseData('C0001');
      } catch (err) {
        console.error("Portal initialization error:", err);
      } finally {
        setLoading(false);
      }
    }
    initPortal();
  }, []);

  // Fetch all dossier and prediction data for a selected case
  async function loadCaseData(caseId) {
    setSelectedCaseId(caseId);
    try {
      // 1. Fetch dossier (accounts + transactions)
      const dossier = await api.getCaseDossier(caseId);
      setCaseDossier(dossier);

      // 2. Fetch ML prediction
      const pred = await api.getPrediction(caseId);
      setPrediction(pred);

      // 3. Fetch SHAP explanation
      const expl = await api.getExplanation(caseId, 1);
      setExplanation(expl);
    } catch (err) {
      console.error(`Error loading data for case ${caseId}:`, err);
    }
  }

  // Handle Real-Time Transaction Injection (Simulation)
  async function handleTransactionInjected(payload) {
    setIsSimulating(true);
    try {
      const res = await api.injectTransaction(payload);
      // Reload updated case dossier and predictions
      await loadCaseData(payload.case_id);

      // Refresh alerts if a new alert was auto-created
      const updatedAlerts = await api.getAlerts();
      setAlerts(updatedAlerts);
    } finally {
      setIsSimulating(false);
    }
  }

  // Handle Manual Alert Dispatching
  async function handleDispatchAlert(candidateLoc) {
    try {
      const payload = {
        case_id: selectedCaseId,
        location_id: candidateLoc.location_id,
        city: candidateLoc.city,
        atm_cluster_name: candidateLoc.atm_cluster_name,
        risk_score: candidateLoc.score,
        risk_tier: candidateLoc.risk,
        estimated_time_window: prediction ? prediction.estimated_cashout_time_window : '06:00 - 07:10',
        notes: `Dispatched via Investigator Portal for ${candidateLoc.city}`
      };
      await api.dispatchAlert(payload);
      const updatedAlerts = await api.getAlerts();
      setAlerts(updatedAlerts);

    } catch (err) {
      console.error("Alert dispatch failed:", err);
    }
  }

  // Handle Alert Acknowledgment
  async function handleAcknowledgeAlert(alertId) {
    try {
      await api.acknowledgeAlert(alertId);
      const updatedAlerts = await api.getAlerts();
      setAlerts(updatedAlerts);
    } catch (err) {
      console.error("Failed to acknowledge alert:", err);
    }
  }

  const currentCaseMeta = caseDossier ? (caseDossier.case_details || caseDossier) : null;
  const currentTransactions = (caseDossier && (caseDossier.transactions || caseDossier.transaction_history)) || [];
  const currentAccounts = (caseDossier && caseDossier.accounts) || [];
  const userRole = currentUser?.role || 'INVESTIGATOR';

  // If not authenticated, enforce the Login Gateway screen
  if (!currentUser) {
    return (
      <LoginGateway
        systemOnline={systemOnline}
        onLogin={handleLogin}
      />
    );
  }

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '0.5rem 1rem 3rem 1rem' }}>
      <Header
        systemStatus={systemOnline}
        currentUser={currentUser}
        onLogin={handleLogin}
        onLogout={handleLogout}
      />


      {/* Role-Specific Command Bar */}
      {userRole === 'ADMIN' && (
        <div style={{
          background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(30, 41, 59, 0.8))',
          border: '1px solid rgba(168, 85, 247, 0.4)',
          borderRadius: 'var(--radius-md)',
          padding: '0.85rem 1.25rem',
          marginBottom: '1.25rem',
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '1rem'
        }}>
          <div>
            <div style={{ fontSize: '0.68rem', color: '#c084fc', textTransform: 'uppercase', fontWeight: 700 }}>
              CENTRAL COMMAND OVERSIGHT
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#f8fafc' }}>
              600 Total Complaints
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Across 12 States</div>
          </div>
          <div>
            <div style={{ fontSize: '0.68rem', color: '#c084fc', textTransform: 'uppercase', fontWeight: 700 }}>
              DISPUTED CAPITAL MONITORED
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#38bdf8' }}>
              ₹8.92 Crore
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Active Laundering Streams</div>
          </div>
          <div>
            <div style={{ fontSize: '0.68rem', color: '#c084fc', textTransform: 'uppercase', fontWeight: 700 }}>
              SURVEILLANCE ZONES
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#34d399' }}>
              12 ATM Clusters
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Centroid Geofences Active</div>
          </div>
          <div>
            <div style={{ fontSize: '0.68rem', color: '#c084fc', textTransform: 'uppercase', fontWeight: 700 }}>
              SYSTEM INTEGRITY
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#a78bfa' }}>
              100% Zero Leakage
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Strict Causality Enforced</div>
          </div>
        </div>
      )}

      {userRole === 'FIELD_OFFICER' && (
        <div style={{
          background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(30, 41, 59, 0.8))',
          border: '1px solid rgba(245, 158, 11, 0.4)',
          borderRadius: 'var(--radius-md)',
          padding: '0.75rem 1.25rem',
          marginBottom: '1.25rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="badge badge-medium" style={{ fontSize: '0.68rem' }}>TACTICAL PATROL MODE</span>
              <strong style={{ color: '#f8fafc', fontSize: '0.95rem' }}>Assigned Unit: FIELD-501 (Bengaluru South Division)</strong>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              Immediate priority: Acknowledge dispatched alerts and position patrol near projected ATM cash-out clusters.
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span className="badge badge-high" style={{ animation: 'pulseGlow 2s infinite' }}>
              {alerts.filter(a => a.status === 'DISPATCHED').length} URGENT ALERTS PENDING
            </span>
          </div>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem', color: '#38bdf8' }}>
          Initializing Cybercrime Predictive Surveillance Portal...
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: '420px 1fr',
          gap: '1.5rem',
          alignItems: 'start'
        }}>
          {/* LEFT COLUMN: Case Dossier, Multi-hop Chain, Simulation / Protocol */}
          <div>
            <CaseSelector
              cases={cases}
              selectedCaseId={selectedCaseId}
              onSelectCase={loadCaseData}
              currentCaseMeta={currentCaseMeta}
            />

            <MuleTimeline
              transactions={currentTransactions}
              accounts={currentAccounts}
              victimRegion={currentCaseMeta ? currentCaseMeta.victim_region : 'Unknown'}
            />

            {/* Evidence Simulation for Investigator & Admin, Tactical Protocol for Field Officer */}
            {userRole !== 'FIELD_OFFICER' ? (
              <SimWidget
                caseId={selectedCaseId}
                onTransactionInjected={handleTransactionInjected}
                isSimulating={isSimulating}
                currentTransactions={currentTransactions}
                currentCaseMeta={currentCaseMeta}
              />
            ) : (
              <div className="glass-card" style={{
                background: 'rgba(15, 23, 42, 0.85)',
                border: '1px solid rgba(245, 158, 11, 0.3)',
                marginBottom: '1.25rem'
              }}>
                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fbbf24', marginBottom: '0.5rem' }}>
                  📋 Standard Field Interception Protocol
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
                  1. <strong>Arrive at Cluster:</strong> Establish perimeter surveillance around primary ATM vestibule.<br />
                  2. <strong>Acknowledge Alert:</strong> Click "Acknowledge" on the alert panel to log unit arrival.<br />
                  3. <strong>Observe Suspects:</strong> Flag repeated card swipes or multi-card withdrawals during projected time window.<br />
                  4. <strong>Detain & Notify:</strong> Contact Cyber Operations if suspect is apprehended with cash evidence.
                </div>
              </div>
            )}
          </div>

          {/* RIGHT COLUMN: Map, Projected Time Window, Top-K Rankings, SHAP, Alerts */}
          <div>
            {/* Field Officer: Alerts pinned to the very top */}
            {userRole === 'FIELD_OFFICER' && (
              <div style={{ marginBottom: '1.25rem' }}>
                <AlertsPanel
                  alerts={alerts}
                  onAcknowledgeAlert={handleAcknowledgeAlert}
                />
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '0.25rem' }}>
              <TimeWindowCard
                timeWindow={prediction ? prediction.estimated_cashout_time_window : null}
                predictionTime={prediction ? prediction.prediction_time : null}
                txCount={prediction ? prediction.observed_transactions_count : null}
              />

              <SurveillanceMap
                candidateLocations={prediction ? prediction.top_5 : []}
                victimCity={currentCaseMeta ? currentCaseMeta.victim_region : null}
                currentMuleCity={currentTransactions?.length > 0 ? currentTransactions[currentTransactions.length - 1].receiver_account : null}
              />

              <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '1.25rem' }}>
                <RankingsTable
                  predictions={prediction ? prediction.all_ranked_locations : []}
                  onDispatchAlert={handleDispatchAlert}
                />

                <ShapExplainer
                  explanation={explanation}
                  candidateCity={prediction && prediction.top_1 ? prediction.top_1[0].city : 'Target Sector'}
                />
              </div>

              {/* Investigator and Admin: Alerts at bottom */}
              {userRole !== 'FIELD_OFFICER' && (
                <div style={{ marginTop: '1.25rem' }}>
                  <AlertsPanel
                    alerts={alerts}
                    onAcknowledgeAlert={handleAcknowledgeAlert}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

