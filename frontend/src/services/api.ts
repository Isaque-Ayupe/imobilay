import type { ContextData } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

export interface ChatRequest {
  message: string;
  user_id?: string;
  session_id?: string;
}

export interface ChatResponse {
  response_text: string;
  context_data: ContextData;
}

export interface SessionInfo {
  id: string;
  title: string;
  timestamp: string;
  isToday?: boolean;
  isYesterday?: boolean;
}

export async function chat(req: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Falha na comunicação com o servidor');
  }

  return response.json();
}

export async function listSessions(userId: string): Promise<SessionInfo[]> {
  const response = await fetch(`${API_BASE_URL}/sessions?user_id=${userId}`);
  
  if (!response.ok) {
    throw new Error('Falha ao carregar sessões');
  }

  return response.json();
}
