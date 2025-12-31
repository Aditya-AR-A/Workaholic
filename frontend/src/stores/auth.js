import { defineStore } from 'pinia';
import api from '../api/axios';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
  }),
  actions: {
    async login(credentials) {
      // In a real app, you would POST to /api/login/ or similar
      // Here we simulate it or use Basic Auth
      try {
        // const response = await api.post('/login/', credentials);
        this.user = { username: credentials.username };
        this.isAuthenticated = true;
      } catch (error) {
        throw error;
      }
    },
    logout() {
      this.user = null;
      this.isAuthenticated = false;
    }
  },
});
