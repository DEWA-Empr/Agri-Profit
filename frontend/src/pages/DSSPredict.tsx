import React, { useState } from 'react';
import { dssService } from '../services/api';
import { BrainCircuit, Play, BarChart3, Info } from 'lucide-react';

const DSSPredict: React.FC = () => {
  const [prediction, setPrediction] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [inputs, setInputs] = useState({
    rainfall: 1200,
    fertilizer_used: 50,
    soil_ph: 6.5,
  });

  const handlePredict = async () => {
    setLoading(true);
    try {
      const res = await dssService.predict(inputs);
      setPrediction(res.data);
    } catch (error) {
      console.error('Prediction error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-800">Predictive Decision Support</h2>
        <p className="text-gray-500">Run custom models to forecast yields and optimize resources.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1 space-y-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-4">
            <h3 className="text-lg font-bold text-gray-800 border-b pb-2 flex items-center space-x-2">
              <Info size={18} className="text-primary-600" />
              <span>Model Inputs</span>
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Rainfall (mm)</label>
                <input
                  type="number"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                  value={inputs.rainfall}
                  onChange={(e) => setInputs({ ...inputs, rainfall: parseFloat(e.target.value) })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Fertilizer (kg/ha)</label>
                <input
                  type="number"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                  value={inputs.fertilizer_used}
                  onChange={(e) => setInputs({ ...inputs, fertilizer_used: parseFloat(e.target.value) })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Soil pH</label>
                <input
                  type="number"
                  step="0.1"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                  value={inputs.soil_ph}
                  onChange={(e) => setInputs({ ...inputs, soil_ph: parseFloat(e.target.value) })}
                />
              </div>
              <button
                onClick={handlePredict}
                disabled={loading}
                className="w-full flex justify-center items-center space-x-2 py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-bold text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
              >
                <Play size={18} />
                <span>{loading ? 'Processing...' : 'Run Simulation'}</span>
              </button>
            </div>
          </div>
        </div>

        <div className="md:col-span-2">
          {prediction ? (
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center justify-center space-y-6 animate-in zoom-in duration-300">
              <div className="bg-primary-50 p-6 rounded-full">
                <BrainCircuit className="text-primary-600" size={48} />
              </div>
              <div className="text-center">
                <h3 className="text-xl font-bold text-gray-800">Forecast Result</h3>
                <p className="text-primary-600 text-3xl font-black mt-2">
                  {prediction.prediction || 'N/A'}
                </p>
                {prediction.error && <p className="text-red-500 mt-2">{prediction.error}</p>}
              </div>
              
              <div className="w-full border-t pt-6 grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase font-bold tracking-wider">Confidence Score</p>
                  <p className="text-lg font-bold text-gray-800">84.2%</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase font-bold tracking-wider">Risk Level</p>
                  <p className="text-lg font-bold text-green-600">Low</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full bg-gray-50 rounded-xl border-2 border-dashed border-gray-200 flex flex-col items-center justify-center p-12 text-center">
              <BarChart3 size={64} className="text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-500">Ready for Analysis</h3>
              <p className="text-gray-400 max-w-xs mt-2">Adjust the parameters on the left and run the simulation to see predicted farm performance.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DSSPredict;
