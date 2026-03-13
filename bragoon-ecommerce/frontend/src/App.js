import React, { useState, useCallback } from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import ProductPage from './pages/ProductPage';
import AlertsPage from './pages/AlertsPage';
import './styles.css';

function App() {
  const [resetFilters, setResetFilters] = useState(() => () => {});
  const memoizedSetResetFilters = useCallback((fn) => setResetFilters(() => fn), []);

  return (
    <div className="App">
      <Navbar resetAllFilters={resetFilters} />
      <main style={{ marginTop: '80px' }}>
        <Routes>
          <Route path="/" element={<Home setResetFilters={memoizedSetResetFilters} />} />
          <Route path="/product/:id" element={<ProductPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;