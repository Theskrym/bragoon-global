import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import '../styles.css';

const Navbar = ({ resetAllFilters }) => {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMenuData = async () => {
      try {
        setLoading(false);
      } catch (error) {
        console.error("Erro ao carregar dados:", error);
        setLoading(false);
      }
    };

    fetchMenuData();
  }, []);

  if (loading) return null;

  return (
    <header>
      <div className="navbar-modular">
        <div className="navbar-left">
          <ul>
            <li><Link to="/?page=1" onClick={resetAllFilters}>Home</Link></li>
            <li><Link to="/alerts">Alertas</Link></li>
          </ul>
        </div>

        <div className="navbar-right">
          <div className="logo">
            <Link to="/" className="logo-text">BRAGOON</Link>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;