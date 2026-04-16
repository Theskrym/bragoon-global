import React from 'react';
import { useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import { renderRating } from '../utils/productUtils';

const ProductCard = ({ product, index }) => {
  const navigate = useNavigate();

  if (!product || typeof product !== 'object') {
    console.warn('Produto inválido recebido em ProductCard:', product);
    return null;
  }

  console.log('Produto em ProductCard:', product, 'Chaves:', Object.keys(product));

  const productId = product.product_id || product.product_ID || product.id || product._id ||
    product.productId || product.ID || product.item_id || product.sku ||
    product.unique_id || product.product_code;
  console.log('productId determinado:', productId, 'Índice:', index);

  const navigationId = productId || `fallback-${index}`;
  if (!productId) {
    console.warn('Identificador não encontrado no produto, usando fallback:', { product, navigationId });
  }

  const shortName = product.name && product.name.length > 50
    ? `${product.name.substring(0, 50)}...`
    : product.name || 'Produto sem nome';

  const handleClick = () => {
    console.log('Clicando no produto:', { product, navigationId });
    navigate(`/product/${navigationId}`);
  };

  return (
    <div className={`part-card ${product.isUnavailable ? 'unavailable' : ''}`} onClick={handleClick}>
      <div className="part-header">
        <h3>{shortName}</h3>
        {product.store && (
          <span className={`store-badge ${product.store.toLowerCase()}`}>
            {product.store}
          </span>
        )}
      </div>

      <div className="part-details">
        {product.image_url && (
          <img
            src={product.image_url}
            alt={shortName}
            className="product-image"
            loading="lazy"
            onError={(e) => {
              e.target.src = 'https://via.placeholder.com/150?text=Sem+Imagem';
            }}
          />
        )}

        <div className="price-rating-container">
          {product.isUnavailable ? (
            <p className="price unavailable">Indisponível</p>
          ) : (
            product.price && (
              <p className="price">
                R$ {parseFloat(product.price).toFixed(2)}
              </p>
            )
          )}
          {renderRating(product.rating, product.review_count)}
        </div>

        <button
          className={`compare-btn ${product.isUnavailable ? 'disabled' : ''}`}
          onClick={(e) => {
            e.stopPropagation();
            if (!product.isUnavailable) {
              handleClick();
            }
          }}
          disabled={product.isUnavailable}
        >
          {product.isUnavailable ? 'Indisponível' : 'Ver Detalhes'}
        </button>
      </div>
    </div>
  );
};

ProductCard.propTypes = {
  product: PropTypes.shape({
    product_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    product_ID: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    _id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    productId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    ID: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    item_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    sku: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    unique_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    product_code: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    name: PropTypes.string,
    price: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    rating: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    review_count: PropTypes.number,
    store: PropTypes.string,
    image_url: PropTypes.string,
    menu: PropTypes.string,
    type: PropTypes.string,
    filter: PropTypes.string,
    subfilter: PropTypes.string,
  }).isRequired,
  index: PropTypes.number.isRequired,
};

export default ProductCard;