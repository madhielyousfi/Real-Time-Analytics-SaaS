'use client';

import { useState } from 'react';

export default function SettingsPage() {
  const [appName, setAppName] = useState('');
  const [saving, setSaving] = useState(false);

  const createApp = async () => {
    if (!appName) return;
    setSaving(true);

    console.log('Creating app:', appName);

    setSaving(false);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      <div className="max-w-xl space-y-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Create New App</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">App Name</label>
              <input
                type="text"
                value={appName}
                onChange={(e) => setAppName(e.target.value)}
                className="border rounded px-3 py-2 w-full"
                placeholder="My Analytics App"
              />
            </div>
            <button
              onClick={createApp}
              disabled={saving}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? 'Creating...' : 'Create App'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}