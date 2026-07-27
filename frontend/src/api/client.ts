// src/api/client.ts

import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const syncApi = {
  triggerSync: async () => {
    const response = await api.post('/sync');
    return response.data;
  },
};

export default api;