import React, { useEffect, useState } from 'react';
import { ledgerService } from '../services/api';
import { TrendingUp, TrendingDown, Wallet, ClipboardList } from 'lucide-react';

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState({ revenue: 0, expenses: 0, gross_margin: 0 });
  const [recentLogs, setRecentLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [summaryRes, logsRes] = await Promise.all([
          ledgerService.getSummary(),
          ledgerService.getLogs(),
        ]);
        setSummary(summaryRes.data);
        setRecentLogs(logsRes.data.slice(0, 5));
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(setLoading(false));
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="text-gray-500">Loading dashboard...</div>;

  const stats = [
    { name: 'Total Revenue', value: `₦${summary.revenue.toLocaleString()}`, icon: TrendingUp, color: 'text-green-600', bg: 'bg-green-100' },
    { name: 'Total Expenses', value: `₦${summary.expenses.toLocaleString()}`, icon: TrendingDown, color: 'text-red-600', bg: 'bg-red-100' },
    { name: 'Gross Margin', value: `₦${summary.gross_margin.toLocaleString()}`, icon: Wallet, color: summary.gross_margin >= 0 ? 'text-blue-600' : 'text-red-600', bg: 'bg-blue-100' },
    { name: 'Recent Activities', value: recentLogs.length, icon: ClipboardList, color: 'text-purple-600', bg: 'bg-purple-100' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-800">Farm Overview</h2>
        <p className="text-gray-500">Real-time financial and operational summary.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => (
          <div key={item.name} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
            <div className={`${item.bg} p-3 rounded-lg`}>
              <item.icon className={item.color} size={24} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">{item.name}</p>
              <p className="text-xl font-bold text-gray-900">{item.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-6 border-b border-gray-100">
          <h3 className="text-lg font-bold text-gray-800">Recent Operational Logs</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-gray-50 text-gray-500 text-xs uppercase font-medium">
              <tr>
                <th className="px-6 py-3">Activity</th>
                <th className="px-6 py-3">Quantity</th>
                <th className="px-6 py-3">Financial Impact</th>
                <th className="px-6 py-3">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {recentLogs.map((log: any) => (
                <tr key={log.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <span className="font-medium text-gray-900 capitalize">{log.activity_type}</span>
                    <p className="text-xs text-gray-500">{log.description}</p>
                  </td>
                  <td className="px-6 py-4 text-gray-600">
                    {log.quantity} {log.unit}
                  </td>
                  <td className="px-6 py-4">
                    {log.financial_transaction ? (
                      <span className={log.financial_transaction.transaction_type === 'debit' ? 'text-red-600' : 'text-green-600'}>
                        {log.financial_transaction.transaction_type === 'debit' ? '-' : '+'} ₦{log.financial_transaction.amount.toLocaleString()}
                      </span>
                    ) : (
                      <span className="text-gray-400">N/A</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-gray-500 text-sm">
                    {new Date(log.timestamp).toLocaleDateString()}
                  </td>
                </tr>
              ))}
              {recentLogs.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-gray-400">
                    No recent activities found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
