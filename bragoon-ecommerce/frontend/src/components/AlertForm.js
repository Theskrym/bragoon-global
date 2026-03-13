import React, { useState } from 'react';
import api from '../services/api';

const AlertForm = ({ product }) => {
    const [targetPrice, setTargetPrice] = useState('');
    const [notificationType, setNotificationType] = useState('price_below');
    const [message, setMessage] = useState('');
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            await api.createAlert({
                product: product.product_ID,
                target_price: parseFloat(targetPrice),
                notification_type: notificationType
            });
            
            setMessage('Alerta criado com sucesso!');
        } catch (error) {
            setMessage('Erro ao criar alerta: ' + error.message);
        }
    };
    
    return (
        <div className="alert-form">
            <h3>Criar Alerta de Preço</h3>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>
                        Notificar-me quando:
                        <select 
                            value={notificationType}
                            onChange={(e) => setNotificationType(e.target.value)}
                        >
                            <option value="price_below">Preço ficar abaixo de</option>
                            <option value="lowest_6_months">Preço for o mais baixo em 6 meses</option>
                        </select>
                    </label>
                </div>
                
                {notificationType === 'price_below' && (
                    <div className="form-group">
                        <label>
                            Preço alvo (R$):
                            <input 
                                type="number" 
                                step="0.01"
                                min="0"
                                value={targetPrice}
                                onChange={(e) => setTargetPrice(e.target.value)}
                                required
                            />
                        </label>
                    </div>
                )}
                
                <button type="submit">Criar Alerta</button>
            </form>
            
            {message && <p className="message">{message}</p>}
        </div>
    );
};

export default AlertForm;