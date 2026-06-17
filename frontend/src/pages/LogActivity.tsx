import React, { useState } from 'react';
import { ledgerService } from '../services/api';
import { Save, AlertCircle } from 'lucide-react';

const LogActivity: React.FC = () => {
  const [formData, setFormData] = useState({
    activity_type: 'fertilizer',
    description: '',
    quantity: 0,
    unit: '',
    financial_data: {
      amount: 0,
      transaction_type: 'debit',
      category: 'fertilizer',
      description: '',
      tax_category: ''
    }
  });

  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  const categories = ['seed', 'fertilizer', 'labour', 'mechanization', 'yield', 'bioprocess', 'other'];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage({ text: '', type: '' });

    try {
      await ledgerService.createLog(formData);
      setMessage({ text: 'Activity logged successfully!', type: 'success' });
      // Reset form partially
      setFormData({
        ...formData,
        description: '',
        quantity: 0,
        financial_data: { ...formData.financial_data, amount: 0, description: '' }
      });
    } catch (error) {
      console.error('Error logging activity:', error);
      setMessage({ text: 'Failed to log activity. Please try again.', type: 'error' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-800">Log Farm Activity</h2>
        <p className="text-gray-500">Record daily operations and their financial impact.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-4">
          <h3 className="text-lg font-bold text-gray-800 border-b pb-2">Operational Data</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Activity Type</label>
              <select
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                value={formData.activity_type}
                onChange={(e) => setFormData({ ...formData, activity_type: e.target.value, financial_data: { ...formData.financial_data, category: e.target.value as any } })}
              >
                {categories.map(c => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Quantity</label>
              <div className="flex space-x-2">
                <input
                  type="number"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) })}
                />
                <input
                  type="text"
                  placeholder="Unit (e.g. bags)"
                  className="mt-1 block w-1/2 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                  value={formData.unit}
                  onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                />
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-4">
          <h3 className="text-lg font-bold text-gray-800 border-b pb-2">Financial Impact</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Amount (₦)</label>
              <input
                type="number"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                value={formData.financial_data.amount}
                onChange={(e) => setFormData({ ...formData, financial_data: { ...formData.financial_data, amount: parseFloat(e.target.value) } })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Transaction Type</label>
              <select
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                value={formData.financial_data.transaction_type}
                onChange={(e) => setFormData({ ...formData, financial_data: { ...formData.financial_data, transaction_type: e.target.value as any } })}
              >
                <option value="debit">Expense (Debit)</option>
                <option value="credit">Revenue (Credit)</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700">Tax Category / Note</label>
              <input
                type="text"
                placeholder="e.g. Agriculture Inputs, Sales Revenue"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
                value={formData.financial_data.tax_category}
                onChange={(e) => setFormData({ ...formData, financial_data: { ...formData.financial_data, tax_category: e.target.value } })}
              />
            </div>
          </div>
        </div>

        {message.text && (
          <div className={`p-4 rounded-lg flex items-center space-x-3 ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
            <AlertCircle size={20} />
            <span>{message.text}</span>
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-full flex justify-center items-center space-x-2 py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-bold text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 transition-all"
        >
          <Save size={20} />
          <span>{submitting ? 'Logging...' : 'Save Record'}</span>
        </button>
      </form>
    </div>
  );
};

export default LogActivity;
