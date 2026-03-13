import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { Link } from 'react-router-dom';

const AlertsPage = () => {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const response = await api.getAlerts();
                setAlerts(response.data);
            } catch (error) {
                console.error('Erro ao buscar alertas:', error);
            } finally {
                setLoading(false);
            }
        };
        
        fetchAlerts();
    }, []);
    
    const handleDelete = async (id) => {
        try {
            await api.deleteAlert(id);
            setAlerts(alerts.filter(alert => alert.id !== id));
        } catch (error) {
            console.error('Erro ao deletar alerta:', error);
        }
    };
    
    if (loading) return <div>Carregando...</div>;
    
    return (
        <div className="alerts-page">
            <h1>Meus Alertas</h1>
            
            {alerts.length === 0 ? (
                <p>Você não tem alertas ativos.</p>
            ) : (
                <ul className="alerts-list">
                    {alerts.map(alert => (
                        <li key={alert.id} className="alert-item">
                            <div>
                                <h3>
                                    <Link to={`/product/${alert.product.product_ID}`}>
                                        {alert.product.name}
                                    </Link>
                                </h3>
                                <p>
                                    {alert.notification_type === 'price_below' 
                                        ? `Notificar quando preço ficar abaixo de R$ ${alert.target_price.toFixed(2)}`
                                        : 'Notificar quando preço for o mais baixo em 6 meses'}
                                </p>
                                <small>
                                    Criado em: {new Date(alert.created_at).toLocaleDateString()}
                                </small>
                            </div>
                            <button 
                                onClick={() => handleDelete(alert.id)}
                                className="delete-btn"
                            >
                                Remover
                            </button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default AlertsPage;