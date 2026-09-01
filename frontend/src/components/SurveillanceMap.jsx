import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { Map, Layers } from 'lucide-react';

export default function SurveillanceMap({ candidateLocations, victimCity, currentMuleCity }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layerGroupRef = useRef(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Initialize map once
    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        zoomControl: true,
        attributionControl: false
      }).setView([20.5937, 78.9629], 5);

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19
      }).addTo(map);

      mapInstanceRef.current = map;
      layerGroupRef.current = L.layerGroup().addTo(map);
    }

    const map = mapInstanceRef.current;
    const layers = layerGroupRef.current;
    layers.clearLayers();

    if (!candidateLocations || candidateLocations.length === 0) return;

    const bounds = L.latLngBounds([]);

    // 1. Render Top-5 Predicted ATM Clusters
    candidateLocations.slice(0, 5).forEach((loc) => {
      const latLng = [loc.latitude, loc.longitude];
      bounds.extend(latLng);

      const isRank1 = loc.rank === 1;
      const isTop3 = loc.rank <= 3;
      const color = isRank1 ? '#f43f5e' : (isTop3 ? '#f59e0b' : '#06b6d4');
      const radius = isRank1 ? 16 : (isTop3 ? 12 : 9);

      const circle = L.circleMarker(latLng, {
        radius: radius,
        fillColor: color,
        color: '#ffffff',
        weight: isRank1 ? 3 : 2,
        opacity: 1,
        fillOpacity: isRank1 ? 0.95 : 0.8
      }).addTo(layers);

      const popupContent = `
        <div style="font-family: 'Inter', sans-serif; min-width: 180px;">
          <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 800; color: ${color}; margin-bottom: 2px;">
            ${isRank1 ? '🚨 PRIMARY SURVEILLANCE SECTOR' : `SECTOR RANK #${loc.rank}`}
          </div>
          <div style="font-size: 1.05rem; font-weight: 700; color: #f8fafc;">
            ${loc.city}
          </div>
          <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 6px;">
            ${loc.atm_cluster_name}
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.8rem; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 6px;">
            <span>Likelihood Score:</span>
            <strong style="color: ${color};">${(loc.score * 100).toFixed(1)}%</strong>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
            <span>Risk Tier:</span>
            <strong style="color: ${color};">${loc.risk}</strong>
          </div>
        </div>
      `;
      circle.bindPopup(popupContent);

      if (isRank1) {
        circle.openPopup();
      }
    });

    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 7 });
    }

  }, [candidateLocations, victimCity, currentMuleCity]);

  return (
    <div className="glass-card" style={{ marginBottom: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
        <h2 style={{ fontSize: '1.05rem', color: '#93c5fd', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Map size={18} color="#38bdf8" /> Geospatial Surveillance & ATM Cluster Map
        </h2>
        <div style={{ display: 'flex', gap: '0.75rem', fontSize: '0.72rem' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: '#fb7185' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f43f5e' }}></span>
            Rank 1 (Primary)
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: '#fbbf24' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b' }}></span>
            Rank 2-3 (Secondary)
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: '#22d3ee' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#06b6d4' }}></span>
            Rank 4-5
          </span>
        </div>
      </div>

      <div
        ref={mapContainerRef}
        style={{
          height: '420px',
          width: '100%',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)'
        }}
      />
    </div>
  );
}
