import React from 'react';
import PropTypes from 'prop-types';
import { renderRating } from '../utils/productUtils';

const ProductDetail = ({ product }) => {
  if (!product) return null;

  return (
    <div className="product-detail-card">
      <div className="product-images">
        <img 
          src={product.image_url || 'https://via.placeholder.com/400'} 
          alt={product.name} 
          className="main-image"
        />
      </div>
      
      <div className="product-info">
        <h1>{product.name || 'Nome do produto não disponível'}</h1>
        
        <div className="rating-container">
          {renderRating(product.rating, product.review_count)}
        </div>
        
        <div className="price-section">
          <span className="current-price">
            R$ {parseFloat(product.price || 0).toFixed(2)}
          </span>
        </div>
        
        <div className="store-info">
          <span className="store-badge">{product.store || 'Loja não especificada'}</span>
        </div>
        
        <a 
          href={product.affiliate_link || '#'} 
          target="_blank" 
          rel="noopener noreferrer"
          className="buy-button"
        >
          Comprar Agora
        </a>
        
        <div className="product-meta">
          <div className="meta-item">
            <span>Categoria:</span>
            <strong>{product.menu || 'Não especificada'}</strong>
          </div>
          <div className="meta-item">
            <span>Tipo:</span>
            <strong>{product.type || 'Não especificado'}</strong>
          </div>
        </div>
      </div>
    </div>
  );
};

ProductDetail.propTypes = {
  product: PropTypes.shape({
    product_id: PropTypes.string.isRequired,
    name: PropTypes.string,
    price: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    rating: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    review_count: PropTypes.number,
    store: PropTypes.string,
    image_url: PropTypes.string,
    affiliate_link: PropTypes.string,
    menu: PropTypes.string,
    type: PropTypes.string
  }).isRequired
};

export default ProductDetail;