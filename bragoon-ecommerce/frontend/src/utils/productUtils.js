// frontend/src/utils/productUtils.js

// Função para aplicar filtros
export const applyFilters = (products = [], filters) => {
  if (!Array.isArray(products)) return [];
  
  const { searchQuery = '', selectedStores = [], selectedMenu, selectedType } = filters;

  return products.filter(product => {
    if (!product || typeof product !== 'object') return false;

    const matchesSearch = !searchQuery || 
      (product.name && product.name.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesStore = selectedStores.length === 0 || 
      (product.store && selectedStores.includes(product.store));
    
    const matchesMenu = !selectedMenu || product.menu === selectedMenu;
    const matchesType = !selectedType || product.type === selectedType;

    return matchesSearch && matchesStore && matchesMenu && matchesType;
  });
};

// Função para ordenar produtos
export const sortProducts = (products = [], sortOrder) => {
  if (!Array.isArray(products)) return [];

  return [...products].sort((a, b) => {
    const priceA = parseFloat(a.price) || 0;
    const priceB = parseFloat(b.price) || 0;
    const ratingA = parseFloat(a.rating) || 0;
    const ratingB = parseFloat(b.rating) || 0;

    if (sortOrder === 'price_asc') return priceA - priceB;
    if (sortOrder === 'price_desc') return priceB - priceA;
    if (sortOrder === 'rating_desc') return ratingB - ratingA;
    return 0;
  });
};

// Função para renderizar avaliação
export const renderRating = (ratingValue, reviewCount) => {
  const rating = parseFloat(ratingValue) || 0;
  const fullStars = Math.floor(rating);
  const hasHalfStar = (rating - fullStars) >= 0.5;
  const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

  return (
    <div className="rating">
      {[...Array(fullStars)].map((_, i) => (
        <i key={`full-${i}`} className="fas fa-star"></i>
      ))}
      {hasHalfStar && <i className="fas fa-star-half-alt"></i>}
      {[...Array(emptyStars)].map((_, i) => (
        <i key={`empty-${i}`} className="far fa-star"></i>
      ))}
      <span>({reviewCount || 0})</span>
    </div>
  );
};