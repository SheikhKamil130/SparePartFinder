export const STORAGE_KEYS = {
  THEME: 'theme',
  HISTORY: 'pro_history'
};

export const MAX_HISTORY_ITEMS = 15;

export const addToHistory = (history, newEntry) => {
  const updatedHistory = [
    { ...newEntry, timestamp: new Date().toLocaleString() },
    ...history
  ].slice(0, MAX_HISTORY_ITEMS);
  
  return updatedHistory;
};

export const deleteHistoryItem = (history, index) => {
  const updatedHistory = [...history];
  updatedHistory.splice(index, 1);
  return updatedHistory;
};

export const deleteMultipleHistoryItems = (history, indexes) => {
  const updatedHistory = [...history];
  indexes.sort((a, b) => b - a).forEach(index => {
    updatedHistory.splice(index, 1);
  });
  return updatedHistory;
};
