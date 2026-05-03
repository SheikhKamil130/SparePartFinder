import axios from 'axios';

// Use environment variable for production, empty string for development (uses Vite proxy)
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const predictPart = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_BASE_URL}/predict`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const getAnalytics = async () => {
  const response = await axios.get(`${API_BASE_URL}/api/analytics`);
  return response.data;
};

export const getParts = async () => {
  const response = await axios.get(`${API_BASE_URL}/api/parts`);
  return response.data;
};
