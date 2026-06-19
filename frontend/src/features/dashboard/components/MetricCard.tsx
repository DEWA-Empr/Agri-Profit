import React from 'react';

interface MetricCardProps {
  label: string;
  value: string;
  trend: string;
  icon: React.ReactNode;
  iconBg: string;
  iconColor: string;
  trendBg: string;
  trendColor: string;
  isRevenue?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({ label, value, trend, icon, iconBg, iconColor, trendBg, trendColor, isRevenue }) => (
  <div style={{
    backgroundColor: isRevenue ? '#f0f7e8' : '#fff',
    borderRadius: '12px',
    padding: '14px',
    border: isRevenue ? '0.5px solid #c8dfa8' : '0.5px solid #e8ede4',
    display: 'flex',
    flexDirection: 'column',
    flex: 1,
    minHeight: '100px',
  }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{
        width: '32px', height: '32px', borderRadius: '9px', backgroundColor: iconBg,
        display: 'flex', alignItems: 'center', justifyContent: 'center'
      }}>
        <div style={{ color: iconColor, display: 'flex' }}>{React.cloneElement(icon as React.ReactElement<{ size?: number }>, { size: 16 })}</div>
      </div>
      <span style={{
        fontSize: '10px', fontWeight: '700', padding: '3px 8px', borderRadius: '8px',
        backgroundColor: trendBg, color: trendColor
      }}>{trend}</span>
    </div>
    <p style={{
      fontSize: '22px', fontWeight: '500', color: isRevenue ? '#27500A' : '#111',
      marginTop: '12px', letterSpacing: '-0.5px'
    }}>{value}</p>
    <p style={{ fontSize: '11px', color: '#888', marginTop: '3px' }}>{label}</p>
  </div>
);
