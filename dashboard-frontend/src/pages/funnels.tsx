'use client';

import { useState, useEffect } from 'react';
import { getFunnel } from '@/services/api';
import { BarChartComponent } from '@/components/charts/BarChart';
import { format, subDays } from 'date-fns';

interface FunnelStep {
  step_name: string;
  count: number;
  conversion_rate: number;
}

interface FunnelData {
  steps: FunnelStep[];
  overall_conversion: number;
}

export default function FunnelsPage() {
  const [funnelData, setFunnelData] = useState<FunnelData | null>(null);
  const [loading, setLoading] = useState(false);
  const [appId, setAppId] = useState('');
  const [steps, setSteps] = useState('page_view,signup,purchase');

  const fetchFunnel = async () => {
    if (!appId) return;
    setLoading(true);

    const stepList = steps.split(',').map((s) => s.trim());
    const startTime = subDays(new Date(), 30);
    const endTime = new Date();

    getFunnel(appId, stepList, format(startTime), format(endTime), 86400)
      .then(setFunnelData)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Funnels</h1>

      <div className="mb-6 space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">App ID</label>
          <input
            type="text"
            value={appId}
            onChange={(e) => setAppId(e.target.value)}
            className="border rounded px-3 py-2 w-80"
            placeholder="Enter app ID..."
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Steps (comma-separated)</label>
          <input
            type="text"
            value={steps}
            onChange={(e) => setSteps(e.target.value)}
            className="border rounded px-3 py-2 w-80"
            placeholder="page_view,signup,purchase"
          />
        </div>
        <button
          onClick={fetchFunnel}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Run Funnel Analysis
        </button>
      </div>

      {loading && <p>Loading...</p>}

      {funnelData && (
        <>
          <div className="grid grid-cols-2 gap-6 mb-8">
            {funnelData.steps.map((step, i) => (
              <div key={i} className="bg-white p-6 rounded-lg shadow">
                <p className="text-sm text-gray-500">{step.step_name}</p>
                <p className="text-2xl font-bold">{step.count.toLocaleString()}</p>
                <p className="text-sm text-gray-500">{step.conversion_rate.toFixed(1)}%</p>
              </div>
            ))}
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-4">Conversion Funnel</h2>
            <BarChartComponent
              data={funnelData.steps.map((s) => ({
                name: s.step_name,
                value: s.count,
              }))}
            />
          </div>
        </>
      )}
    </div>
  );
}