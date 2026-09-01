import React from 'react';
import { HelpCircle, TrendingUp, TrendingDown, Sparkles } from 'lucide-react';

export default function ShapExplainer({ explanation, candidateCity }) {
  if (!explanation) {
    return (
      <div className="glass-card" style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-dim)' }}>
        Loading explainability attributions...
      </div>
    );
  }

  const factors = explanation.contributing_factors || [];

  return (
    <div className="glass-card" style={{ marginBottom: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
        <h2 style={{ fontSize: '1.05rem', color: '#93c5fd', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles size={18} color="#a855f7" /> Explainable AI (SHAP Attributions)
        </h2>
        <span className="badge" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc', border: '1px solid rgba(168, 85, 247, 0.4)' }}>
          {explanation.explanation_method || 'SHAP TreeExplainer'}
        </span>
      </div>

      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
        Primary contributing factors prioritizing <strong style={{ color: '#f8fafc' }}>{explanation.city || candidateCity}</strong> as the high-risk cash-out sector:
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {factors.map((f, idx) => {
          const isIncrease = f.direction === 'INCREASES_RISK';
          const color = isIncrease ? '#f43f5e' : '#10b981';
          const sign = isIncrease ? '+' : '';
          const barWidth = Math.min(100, Math.max(15, Math.abs(f.attribution_score) * 2500));

          return (
            <div key={idx} style={{
              background: 'rgba(15, 23, 42, 0.7)',
              borderRadius: 'var(--radius-sm)',
              padding: '0.65rem 0.85rem',
              border: '1px solid rgba(255, 255, 255, 0.05)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem', fontSize: '0.78rem' }}>
                <span style={{ fontWeight: 600, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  {isIncrease ? <TrendingUp size={14} color="#f43f5e" /> : <TrendingDown size={14} color="#10b981" />}
                  {f.feature_description}
                </span>
                <span style={{ color: color, fontWeight: 700 }}>
                  {sign}{f.attribution_score}
                </span>
              </div>

              {/* Attribution Bar */}
              <div style={{ width: '100%', height: '5px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                <div style={{
                  width: `${barWidth}%`,
                  height: '100%',
                  background: color,
                  borderRadius: 'var(--radius-full)'
                }} />
              </div>
            </div>
          );
        })}
      </div>

      <div style={{
        marginTop: '0.85rem',
        fontSize: '0.7rem',
        color: 'var(--text-dim)',
        lineHeight: '1.4'
      }}>
        ℹ️ <em>SHAP explains statistical model attributions. It illustrates which topological and spatial variables drove the score without claiming direct physical causality.</em>
      </div>
    </div>
  );
}
