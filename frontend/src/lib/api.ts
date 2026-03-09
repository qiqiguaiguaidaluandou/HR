const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RequestOptions {
  method?: string;
  body?: any;
  headers?: Record<string, string>;
}

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('token', token);
      } else {
        localStorage.removeItem('token');
      }
    }
  }

  getToken(): string | null {
    if (this.token) return this.token;
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token');
    }
    return null;
  }

  async request(endpoint: string, options: RequestOptions = {}) {
    const token = this.getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      method: options.method || 'GET',
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || 'An error occurred');
    }

    return response.json();
  }

  async login(username: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async register(username: string, email: string, password: string) {
    return this.request('/api/v1/auth/register', {
      method: 'POST',
      body: { username, email, password },
    });
  }

  async getCurrentUser() {
    return this.request('/api/v1/auth/me');
  }

  logout() {
    this.setToken(null);
  }

  async generateImages(prompt: string, aspectRatio: string, imageCount: number) {
    return this.request('/api/v1/images/generate', {
      method: 'POST',
      body: { prompt, aspect_ratio: aspectRatio, image_count: imageCount },
    });
  }

  async getImages(favoriteOnly: boolean = false) {
    return this.request(`/api/v1/images?favorite_only=${favoriteOnly}`);
  }

  async toggleFavorite(imageId: number) {
    return this.request(`/api/v1/images/${imageId}/favorite`, {
      method: 'POST',
    });
  }

  async deleteImage(imageId: number) {
    return this.request(`/api/v1/images/${imageId}`, {
      method: 'DELETE',
    });
  }
}

export const api = new ApiClient();
