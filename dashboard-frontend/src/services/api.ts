import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const setAuthToken = (token: string) => {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
};

export const getApps = async () => {
  const response = await api.get('/api/apps');
  return response.data;
};

export const getMetrics = async (appId: string, startTime: string, endTime: string) => {
  const response = await api.get(`/api/metrics/summary`, {
    params: { app_id: appId, start_time: startTime, end_time: endTime },
  });
  return response.data;
};

export const getTimeseries = async (appId: string, metricName: string, startTime: string, endTime: string, interval: string) => {
  const response = await api.post('/api/metrics/timeseries', {
    app_id: appId,
    metric_name: metricName,
    start_time: startTime,
    end_time: endTime,
    interval,
  });
  return response.data;
};

export const getEvents = async (appId: string, limit: number = 100) => {
  const response = await api.post('/api/events/query', {
    app_id: appId,
    limit,
  });
  return response.data;
};

export const getFunnel = async (appId: string, steps: string[], startTime: string, endTime: string, windowSeconds: number) => {
  const response = await api.post('/api/funnels/query', {
    app_id: appId,
    steps,
    start_time: startTime,
    end_time: endTime,
    window_seconds: windowSeconds,
  });
  return response.data;
};

export default api;