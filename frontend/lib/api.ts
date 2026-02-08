import axios from 'axios';
// Use /api which proxies to backend (works on both Vercel and Docker)
const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Note {
  id: number;
  video_id: string;
  url: string;
  title: string;
  content_detailed?: string;
  input_tokens?: number;
  output_tokens?: number;
  generation_cost?: number;
  created_at: string;
}

export const createNote = async (url: string, force_refresh: boolean = false): Promise<Note> => {
  const response = await api.post<Note>('/notes', { url, force_refresh });
  return response.data;
};

export const getNote = async (id: number): Promise<Note> => {
  const response = await api.get<Note>(`/notes/${id}`);
  return response.data;
};

export const listNotes = async (): Promise<Note[]> => {
  const response = await api.get<Note[]>('/notes');
  return response.data;
};
