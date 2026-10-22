
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('sqr_user');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  });

  const [token, setToken] = useState(
    () => localStorage.getItem('sqr_token') || null
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifySession = async () => {
      if (token) {
        try {
          const profile = await authService.getCurrentUser();
          setUser(profile);
          localStorage.setItem('sqr_user', JSON.stringify(profile));
        } catch (err) {
          console.error('Session verification failed:', err);
          logout();
        }
      }

      setLoading(false);
    };

    verifySession();
  }, [token]);

  const login = async (email, password) => {
    const normalizedEmail = email.trim().toLowerCase();
    const data = await authService.login(normalizedEmail, password);

    localStorage.setItem('sqr_token', data.access_token);

    const profile = {
      id: data.user_id,
      email: data.email,
      full_name: data.full_name,
      role: String(data.role).toUpperCase(),
    };

    localStorage.setItem('sqr_user', JSON.stringify(profile));
    setToken(data.access_token);
    setUser(profile);

    return profile;
  };

  const register = async (userData) => {
    const email = userData.email.trim().toLowerCase();

    if (!/^[^\s@]+@nip\.ac\.in$/.test(email)) {
      throw new Error(
        'Please use an institute email ending with @nip.ac.in.'
      );
    }

    return await authService.register({
      ...userData,
      email,
    });
  };

  const logout = () => {
    localStorage.removeItem('sqr_token');
    localStorage.removeItem('sqr_user');
    setToken(null);
    setUser(null);
  };

  const getDashboardPath = (currentUser) => {
    if (!currentUser) return '/login';

    const role = String(currentUser.role || '').toUpperCase();

    if (role === 'ADMIN') return '/admin/dashboard';
    if (role === 'STUDENT') return '/student/dashboard';

    return '/unauthorized';
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        role: user?.role || null,
        isAuthenticated: !!token && !!user,
        loading,
        login,
        register,
        logout,
        getDashboardPath,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
};
