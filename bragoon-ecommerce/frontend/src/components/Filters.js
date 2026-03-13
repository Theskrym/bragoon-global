import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const Filters = ({ products = [], onFilter = () => {} }) => {
  // Estados para os filtros
  const [stores, setStores] = useState([]);
  const [menus, setMenus] = useState([]);
  const [types, setTypes] = useState([]);
  
  // Estados para os valores selecionados
  const [selectedStores, setSelectedStores] = useState([]);
  const [selectedMenu, setSelectedMenu] = useState('');
  const [selectedType, setSelectedType] = useState('');

  // Extrai opções únicas dos produtos
  useEffect(() => {
    if (products.length > 0) {
      // Lojas únicas
      const uniqueStores = [...new Set(products.map(p => p.store).filter(Boolean))];
      setStores(uniqueStores);

      // Menus únicos
      const uniqueMenus = [...new Set(products.map(p => p.menu).filter(Boolean))];
      setMenus(uniqueMenus);

      // Tipos únicos (para o menu selecionado)
      if (selectedMenu) {
        const filteredTypes = products
          .filter(p => p.menu === selectedMenu)
          .map(p => p.type)
          .filter(Boolean);
        const uniqueTypes = [...new Set(filteredTypes)];
        setTypes(uniqueTypes);
      }
    }
  }, [products, selectedMenu]);

  // Aplica os filtros quando algo muda
  useEffect(() => {
    const filters = {
      selectedStores,
      selectedMenu,
      selectedType
    };
    onFilter(filters);
  }, [selectedStores, selectedMenu, selectedType, onFilter]);

  // Manipuladores de eventos
  const handleStoreToggle = (store) => {
    setSelectedStores(prev => 
      prev.includes(store)
        ? prev.filter(s => s !== store)
        : [...prev, store]
    );
  };

  const handleMenuChange = (e) => {
    setSelectedMenu(e.target.value);
    setSelectedType(''); // Reseta o tipo quando o menu muda
  };

  const handleTypeChange = (e) => {
    setSelectedType(e.target.value);
  };

  return (
    <div className="filters-sidebar">
      {/* Filtro por loja */}
      <div className="filter-group">
        <h3>Lojas</h3>
        {stores.map(store => (
          <label key={store} className="filter-option">
            <input
              type="checkbox"
              checked={selectedStores.includes(store)}
              onChange={() => handleStoreToggle(store)}
            />
            {store}
          </label>
        ))}
      </div>

      {/* Filtro por menu */}
      <div className="filter-group">
        <h3>Categorias</h3>
        <select
          value={selectedMenu}
          onChange={handleMenuChange}
          className="filter-select"
        >
          <option value="">Todas categorias</option>
          {menus.map(menu => (
            <option key={menu} value={menu}>
              {menu}
            </option>
          ))}
        </select>
      </div>

      {/* Filtro por tipo (só aparece quando um menu está selecionado) */}
      {selectedMenu && (
        <div className="filter-group">
          <h3>Tipos</h3>
          <select
            value={selectedType}
            onChange={handleTypeChange}
            className="filter-select"
          >
            <option value="">Todos os tipos</option>
            {types.map(type => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Botão para limpar todos os filtros */}
      {(selectedStores.length > 0 || selectedMenu || selectedType) && (
        <button
          onClick={() => {
            setSelectedStores([]);
            setSelectedMenu('');
            setSelectedType('');
          }}
          className="clear-filters-btn"
        >
          Limpar filtros
        </button>
      )}
    </div>
  );
};

Filters.propTypes = {
  products: PropTypes.arrayOf(
    PropTypes.shape({
      product_ID: PropTypes.string.isRequired,
      store: PropTypes.string,
      menu: PropTypes.string,
      type: PropTypes.string
    })
  ),
  onFilter: PropTypes.func
};

Filters.defaultProps = {
  products: [],
  onFilter: () => {}
};

export default Filters;