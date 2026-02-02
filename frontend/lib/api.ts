import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
  markdown_content: string;
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
