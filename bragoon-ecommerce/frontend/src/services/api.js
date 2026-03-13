import axios from 'axios';

const apiInstance = axios.create({
  baseURL: 'http://localhost:8000/api/',
  timeout: 10000,
});

// Request interceptor
apiInstance.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

const apiService = {
  getFilterOptions: async () => {
    try {
      const response = await apiInstance.get('products/filter_options/');
      return {
        success: true,
        data: {
          stores: response.data.stores || [],
          menus: response.data.menus || [],
          type: response.data.type || {},
          filter: response.data.filter || {},
          subfilter: response.data.subfilter || {}
        }
      };
    } catch (error) {
      console.error('Error fetching filter options:', error);
      return {
        success: false,
        error: error.response?.data || error.message,
        data: {
          stores: [],
          menus: [],
          type: {},
          filter: {},
          subfilter: {}
        }
      };
    }
  },

  searchProducts: async (params = {}) => {
    try {
      const response = await apiInstance.get('products/search/', {
        params: {
          page: params.page || 1,
          page_size: params.pageSize || 12,
          search: params.search || undefined,
          ordering: params.sort || undefined,
          store: params.stores?.join(',') || undefined,
          menu: params.menu || undefined,
          type: params.type || undefined,
          filter: params.filter?.join(',') || undefined,
          subfilter: params.subfilter?.join(',') || undefined
        }
      });

      const normalizedProducts = (response.data.products || []).map(product => ({
        ...product,
        product_id: product.product_ID || product.id || product._id,
        menu: product.menu || '',
        type: product.type || '',
        filter: product.filter || '',
        subfilter: product.subfilter || ''
      }));

      return {
        success: true,
        data: {
          products: normalizedProducts,
          pagination: response.data.pagination || {
            current_page: 1,
            total_pages: 1,
            total_items: 0,
            page_size: 12
          }
        }
      };
    } catch (error) {
      console.error('Error searching products:', error);
      return {
        success: false,
        error: error.response?.data || error.message,
        data: {
          products: [],
          pagination: {
            current_page: 1,
            total_pages: 1,
            total_items: 0,
            page_size: 12
          }
        }
      };
    }
  },

  getProductById: async (productId) => {
    try {
      const response = await apiInstance.get(`products/${productId}/`);
      return {
        success: true,
        data: {
          ...response.data,
          product_id: response.data.product_ID || response.data.id || response.data._id
        }
      };
    } catch (error) {
      console.error(`Error fetching product ${productId}:`, error);
      return {
        success: false,
        error: error.response?.data || error.message,
        data: null
      };
    }
  },

  getPriceHistory: async (productId) => {
    try {
      const response = await apiInstance.get(`products/${productId}/price_history/`);
      return {
        success: true,
        data: {
          price_history: response.data.price_history || [],
          stats: response.data.stats || {},
          similar_products: (response.data.similar_products || []).map(product => ({
            ...product,
            product_id: product.product_ID || product.id || product._id
          }))
        }
      };
    } catch (error) {
      console.error(`Error fetching price history for product ${productId}:`, error);
      return {
        success: false,
        error: error.response?.data || error.message,
        data: {
          price_history: [],
          stats: {},
          similar_products: []
        }
      };
    }
  },

  getAlerts: async () => {
    try {
      const response = await apiInstance.get('alerts/');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error fetching alerts:', error);
      return {
        success: false,
        error: error.response?.data || error.message,
        data: []
      };
    }
  },

  createAlert: async (productId, targetPrice) => {
    try {
      const response = await apiInstance.post('alerts/', {
        product: productId,
        target_price: targetPrice
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error creating alert:', error);
      return {
        success: false,
        error: error.response?.data || error.message
      };
    }
  },

  deleteAlert: async (alertId) => {
    try {
      await apiInstance.delete(`alerts/${alertId}/`);
      return {
        success: true
      };
    } catch (error) {
      console.error('Error deleting alert:', error);
      return {
        success: false,
        error: error.response?.data || error.message
      };
    }
  },

  checkAlert: async (alertId) => {
    try {
      const response = await apiInstance.post(`alerts/${alertId}/check_price/`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error checking alert:', error);
      return {
        success: false,
        error: error.response?.data || error.message
      };
    }
  }
};

export default apiService;