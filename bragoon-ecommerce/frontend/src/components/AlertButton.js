// frontend/src/components/AlertButton.js
import React, { useState } from 'react';
import { createAlert } from '../services/alertService';

const AlertButton = ({ product }) => {
  const [showForm, setShowForm] = useState(false);
  const [targetPrice, setTargetPrice] = useState('');

  const handleCreateAlert = () => {
    createAlert(
      product.product_ID,
      parseFloat(targetPrice),
      'price_below'
    );
    setShowForm(false);
    setTargetPrice('');
  };

  return (
    <div className="alert-button">
      <button onClick={() => setShowForm(!showForm)}>
        Criar Alerta de Preço
      </button>
      
      {showForm && (
        <div className="alert-form">
          <input
            type="number"
            placeholder="Preço alvo"
            value={targetPrice}
            onChange={(e) => setTargetPrice(e.target.value)}
          />
          <button onClick={handleCreateAlert}>Salvar</button>
        </div>
      )}
    </div>
  );
};

export default AlertButton;