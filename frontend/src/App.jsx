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

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '0.5rem 1rem 3rem 1rem' }}>
      <Header systemStatus={systemOnline} />

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
          {/* LEFT COLUMN: Case Dossier, Multi-hop Chain, Simulation */}
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

            <SimWidget
              caseId={selectedCaseId}
              onTransactionInjected={handleTransactionInjected}
              isSimulating={isSimulating}
            />
          </div>

          {/* RIGHT COLUMN: Map, Projected Time Window, Top-K Rankings, SHAP, Alerts */}
          <div>
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

              <div style={{ marginTop: '1.25rem' }}>
                <AlertsPanel
                  alerts={alerts}
                  onAcknowledgeAlert={handleAcknowledgeAlert}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
