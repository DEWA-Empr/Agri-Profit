import React, { useEffect, useState } from 'react';
import { equipmentService } from '../services/api';
import { Tractor, Wrench, Plus, Calendar, Hash } from 'lucide-react';

const Equipment: React.FC = () => {
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newEq, setNewEq] = useState({ name: '', model: '', purchase_price: 0, depreciation_rate: 10 });

  useEffect(() => {
    fetchEquipment();
  }, []);

  const fetchEquipment = async () => {
    try {
      const res = await equipmentService.getEquipment();
      setEquipment(res.data);
    } catch (error) {
      console.error('Error fetching equipment:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddEquipment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await equipmentService.createEquipment(newEq);
      setShowAddForm(false);
      fetchEquipment();
      setNewEq({ name: '', model: '', purchase_price: 0, depreciation_rate: 10 });
    } catch (error) {
      console.error('Error adding equipment:', error);
    }
  };

  if (loading) return <div className="text-gray-500">Loading equipment...</div>;

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Mechanization & Equipment</h2>
          <p className="text-gray-500">Manage farm machinery and maintenance schedules.</p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg font-bold hover:bg-primary-700 transition-all"
        >
          <Plus size={20} />
          <span>Add Equipment</span>
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleAddEquipment} className="bg-white p-6 rounded-xl shadow-sm border border-primary-100 grid grid-cols-1 md:grid-cols-4 gap-4 items-end animate-in fade-in duration-300">
          <div className="md:col-span-1">
            <label className="block text-sm font-medium text-gray-700">Name</label>
            <input
              type="text"
              required
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
              value={newEq.name}
              onChange={(e) => setNewEq({ ...newEq, name: e.target.value })}
            />
          </div>
          <div className="md:col-span-1">
            <label className="block text-sm font-medium text-gray-700">Model/Year</label>
            <input
              type="text"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
              value={newEq.model}
              onChange={(e) => setNewEq({ ...newEq, model: e.target.value })}
            />
          </div>
          <div className="md:col-span-1">
            <label className="block text-sm font-medium text-gray-700">Price (₦)</label>
            <input
              type="number"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 border"
              value={newEq.purchase_price}
              onChange={(e) => setNewEq({ ...newEq, purchase_price: parseFloat(e.target.value) })}
            />
          </div>
          <button type="submit" className="bg-primary-600 text-white p-2 rounded-md font-bold hover:bg-primary-700">
            Save
          </button>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {equipment.map((item: any) => (
          <div key={item.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-4 hover:border-primary-200 transition-colors group">
            <div className="flex justify-between items-start">
              <div className="bg-primary-50 p-3 rounded-lg group-hover:bg-primary-100 transition-colors">
                <Tractor className="text-primary-600" size={24} />
              </div>
              <span className="text-xs font-bold bg-gray-100 text-gray-500 px-2 py-1 rounded">ID: {item.id}</span>
            </div>
            
            <div>
              <h3 className="text-lg font-bold text-gray-800">{item.name}</h3>
              <p className="text-sm text-gray-500">{item.model || 'No model info'}</p>
            </div>

            <div className="grid grid-cols-2 gap-2 text-sm border-t border-b py-3 border-gray-50">
              <div className="flex items-center space-x-2 text-gray-600">
                <Calendar size={14} />
                <span>₦{item.purchase_price?.toLocaleString()}</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-600">
                <Hash size={14} />
                <span>{item.depreciation_rate}% Dep.</span>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <button className="flex items-center space-x-2 text-primary-600 font-medium hover:underline">
                <Wrench size={16} />
                <span>Maintenance</span>
              </button>
              <span className="text-xs text-gray-400">Healthy</span>
            </div>
          </div>
        ))}
        {equipment.length === 0 && (
          <div className="md:col-span-3 py-12 text-center bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
            <Tractor size={48} className="mx-auto text-gray-300 mb-4" />
            <p className="text-gray-500 font-medium">No equipment found. Start by adding your first machine.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Equipment;
