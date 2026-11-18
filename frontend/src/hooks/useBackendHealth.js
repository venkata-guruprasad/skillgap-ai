import { useCallback, useEffect, useState } from 'react';
import { fetchBackendHealth, fetchDatabaseHealth } from '../services/api';

export function useBackendHealth() {
  const [apiHealth, setApiHealth] = useState({
    status: 'loading',
    message: 'Checking backend connection...',
  });
  const [dbHealth, setDbHealth] = useState({
    status: 'loading',
    database: 'checking',
    message: 'Checking database connectivity...',
  });
  const [lastChecked, setLastChecked] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const checkHealth = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const apiData = await fetchBackendHealth();
      setApiHealth(apiData);
    } catch (err) {
      setApiHealth({
        status: 'error',
        message: err?.message || 'Unable to reach SkillGap AI backend',
      });
    }

    try {
      const dbData = await fetchDatabaseHealth();
      setDbHealth(dbData);
    } catch (err) {
      setDbHealth({
        status: 'error',
        database: 'disconnected',
        message: err?.message || 'Unable to verify PostgreSQL status',
      });
    } finally {
      setLastChecked(new Date());
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  return {
    apiHealth,
    dbHealth,
    lastChecked,
    isRefreshing,
    refresh: checkHealth,
  };
}
