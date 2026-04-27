import { useEffect, useRef } from 'react';

export type WebSocketMessage = {
  type: string;
  data: unknown;
};

export const useWebSocket = (url: string, onMessage: (data: WebSocketMessage) => void) => {
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return () => {
      ws.current?.close();
    };
  }, [url, onMessage]);

  const send = (data: unknown) => {
    ws.current?.send(JSON.stringify(data));
  };

  return { send };
};