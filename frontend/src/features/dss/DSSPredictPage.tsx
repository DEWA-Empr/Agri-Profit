import { useEffect, useState, type CSSProperties } from 'react';
import axios from 'axios';
import { BrainCircuit, Play, BarChart3, Info, AlertTriangle } from 'lucide-react';
import { dssService, type DssPrediction, type DssPredictInput, type DssModelInfo } from '../../lib/apiClient';
import { colors } from '../../styles/theme';

// Human labels + bounds for the three numeric model inputs. Bounds mirror the
// backend (ml/dataset.BOUNDS) so the UI nudges users to valid ranges before
// they submit.
const FIELDS = [
  { key: 'rainfall', label: 'Rainfall (mm)', min: 300, max: 2000, step: 10 },
  { key: 'fertilizer_used', label: 'Fertilizer (kg N/ha)', min: 0, max: 120, step: 1 },
  { key: 'soil_ph', label: 'Soil pH', min: 4.5, max: 8.5, step: 0.1 },
] as const;

// Crops the model is trained on; mirrors backend schemas.DSSCrop / dataset.CROPS.
const CROPS = [
  { value: 'maize', label: 'Maize' },
  { value: 'rice', label: 'Rice' },
  { value: 'sorghum', label: 'Sorghum' },
  { value: 'soybean', label: 'Soybean' },
  { value: 'cassava', label: 'Cassava' },
] as const;

const IMPORTANCE_LABELS: Record<string, string> = {
  rainfall: 'Rainfall',
  fertilizer_used: 'Fertilizer',
  soil_ph: 'Soil pH',
  crop: 'Crop',
};

const DSSPredictPage = () => {
  const [prediction, setPrediction] = useState<DssPrediction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [inputs, setInputs] = useState<DssPredictInput>({ rainfall: 1200, fertilizer_used: 50, soil_ph: 6.5, crop: 'maize' });
  // Model quality metadata. `null` = not yet loaded, `{trained:false}` = the
  // backend has no fitted model. The two are reported differently: a load that
  // has not finished says nothing, an untrained model says so explicitly.
  const [model, setModel] = useState<DssModelInfo | null>(null);

  useEffect(() => {
    dssService.getModel()
      .then((res) => setModel(res.data))
      .catch(() => setModel({ trained: false }));
  }, []);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await dssService.predict(inputs);
      setPrediction(res.data);
    } catch (err: unknown) {
      setPrediction(null);
      const status = axios.isAxiosError(err) ? err.response?.status : undefined;
      if (status === 503) {
        setError('The model is still warming up. Try again in a moment.');
      } else if (status === 422) {
        setError('Some inputs are outside the model’s valid range. Check the fields and retry.');
      } else {
        setError('Prediction failed. Is the backend running?');
      }
    } finally {
      setLoading(false);
    }
  };

  const input: CSSProperties = { width: '100%', padding: '8px 10px', borderRadius: '7px', border: `1px solid ${colors.borderInput}`, fontSize: '12px', marginTop: '4px' };
  const label: CSSProperties = { fontSize: '11px', fontWeight: 600, color: colors.labelText };
  const card: CSSProperties = { background: colors.surface, borderRadius: '12px', border: `0.5px solid ${colors.border}`, padding: '20px' };
  const tile: CSSProperties = { background: colors.surfaceMuted, padding: '12px', borderRadius: '8px' };
  const tileLabel: CSSProperties = { fontSize: '9px', color: colors.textMuted, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' };
  const tileValue: CSSProperties = { fontSize: '15px', fontWeight: 700, color: colors.text, marginTop: '2px' };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      <div className="split-row-reverse">
        {/* Inputs */}
        <div style={card}>
          <h3 style={{ fontSize: '12px', fontWeight: 700, color: colors.text, display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '0.5px solid #eee', paddingBottom: '10px', marginBottom: '14px' }}>
            <Info size={16} color={colors.primary} /> Model Inputs
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div>
              <label style={label}>Crop</label>
              <select
                value={inputs.crop}
                onChange={(e) => setInputs({ ...inputs, crop: e.target.value })}
                style={{ ...input, cursor: 'pointer' }}
              >
                {CROPS.map((c) => (
                  <option key={c.value} value={c.value}>{c.label}</option>
                ))}
              </select>
            </div>
            {FIELDS.map((f) => (
              <div key={f.key}>
                <label style={label}>{f.label}</label>
                <input
                  type="number"
                  min={f.min}
                  max={f.max}
                  step={f.step}
                  value={inputs[f.key]}
                  onChange={(e) => setInputs({ ...inputs, [f.key]: parseFloat(e.target.value) })}
                  style={input}
                />
              </div>
            ))}
            <button
              onClick={handlePredict}
              disabled={loading}
              style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', background: colors.primaryDark, color: colors.onPrimary, padding: '11px', borderRadius: '8px', border: 'none', fontSize: '12px', fontWeight: 600, cursor: loading ? 'default' : 'pointer', opacity: loading ? 0.6 : 1, marginTop: '4px' }}
            >
              <Play size={16} /> {loading ? 'Processing…' : 'Run Prediction'}
            </button>
          </div>
        </div>

        {/* Result */}
        <div style={card}>
          {prediction ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '18px', padding: '12px 0' }}>
              <div style={{ background: colors.primarySurface, padding: '20px', borderRadius: '50%' }}><BrainCircuit size={40} color={colors.primary} /></div>
              <div style={{ textAlign: 'center' }}>
                <h3 style={{ fontSize: '15px', fontWeight: 700, color: colors.text }}>Predicted Yield</h3>
                <p style={{ fontSize: '30px', fontWeight: 800, color: colors.primaryDark, marginTop: '6px' }}>
                  {prediction.prediction} <span style={{ fontSize: '15px', fontWeight: 700, color: colors.textMuted }}>{prediction.unit}</span>
                </p>
              </div>
              <div className="grid-2" style={{ width: '100%', gap: '12px', borderTop: '0.5px solid #eee', paddingTop: '18px' }}>
                <div style={tile}>
                  <p style={tileLabel}>Confidence</p>
                  <p style={tileValue}>{prediction.confidence}%</p>
                </div>
                <div style={tile}>
                  <p style={tileLabel}>Likely range</p>
                  <p style={tileValue}>{prediction.interval.lower}–{prediction.interval.upper} {prediction.unit}</p>
                </div>
              </div>

              {/* What drives this prediction — real model feature importances. */}
              <div style={{ width: '100%' }}>
                <p style={{ ...tileLabel, marginBottom: '8px' }}>What drives this prediction</p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
                  {Object.entries(prediction.feature_importances)
                    .sort((a, b) => b[1] - a[1])
                    .map(([key, weight]) => (
                      <div key={key} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ fontSize: '11px', color: colors.textMuted, width: '74px', flexShrink: 0 }}>{IMPORTANCE_LABELS[key] ?? key}</span>
                        <div style={{ flex: 1, height: '6px', background: colors.surfaceMuted, borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ width: `${Math.round(weight * 100)}%`, height: '100%', background: colors.primary, borderRadius: '3px' }} />
                        </div>
                        <span style={{ fontSize: '11px', fontWeight: 700, color: colors.text, width: '34px', textAlign: 'right' }}>{Math.round(weight * 100)}%</span>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          ) : (
            <div style={{ minHeight: '260px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', color: colors.textFaint }}>
              {error ? <AlertTriangle size={48} color={colors.danger} style={{ marginBottom: '14px' }} /> : <BarChart3 size={48} color={colors.borderInput} style={{ marginBottom: '14px' }} />}
              <h3 style={{ fontSize: '13px', fontWeight: 600, color: error ? colors.danger : colors.textMuted }}>{error ? 'Could not predict' : 'Ready for analysis'}</h3>
              <p style={{ fontSize: '11px', maxWidth: '260px', marginTop: '6px' }}>{error ?? 'Adjust the inputs and run the model to forecast yield from rainfall, fertilizer and soil pH.'}</p>
            </div>
          )}
        </div>
      </div>

      {/* MODEL QUALITY — a property of the model, not of any one prediction, so
          it renders whether or not a forecast has been run.

          The synthetic-data disclosure sits directly beneath the two numbers on
          purpose. R² and MAE describe how well the forest fits its own held-out
          test split; that split is drawn from generated data, not from this
          farm. Placing the qualifier anywhere else on the page would let the
          numbers be read as accuracy against real harvests. */}
      <div style={card}>
        <h3 style={{ fontSize: '12px', fontWeight: 700, color: colors.text, display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '0.5px solid #eee', paddingBottom: '10px', marginBottom: '14px' }}>
          <BarChart3 size={15} color={colors.primary} /> Model quality
        </h3>

        {model === null ? (
          <p style={{ fontSize: '12px', color: colors.textMuted }}>Loading model details…</p>
        ) : !model.trained || !model.metrics ? (
          /* Untrained is stated, never rendered as blanks or zeros — a 0.0 R²
             would read as a terrible model rather than as no model. */
          <div>
            <p style={{ fontSize: '12px', fontWeight: 600, color: colors.warn }}>The model has not been trained yet.</p>
            <p style={{ fontSize: '11px', color: colors.textMuted, marginTop: '6px', lineHeight: 1.6 }}>
              No accuracy figures exist until it has been fitted. Run a forecast to train it on first use, and these
              figures will appear here.
            </p>
          </div>
        ) : (
          <>
            <div className="grid-2" style={{ gap: '12px' }}>
              <div style={tile}>
                <p style={tileLabel}>R² (coefficient of determination)</p>
                <p style={tileValue}>{model.metrics.r2.toFixed(4)}</p>
                <p style={{ fontSize: '10px', color: colors.textFaint, marginTop: '4px' }}>
                  Share of yield variation the model explains. 1.0 is perfect.
                </p>
              </div>
              <div style={tile}>
                <p style={tileLabel}>MAE (mean absolute error)</p>
                <p style={tileValue}>{model.metrics.mae.toFixed(4)} <span style={{ fontSize: '12px', fontWeight: 700, color: colors.textMuted }}>{model.target_unit ?? ''}</span></p>
                <p style={{ fontSize: '10px', color: colors.textFaint, marginTop: '4px' }}>
                  Average size of the model's error, in the target's own unit.
                </p>
              </div>
            </div>

            {/* The qualifier, immediately beside the numbers it qualifies. */}
            <div style={{ marginTop: '14px', background: 'rgba(160,92,0,0.08)', border: `0.5px solid rgba(160,92,0,0.25)`, borderRadius: '8px', padding: '11px 13px' }}>
              <p style={{ fontSize: '11px', color: colors.warn, fontWeight: 700, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
                What these figures measure
              </p>
              <p style={{ fontSize: '11.5px', color: colors.textBody, marginTop: '5px', lineHeight: 1.6 }}>
                Both are measured against a held-out split of <strong>representative synthetic data</strong>, not against
                this farm's records. The forecast model does not learn from your entries. They describe how well the model
                reproduces the agronomic response surface it was generated from — not how accurately it predicts your
                harvest.
                {model.n_samples != null && ` Trained on ${model.n_samples.toLocaleString()} generated samples.`}
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default DSSPredictPage;
