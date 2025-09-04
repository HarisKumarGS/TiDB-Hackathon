// API Configuration and Services
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Utility function to get auth token
const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

// Base API request function
export const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getAuthToken();

  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    // Handle 401 Unauthorized - token expired
    if (response.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      window.location.href = '/login';
      throw new Error('Authentication required');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    // Handle empty responses
    const contentLength = response.headers.get('content-length');
    if (contentLength === '0') {
      return {} as T;
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error for ${endpoint}:`, error);
    throw error;
  }
};

// Authentication API
export const authAPI = {
  login: (credentials: { email: string; password: string }) =>
    apiRequest<{ access_token: string; user: any }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),

  register: (userData: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
  }) =>
    apiRequest<{ access_token: string; user: any }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),

  getProfile: () => apiRequest<any>('/auth/me'),

  refreshToken: () =>
    apiRequest<{ access_token: string }>('/auth/refresh', {
      method: 'POST',
    }),
};

// Products API
export const productsAPI = {
  getProducts: (params?: {
    page?: number;
    limit?: number;
    category?: string;
    search?: string;
    sortBy?: string;
    minPrice?: number;
    maxPrice?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, value.toString());
        }
      });
    }

    const queryString = searchParams.toString();
    return apiRequest<{
      products: any[];
      total: number;
      page: number;
      limit: number;
    }>(`/products${queryString ? `?${queryString}` : ''}`);
  },

  getProduct: (id: string) => apiRequest<any>(`/products/${id}`),

  searchProducts: (query: string) =>
    apiRequest<{ products: any[] }>(`/products/search?q=${encodeURIComponent(query)}`),

  getCategories: () => apiRequest<{ categories: string[] }>('/products/categories'),
};

// Cart API
export const cartAPI = {
  getCart: () => apiRequest<{ items: any[] }>('/cart'),

  addToCart: (item: { productId: string; quantity: number; variant?: string }) =>
    apiRequest<{ success: boolean }>('/cart/add', {
      method: 'POST',
      body: JSON.stringify(item),
    }),

  updateCartItem: (itemId: string, quantity: number) =>
    apiRequest<{ success: boolean }>(`/cart/update`, {
      method: 'PUT',
      body: JSON.stringify({ itemId, quantity }),
    }),

  removeFromCart: (itemId: string) =>
    apiRequest<{ success: boolean }>(`/cart/remove/${itemId}`, {
      method: 'DELETE',
    }),

  clearCart: () =>
    apiRequest<{ success: boolean }>('/cart/clear', {
      method: 'DELETE',
    }),
};

// Orders API
export const ordersAPI = {
  createOrder: (orderData: {
    items: any[];
    shippingAddress: any;
    paymentMethodId?: string;
  }) =>
    apiRequest<{ order: any; clientSecret?: string }>('/orders', {
      method: 'POST',
      body: JSON.stringify(orderData),
    }),

  getOrders: (params?: { page?: number; limit?: number }) => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }

    const queryString = searchParams.toString();
    return apiRequest<{
      orders: any[];
      total: number;
      page: number;
      limit: number;
    }>(`/orders${queryString ? `?${queryString}` : ''}`);
  },

  getOrder: (id: string) => apiRequest<{ order: any }>(`/orders/${id}`),

  updateOrderStatus: (id: string, status: string) =>
    apiRequest<{ success: boolean }>(`/orders/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    }),
};

// Payments API
export const paymentsAPI = {
  initializePayment: (orderData: {
    amount: number;
    orderId: string;
    customerEmail: string;
  }) =>
    apiRequest<{
      authorization_url: string;
      reference: string;
    }>('/payments/initialize', {
      method: 'POST',
      body: JSON.stringify(orderData),
    }),

  verifyPayment: (reference: string) =>
    apiRequest<{
      status: string;
      data: any;
    }>(`/payments/verify/${reference}`),
};