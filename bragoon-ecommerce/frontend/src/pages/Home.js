import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import ProductCard from '../components/ProductCard';
import MenuBar from '../components/MenuBar';
import api from '../services/api';
import '../styles.css';

const Home = ({ setResetFilters }) => {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 52
  });
  const [filterOptions, setFilterOptions] = useState({
    stores: [],
    menus: [],
    type: {},
    filter: {},
    subfilter: {}
  });
  const [filters, setFilters] = useState({
    search: '',
    stores: [],
    menu: '',
    type: '',
    filter: '',
    subfilter: '',
    sort: 'price_asc'
  });

  // Normaliza chaves para consistência
  const normalizeKey = (key) => {
    if (!key) return '';
    return key
      .toString()
      .toLowerCase()
      .replace(/\s+/g, '_')
      .replace(/[:;,.]/g, '')
      .replace(/__/g, '_');
  };

  // Função resetAllFilters envolvida em useCallback
  const resetAllFilters = useCallback(() => {
    console.log('Resetting all filters for Home click');
    setPagination({
      currentPage: 1,
      totalPages: 1,
      totalItems: 0,
      pageSize: 52
    });
    setFilters({
      search: '',
      stores: [],
      menu: '',
      type: '',
      filter: '',
      subfilter: '',
      sort: 'price_asc'
    });
    navigate('/?page=1', { replace: true });
  }, [setPagination, setFilters, navigate]);

  // Passa resetAllFilters para o componente pai
  useEffect(() => {
    setResetFilters(() => resetAllFilters);
  }, [resetAllFilters, setResetFilters]);

  // Carrega as opções de filtro disponíveis
  useEffect(() => {
    const loadFilterOptions = async () => {
      try {
        const response = await api.getFilterOptions();
        console.log('Filter Options Response:', JSON.stringify(response, null, 2));
        
        const normalizedFilter = {};
        const normalizedSubfilter = {};
        Object.keys(response.data.filter || {}).forEach(key => {
          const normalized = normalizeKey(key);
          normalizedFilter[normalized] = response.data.filter[key].map(item => item || '');
          console.log(`Filter Key Mapping: ${key} -> ${normalized}`, normalizedFilter[normalized]);
        });
        Object.keys(response.data.subfilter || {}).forEach(key => {
          const normalized = normalizeKey(key);
          normalizedSubfilter[normalized] = response.data.subfilter[key].map(item => item || '');
          console.log(`Subfilter Key Mapping: ${key} -> ${normalized}`, normalizedSubfilter[normalized]);
        });

        setFilterOptions({
          stores: response.data.stores || [],
          menus: response.data.menus || [],
          type: response.data.type || {},
          filter: normalizedFilter,
          subfilter: normalizedSubfilter
        });
        console.log('Final FilterOptions Set:', {
          stores: response.data.stores || [],
          menus: response.data.menus || [],
          type: response.data.type || {},
          filter: normalizedFilter,
          subfilter: normalizedSubfilter
        });
      } catch (err) {
        console.error('Failed to load filter options:', err);
        setFilterOptions({
          stores: [],
          menus: [],
          type: {},
          filter: {},
          subfilter: {}
        });
      }
    };
    
    loadFilterOptions();
  }, []);

  // Log para depurar filtros após cada mudança
  useEffect(() => {
    console.log('Current Filters:', filters);
    if (filters.menu && filters.type) {
      const filterKey = normalizeKey(`${filters.menu}_${filters.type}`);
      console.log('Filter Key:', filterKey);
      console.log('Available Filters:', filterOptions.filter[filterKey] || 'None');
      if (filters.filter) {
        const subfilterKey = normalizeKey(`${filters.menu}_${filters.type}_${filters.filter}`);
        console.log('Subfilter Key:', subfilterKey);
        console.log('Available Subfilters:', filterOptions.subfilter[subfilterKey] || 'None');
      }
    }
  }, [filters, filterOptions]);

  // Busca produtos quando filtros ou página mudam
  useEffect(() => {
    const searchProducts = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const result = await api.searchProducts({
          search: filters.search,
          stores: filters.stores,
          menu: filters.menu,
          type: filters.type,
          filter: filters.filter ? [filters.filter] : [],
          subfilter: filters.subfilter ? [filters.subfilter] : [],
          sort: filters.sort,
          page: pagination.currentPage,
          pageSize: pagination.pageSize
        });
        
        console.log('Search Products Response:', result);
        
        if (result.success) {
          // Processar produtos para marcar indisponíveis
          const processedProducts = (result.data.products || []).map(product => ({
            ...product,
            isUnavailable: parseFloat(product.price) === 0 || product.price === "0,00" || parseFloat(product.price) < 0
          }));
          
          console.log(`Produtos carregados: ${processedProducts.filter(p => !p.isUnavailable).length} disponíveis, ${processedProducts.filter(p => p.isUnavailable).length} indisponíveis`);
          
          setProducts(processedProducts);
          setPagination({
            currentPage: result.data.pagination.current_page || 1,
            totalPages: result.data.pagination.total_pages || 1,
            totalItems: result.data.pagination.total_items || 0,
            pageSize: result.data.pagination.page_size || 52
          });
          
          const params = new URLSearchParams();
          if (filters.search) params.set('search', filters.search);
          if (filters.stores.length) params.set('stores', filters.stores.join(','));
          if (filters.menu) params.set('menu', filters.menu);
          if (filters.type) params.set('type', filters.type);
          if (filters.filter) params.set('filter', filters.filter);
          if (filters.subfilter) params.set('subfilter', filters.subfilter);
          if (filters.sort && filters.sort !== 'price_asc') params.set('sort', filters.sort);
          params.set('page', pagination.currentPage);
          
          navigate(`/?${params.toString()}`, { replace: true });
        } else {
          throw new Error(result.error || 'Failed to load products');
        }
      } catch (err) {
        console.error('Search Error:', err);
        setError(err.message || 'Erro ao carregar produtos');
        setProducts([]);
        setPagination({
          currentPage: 1,
          totalPages: 1,
          totalItems: 0,
          pageSize: 52
        });
      } finally {
        setLoading(false);
      }
    };
    
    searchProducts();
  }, [filters, pagination.currentPage, pagination.pageSize, navigate]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const searchValue = e.target.elements.search.value.trim();
    console.log('Search Submitted:', searchValue);
    setPagination(prev => ({ ...prev, currentPage: 1 }));
    setFilters(prev => ({ ...prev, search: searchValue }));
  };

  const handleFilterChange = (filterType, value) => {
    console.log(`Filter Change - ${filterType}:`, value);
    setPagination(prev => ({ ...prev, currentPage: 1 }));
    
    setFilters(prev => {
      if (filterType === 'stores') {
        return {
          ...prev,
          stores: prev.stores.includes(value)
            ? prev.stores.filter(v => v !== value)
            : [...prev.stores, value]
        };
      } else if (filterType === 'menu') {
        return {
          ...prev,
          menu: prev.menu === value ? '' : value,
          type: '',
          filter: '',
          subfilter: ''
        };
      } else if (filterType === 'type') {
        return {
          ...prev,
          type: prev.type === value ? '' : value,
          filter: '',
          subfilter: ''
        };
      } else if (filterType === 'filter') {
        return {
          ...prev,
          filter: prev.filter === value ? '' : value,
          subfilter: ''
        };
      } else if (filterType === 'subfilter') {
        return {
          ...prev,
          subfilter: prev.subfilter === value ? '' : value
        };
      } else {
        return {
          ...prev,
          [filterType]: prev[filterType] === value ? '' : value
        };
      }
    });
  };

  const clearAllFilters = () => {
    console.log('Clearing filters and subfilters');
    setPagination(prev => ({ ...prev, currentPage: 1 }));
    setFilters(prev => ({
      ...prev,
      search: '',
      stores: [],
      filter: '',
      subfilter: ''
    }));
  };

  const getPageButtons = () => {
    const buttons = [];
    const { currentPage, totalPages } = pagination;
    const maxVisible = 5;

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        buttons.push(
          <button
            key={i}
            className={currentPage === i ? 'active' : ''}
            onClick={() => setPagination(prev => ({ ...prev, currentPage: i }))}
          >
            {i}
          </button>
        );
      }
    } else {
      const half = Math.floor(maxVisible / 2);

      if (currentPage > half + 1) {
        buttons.push(
          <button key={1} onClick={() => setPagination(prev => ({ ...prev, currentPage: 1 }))}>
            1
          </button>
        );
        if (currentPage > half + 2) {
          buttons.push(<span key="start-ellipsis">...</span>);
        }
      }

      const start = Math.max(1, currentPage - half);
      const end = Math.min(totalPages, start + maxVisible - 1);

      for (let i = start; i <= end; i++) {
        buttons.push(
          <button
            key={i}
            className={currentPage === i ? 'active' : ''}
            onClick={() => setPagination(prev => ({ ...prev, currentPage: i }))}
          >
            {i}
          </button>
        );
      }

      if (currentPage < totalPages - half) {
        if (currentPage < totalPages - half - 1) {
          buttons.push(<span key="end-ellipsis">...</span>);
        }
        buttons.push(
          <button key={totalPages} onClick={() => setPagination(prev => ({ ...prev, currentPage: totalPages }))}>
            {totalPages}
          </button>
        );
      }
    }

    console.log('Page Buttons:', buttons);
    return buttons;
  };

  if (loading && products.length === 0) {
    return (
      <div className="loading-overlay">
        <div className="spinner"></div>
        <p>Carregando produtos...</p>
      </div>
    );
  }

  return (
    <div className="home-container">
      <MenuBar
        filterOptions={filterOptions}
        filters={filters}
        setFilters={setFilters}
        setPagination={setPagination}
      />
      <div className="builder-container">
        <aside className="filters-sidebar">
          <div className="filter-group">
            <h3>Pesquisar</h3>
            <form onSubmit={handleSearchSubmit}>
              <input
                type="text"
                name="search"
                placeholder="Digite o nome do produto..."
                defaultValue={filters.search}
              />
              <button type="submit" className="search-button">
                <i className="search-icon">🔍</i>
              </button>
            </form>
          </div>

          <div className="filter-group">
            <h3>Lojas</h3>
            {filterOptions.stores.length > 0 ? (
              filterOptions.stores.map(store => (
                <label key={store} className="filter-option">
                  <input
                    type="checkbox"
                    checked={filters.stores.includes(store)}
                    onChange={() => handleFilterChange('stores', store)}
                  />
                  {store}
                </label>
              ))
            ) : (
              <p>Nenhuma loja disponível.</p>
            )}
          </div>

          {filters.menu && (
            <div className="filter-group">
              <h3>Filtros</h3>
              {console.log('Debug Filtros:', { menu: filters.menu, type: filters.type, filterKey: normalizeKey(`${filters.menu}_${filters.type}`), availableFilters: filterOptions.filter[normalizeKey(`${filters.menu}_${filters.type}`)] })}
              {filters.type && filterOptions.filter[normalizeKey(`${filters.menu}_${filters.type}`)]?.length > 0 ? (
                filterOptions.filter[normalizeKey(`${filters.menu}_${filters.type}`)].map(filter => (
                  <label key={filter} className="filter-option">
                    <input
                      type="radio"
                      name="filter"
                      checked={filters.filter === filter}
                      onChange={() => handleFilterChange('filter', filter)}
                    />
                    {filter}
                  </label>
                ))
              ) : (
                <p>Nenhum filtro disponível. {filters.menu ? `Menu: ${filters.menu}` : 'Selecione um menu.'} {filters.type ? `Type: ${filters.type}` : 'Selecione um tipo.'}</p>
              )}
            </div>
          )}

          {filters.menu && filters.type && filters.filter && (
            <div className="filter-group">
              <h3>Subfiltros</h3>
              {console.log('Debug Subfiltros:', { menu: filters.menu, type: filters.type, filter: filters.filter, filterKey: normalizeKey(`${filters.menu}_${filters.type}_${filters.filter}`), availableSubfilters: filterOptions.subfilter[normalizeKey(`${filters.menu}_${filters.type}_${filters.filter}`)] })}
              {filterOptions.subfilter[normalizeKey(`${filters.menu}_${filters.type}_${filters.filter}`)]?.length > 0 ? (
                filterOptions.subfilter[normalizeKey(`${filters.menu}_${filters.type}_${filters.filter}`)].map(subfilter => (
                  <label key={subfilter} className="filter-option">
                    <input
                      type="radio"
                      name="subfilter"
                      checked={filters.subfilter === subfilter}
                      onChange={() => handleFilterChange('subfilter', subfilter)}
                    />
                    {subfilter}
                  </label>
                ))
              ) : (
                <p>Nenhum subfiltro disponível.</p>
              )}
            </div>
          )}

          <div className="filter-group">
            <h3>Ordenar por</h3>
            <select
              value={filters.sort}
              onChange={(e) => handleFilterChange('sort', e.target.value)}
              className="filter-select"
            >
              <option value="price_asc">Preço: Menor para Maior</option>
              <option value="price_desc">Preço: Maior para Menor</option>
              <option value="rating_desc">Melhor Avaliação</option>
            </select>
          </div>

          {(filters.search || filters.stores.length || filters.menu || filters.type || filters.filter || filters.subfilter) && (
            <button onClick={clearAllFilters} className="clear-filters-btn">
              Limpar todos os filtros
            </button>
          )}
        </aside>

        <section className="parts-grid">
          <div className="parts-header">
            <h2>
              {filters.type ? 
                `${filters.type.replace(/_/g, ' ')}` : 
                filters.menu ? 
                  `${filters.menu.replace(/_/g, ' ')}` : 
                  'Todos os produtos'}
              <small>({pagination.totalItems} itens)</small>
            </h2>
            <div className="pagination-controls">
              <button
                disabled={pagination.currentPage === 1}
                onClick={() => setPagination(prev => ({ ...prev, currentPage: prev.currentPage - 1 }))}
              >
                
              </button>
              {getPageButtons()}
              <button
                disabled={pagination.currentPage >= pagination.totalPages}
                onClick={() => setPagination(prev => ({ ...prev, currentPage: prev.currentPage + 1 }))}
              >
                
              </button>
            </div>
          </div>

          {error ? (
            <div className="error-message">
              <p>{error}</p>
              <button onClick={() => window.location.reload()}>Recarregar</button>
            </div>
          ) : (
            <div id="parts-container">
              {products.length > 0 ? (
                products.map((product, index) => (
                  <ProductCard
                    key={product.product_id || `product-${index}`}
                    product={product}
                    index={index}
                  />
                ))
              ) : (
                <div className="no-results">
                  <p>Nenhum produto encontrado com os filtros atuais.</p>
                  <button onClick={clearAllFilters}>
                    Limpar todos os filtros
                  </button>
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default Home;