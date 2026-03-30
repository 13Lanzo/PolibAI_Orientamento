const API_URL = 'http://127.0.0.1:5000/chat';

export interface ChatResponse {
  response: string;
  type: 'text' | 'map' | 'options' | 'image';
  mapUrl?: string;
  mapTitle?: string;
  options?: { label: string; value: string }[];
}

export async function sendMessage(message: string): Promise<ChatResponse> {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
