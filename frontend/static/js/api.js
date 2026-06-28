/**
 * ULTRON AI – API Integration Service
 * Standardized client connection configurations.
 */

const API_BASE_URL = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')
  ? 'http://localhost:8000/api'
  : '/api'; // Fallback to same host for deployments

class APIClient {
  static getHeaders() {
    const token = localStorage.getItem('ultron_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
  }

  static async get(endpoint) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'GET',
        headers: this.getHeaders()
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error(`GET request failed: ${endpoint}`, error);
      throw error;
    }
  }

  static async post(endpoint, data) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(data)
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error(`POST request failed: ${endpoint}`, error);
      throw error;
    }
  }

  static async upload(endpoint, formData) {
    try {
      const token = localStorage.getItem('ultron_token');
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: formData
      });
      return await this.handleResponse(response);
    } catch (error) {
      console.error(`UPLOAD request failed: ${endpoint}`, error);
      throw error;
    }
  }

  static async handleResponse(response) {
    if (response.status === 401) {
      // Automatic session logout on expired tokens
      localStorage.removeItem('ultron_token');
      localStorage.removeItem('ultron_user');
      if (!window.location.pathname.endsWith('login.html') && !window.location.pathname.endsWith('index.html') && window.location.pathname !== '/') {
        window.location.href = 'login.html';
      }
      throw new Error('Session expired. Please login again.');
    }

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'API request failed');
    }
    return data;
  }
}
