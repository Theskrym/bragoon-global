import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import PriceChart from '../components/PriceChart';
import AlertForm from '../components/AlertForm';
import { renderRating } from '../utils/productUtils';
import './ProductPage.css';

const ProductPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [priceData, setPriceData] = useState({
    price_history: [],
    stats: {},
    similar_products: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProductData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Busca o produto principal usando o product_id da URL
        console.log('Buscando produto com product_id:', id);
        const productResponse = await api.getProductById(id);
        if (!productResponse.data) {
          throw new Error('Produto não encontrado');
        }
        console.log('Produto carregado:', productResponse.data);
        setProduct(productResponse.data);

        // Busca o histórico de preços e produtos similares
        const priceResponse = await api.getPriceHistory(id);
        console.log('Dados de preço e similares:', priceResponse.data);
        setPriceData(priceResponse.data);

      } catch (err) {
        setError(err.message || 'Erro ao carregar detalhes do produto');
        console.error('Erro na requisição:', err);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchProductData();
    } else {
      setError('ID do produto inválido');
      setLoading(false);
    }
  }, [id]);

  if (loading) {
    return (
      <div className="product-page-loading">
        <div className="spinner"></div>
        <p>Carregando produto...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="product-page-error">
        <p>{error}</p>
        <button onClick={() => navigate(-1)}>Voltar</button>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="product-page-not-found">
        <p>Produto não encontrado</p>
        <button onClick={() => navigate('/')}>Voltar à loja</button>
      </div>
    );
  }

  return (
    <div className="product-page-container">
      <div className="product-main-info">
        <div className="product-image-container">
          <img 
            src={product.image_url || 'https://via.placeholder.com/400'} 
            alt={product.name} 
            className="product-main-image"
            onError={(e) => {
              e.target.src = 'https://via.placeholder.com/400';
            }}
          />
        </div>

        <div className="product-details">
          <h1>{product.name}</h1>
          
          <div className="product-rating">
            {renderRating(product.rating, product.review_count)}
          </div>

          <div className="product-price-section">
            <p className="current-price">R$ {parseFloat(product.price).toFixed(2)}</p>
            {priceData.stats.avg_price && (
              <p className="avg-price">
                Preço médio: R$ {parseFloat(priceData.stats.avg_price).toFixed(2)}
              </p>
            )}
          </div>

          <a 
            href={product.affiliate_link || product.product_link} 
            target="_blank" 
            rel="noopener noreferrer"
            className="buy-button"
          >
            Comprar Agora
          </a>

          <div className="product-store-info">
            <span className="store-badge">{product.store}</span>
          </div>
        </div>
      </div>

      <div className="product-secondary-info">
        <PriceChart 
          priceHistory={priceData.price_history} 
          stats={priceData.stats}
          similarProducts={priceData.similar_products}
        />

        <AlertForm productId={id} />
      </div>
    </div>
  );
};

export default ProductPage;