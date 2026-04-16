export const createAlert = (productId, targetPrice, notificationType) => {
  if (!productId || isNaN(targetPrice) || !notificationType) {
    console.error('Parâmetros inválidos para criar alerta:', { productId, targetPrice, notificationType });
    return null;
  }

  const alerts = JSON.parse(localStorage.getItem('priceAlerts')) || [];
  const newAlert = {
    id: Date.now(),
    productId,
    targetPrice: parseFloat(targetPrice),
    notificationType,
    createdAt: new Date().toISOString()
  };
  
  const updatedAlerts = [...alerts, newAlert];
  localStorage.setItem('priceAlerts', JSON.stringify(updatedAlerts));
  return newAlert;
};

export const getAlerts = () => {
  try {
    return JSON.parse(localStorage.getItem('priceAlerts')) || [];
  } catch (error) {
    console.error('Erro ao obter alertas:', error);
    return [];
  }
};

export const removeAlert = (alertId) => {
  try {
    const alerts = getAlerts().filter(alert => alert.id !== alertId);
    localStorage.setItem('priceAlerts', JSON.stringify(alerts));
    return true;
  } catch (error) {
    console.error('Erro ao remover alerta:', error);
    return false;
  }
};