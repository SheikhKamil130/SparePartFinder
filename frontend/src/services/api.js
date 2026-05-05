import axios from 'axios';

// Hardcoded backend URL for production deployment
const API_BASE_URL = 'https://sparepartfinder-1.onrender.com';

export const predictPart = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_BASE_URL}/api/test-predict`, formData, {
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
