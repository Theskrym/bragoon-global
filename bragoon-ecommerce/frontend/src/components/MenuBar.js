import React from 'react';
import '../styles.css';

const MenuBar = ({ filterOptions, filters, setFilters, setPagination }) => {
  const handleMenuClick = (menu) => {
    console.log('MenuBar: Menu clicked -', menu);
    setPagination(prev => ({ ...prev, currentPage: 1 }));
    setFilters(prev => ({
      ...prev,
      menu: prev.menu === menu ? '' : menu,
      type: '',
      filter: '',
      subfilter: ''
    }));
  };

  const handleTypeClick = (type) => {
    console.log('MenuBar: Type clicked -', type, '| Menu:', filters.menu);
    setPagination(prev => ({ ...prev, currentPage: 1 }));
    setFilters(prev => ({
      ...prev,
      menu: prev.menu,
      type: prev.type === type ? '' : type,
      filter: '',
      subfilter: ''
    }));
  };

  return (
    <div className="menu-bar">
      <div className="menu-items">
        {filterOptions.menus.map((menu, index) => (
          <React.Fragment key={menu}>
            <div className="menu-item">
              <span
                className={`menu-text ${filters.menu === menu ? 'active' : ''}`}
                onClick={() => handleMenuClick(menu)}
              >
                {menu}
              </span>
              {filterOptions.type[menu]?.length > 0 && (
                <div className="dropdown-menu">
                  {filterOptions.type[menu].map(type => (
                    <button
                      key={type}
                      className={`dropdown-item ${filters.type === type ? 'active' : ''}`}
                      onClick={() => handleTypeClick(type)}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {index < filterOptions.menus.length - 1 && (
              <span className="menu-separator">|</span>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

export default MenuBar;