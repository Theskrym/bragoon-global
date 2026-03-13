import React from 'react';
import { Line } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';
import { useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';

Chart.register(...registerables);

const PriceChart = ({ priceHistory, stats, similarProducts }) => {
  const navigate = useNavigate();
  
  if (!priceHistory || !Array.isArray(priceHistory)) {
    return <div className="chart-error">Histórico de preços indisponível</div>;
  }

  // Logar similar_products para depuração
  console.log('Similar products recebidos:', similarProducts);

  const data = {
    labels: priceHistory.map(item => 
      item?.date ? new Date(item.date).toLocaleDateString() : ''
    ).filter(label => label !== ''),
    datasets: [
      {
        label: 'Histórico de Preços',
        data: priceHistory.map(item => item?.price || 0),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
        fill: false
      }
    ]
  };
  
  const options = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Histórico de Preços'
      },
    },
    scales: {
      y: {
        beginAtZero: false
      }
    }
  };

  const safeStats = stats || {
    current_price: 0,
    avg_price: 0,
    min_price: 0,
    max_price: 0
  };

  const safeSimilarProducts = Array.isArray(similarProducts) 
    ? similarProducts.filter(product => {
        const productId = product.product_id || product.id || product._id || product.productId || product.ID;
        if (!productId) {
          console.warn('Produto similar sem identificador:', product);
          return false;
        }
        return true;
      })
    : [];

  return (
    <div className="price-chart-container">
      <h2>Análise de Preços</h2>
      
      <div className="chart-stats">
        <div className="stat-item">
          <span>Preço Atual:</span>
          <strong>R$ {safeStats.current_price?.toFixed(2) || '0.00'}</strong>
        </div>
        <div className="stat-item">
          <span>Média 6 meses:</span>
          <strong>R$ {safeStats.avg_price?.toFixed(2) || '0.00'}</strong>
        </div>
        <div className="stat-item">
          <span>Mínimo:</span>
          <strong>R$ {safeStats.min_price?.toFixed(2) || '0.00'}</strong>
        </div>
        <div className="stat-item">
          <span>Máximo:</span>
          <strong>R$ {safeStats.max_price?.toFixed(2) || '0.00'}</strong>
        </div>
      </div>
      
      <div className="chart-wrapper">
        <Line data={data} options={options} />
      </div>
      
      {safeSimilarProducts.length > 0 && (
        <div className="similar-products">
          <h3>Produtos Similares</h3>
          <div className="similar-list">
            {safeSimilarProducts.slice(0, 3).map(product => {
              const productId = product.product_id || product.id || product._id || product.productId || product.ID;
              return (
                <div 
                  key={productId || Math.random()}
                  className="similar-item"
                  onClick={() => productId && navigate(`/product/${productId}`)}
                >
                  <img 
                    src={product?.image_url || 'https://via.placeholder.com/60'} 
                    alt={product?.name || 'Produto similar'} 
                    width="60" 
                    height="60" 
                  />
                  <div>
                    <p>{product?.name || 'Produto'}</p>
                    <p>
                      R$ {product?.price 
                        ? parseFloat(product.price).toFixed(2) 
                        : '0.00'}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

PriceChart.propTypes = {
  priceHistory: PropTypes.arrayOf(
    PropTypes.shape({
      date: PropTypes.string,
      price: PropTypes.number
    })
  ),
  stats: PropTypes.shape({
    current_price: PropTypes.number,
    avg_price: PropTypes.number,
    min_price: PropTypes.number,
    max_price: PropTypes.number
  }),
  similarProducts: PropTypes.arrayOf(
    PropTypes.shape({
      product_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      _id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      productId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      ID: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      name: PropTypes.string,
      price: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      image_url: PropTypes.string
    })
  )
};

PriceChart.defaultProps = {
  priceHistory: [],
  stats: {},
  similarProducts: []
};

export default PriceChart;