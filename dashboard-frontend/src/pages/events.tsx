'use client';

import { useState, useEffect } from 'react';
import { getEvents } from '@/services/api';
import { DataTable } from '@/components/tables/DataTable';
import { format } from 'date-fns';

interface Event {
  id: string;
  event_type: string;
  user_id: string | null;
  session_id: string | null;
  timestamp: string;
}

const columns = [
  { key: 'event_type', header: 'Event Type' },
  { key: 'user_id', header: 'User ID' },
  { key: 'session_id', header: 'Session ID' },
  { key: 'timestamp', header: 'Timestamp' },
];

export default function EventsPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [appId, setAppId] = useState('');

  useEffect(() => {
    if (!appId) return;
    setLoading(true);

    getEvents(appId, 100)
      .then(setEvents)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [appId]);

  const tableData = events.map((e) => ({
    ...e,
    timestamp: format(new Date(e.timestamp), 'PPp'),
  }));

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Events</h1>

      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">App ID</label>
        <input
          type="text"
          value={appId}
          onChange={(e) => setAppId(e.target.value)}
          className="border rounded px-3 py-2 w-80"
          placeholder="Enter app ID..."
        />
      </div>

      {loading && <p>Loading...</p>}

      {!loading && events.length > 0 && (
        <DataTable columns={columns} data={tableData} />
      )}
    </div>
  );
}