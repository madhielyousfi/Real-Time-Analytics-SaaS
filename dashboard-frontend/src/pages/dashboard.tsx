'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { LineChartComponent } from '@/components/charts/LineChart';
import { BarChartComponent } from '@/components/charts/BarChart';
import { getApps, getMetrics, getTimeseries } from '@/services/api';
import { subDays, format } from 'date-fns';

interface Stats {
  total_events: number;
  unique_users: number;
  unique_sessions: number;
  avg_session_duration_seconds: number;
}

export default function DashboardPage() {
  const [appId, setAppId] = useState('');
  const [apps, setApps] = useState<Array<{ id: string; name: string }>>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [timeseriesData, setTimeseriesData] = useState<Array<{ timestamp: string; value: number }>>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getApps().then(setApps).catch(console.error);
  }, []);

  useEffect(() => {
    if (!appId) return;
    setLoading(true);

    const startTime = subDays(new Date(), 7);
    const endTime = new Date();

    getMetrics(appId, format(startTime), format(endTime))
      .then(setStats)
      .catch(console.error);

    getTimeseries(appId, 'events', format(startTime), format(endTime), 'hour')
      .then((data) => setTimeseriesData(data.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [appId]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Select App</label>
        <select
          value={appId}
          onChange={(e) => setAppId(e.target.value)}
          className="border rounded px-3 py-2 w-64"
        >
          <option value="">Choose an app...</option>
          {apps.map((app) => (
            <option key={app.id} value={app.id}>
              {app.name}
            </option>
          ))}
        </select>
      </div>

      {loading && <p>Loading...</p>}

      {stats && (
        <div className="grid grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-sm text-gray-500">Total Events</p>
            <p className="text-2xl font-bold">{stats.total_events.toLocaleString()}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-sm text-gray-500">Unique Users</p>
            <p className="text-2xl font-bold">{stats.unique_users.toLocaleString()}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-sm text-gray-500">Unique Sessions</p>
            <p className="text-2xl font-bold">{stats.unique_sessions.toLocaleString()}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-sm text-gray-500">Avg Session Duration</p>
            <p className="text-2xl font-bold">{stats.avg_session_duration_seconds.toFixed(0)}s</p>
          </div>
        </div>
      )}

      {timeseriesData.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Events Over Time</h2>
          <LineChartComponent data={timeseriesData} />
        </div>
      )}
    </div>
  );
}