import { useState, type CSSProperties } from 'react';
import { BrainCircuit, Play, BarChart3, Info } from 'lucide-react';
import { dssService } from '../../lib/apiClient';

// Salvaged from the original pages/DSSPredict.tsx (logic preserved, restyled to
// the app's inline-style standard since Tailwind is not compiled).
const DSSPredictPage = () => {
  const [prediction, setPrediction] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [inputs, setInputs] = useState({ rainfall: 1200, fertilizer_used: 50, soil_ph: 6.5 });

  const handlePredict = async () => {
    setLoading(true);
    try {
      const res = await dssService.predict(inputs);
      setPrediction(res.data);
    } catch (err) {
      console.error('Prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  const input: CSSProperties = { width: '100%', padding: '8px 10px', borderRadius: '7px', border: '1px solid #d0d8c8', fontSize: '12px', marginTop: '4px' };
  const label: CSSProperties = { fontSize: '11px', fontWeight: 600, color: '#555' };
  const card: CSSProperties = { background: '#fff', borderRadius: '12px', border: '0.5px solid #e8ede4', padding: '20px' };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <BrainCircuit size={20} color="#639922" />
        <div>
          <h2 style={{ fontSize: '17px', fontWeight: 600, color: '#111' }}>Predictive DSS</h2>
          <p style={{ fontSize: '11px', color: '#888', marginTop: '2px' }}>Forecast yields and optimize resources from your farm data.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '18px', alignItems: 'start' }}>
        {/* Inputs */}
        <div style={card}>
          <h3 style={{ fontSize: '12px', fontWeight: 700, color: '#222', display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '0.5px solid #eee', paddingBottom: '10px', marginBottom: '14px' }}>
            <Info size={16} color="#639922" /> Model Inputs
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div>
              <label style={label}>Rainfall (mm)</label>
              <input type="number" value={inputs.rainfall} onChange={(e) => setInputs({ ...inputs, rainfall: parseFloat(e.target.value) })} style={input} />
            </div>
            <div>
              <label style={label}>Fertilizer (kg/ha)</label>
              <input type="number" value={inputs.fertilizer_used} onChange={(e) => setInputs({ ...inputs, fertilizer_used: parseFloat(e.target.value) })} style={input} />
            </div>
            <div>
              <label style={label}>Soil pH</label>
              <input type="number" step="0.1" value={inputs.soil_ph} onChange={(e) => setInputs({ ...inputs, soil_ph: parseFloat(e.target.value) })} style={input} />
            </div>
            <button
              onClick={handlePredict}
              disabled={loading}
              style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', background: '#3B6D11', color: '#EAF3DE', padding: '11px', borderRadius: '8px', border: 'none', fontSize: '12px', fontWeight: 600, cursor: loading ? 'default' : 'pointer', opacity: loading ? 0.6 : 1, marginTop: '4px' }}
            >
              <Play size={16} /> {loading ? 'Processing…' : 'Run Simulation'}
            </button>
          </div>
        </div>

        {/* Result */}
        <div style={card}>
          {prediction ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '18px', padding: '20px 0' }}>
              <div style={{ background: '#f0f7e8', padding: '20px', borderRadius: '50%' }}><BrainCircuit size={40} color="#639922" /></div>
              <div style={{ textAlign: 'center' }}>
                <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#222' }}>Forecast Result</h3>
                <p style={{ fontSize: '28px', fontWeight: 800, color: '#3B6D11', marginTop: '6px' }}>{prediction.prediction ?? 'N/A'}</p>
                {prediction.error && <p style={{ color: '#c0392b', fontSize: '12px', marginTop: '6px' }}>{prediction.error}</p>}
              </div>
              <div style={{ width: '100%', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', borderTop: '0.5px solid #eee', paddingTop: '18px' }}>
                <div style={{ background: '#fafbf8', padding: '12px', borderRadius: '8px' }}>
                  <p style={{ fontSize: '9px', color: '#888', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Confidence</p>
                  <p style={{ fontSize: '15px', fontWeight: 700, color: '#222', marginTop: '2px' }}>84.2%</p>
                </div>
                <div style={{ background: '#fafbf8', padding: '12px', borderRadius: '8px' }}>
                  <p style={{ fontSize: '9px', color: '#888', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Risk Level</p>
                  <p style={{ fontSize: '15px', fontWeight: 700, color: '#3B6D11', marginTop: '2px' }}>Low</p>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ minHeight: '260px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', color: '#aaa' }}>
              <BarChart3 size={48} color="#d0d8c8" style={{ marginBottom: '14px' }} />
              <h3 style={{ fontSize: '13px', fontWeight: 600, color: '#888' }}>Ready for Analysis</h3>
              <p style={{ fontSize: '11px', maxWidth: '240px', marginTop: '6px' }}>Adjust the parameters and run the simulation to see predicted farm performance.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DSSPredictPage;
