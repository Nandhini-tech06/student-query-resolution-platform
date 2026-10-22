
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogIn, AlertCircle, Shield, GraduationCap } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login, getDashboardPath } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const user = await login(email, password);
      const dashboardPath = getDashboardPath(user);
      navigate(dashboardPath, { replace: true });
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          'Authentication failed. Please check your credentials.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleFillAdmin = () => {
    setEmail('');
    setPassword('');
    setError('');
  };

  const handleFillStudent = () => {
    setEmail('');
    setPassword('');
    setError('');
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-icon-wrapper">
            <LogIn size={26} color="#2563eb" />
          </div>
          <h2>Welcome Back</h2>
          <p>Sign in to access your student services or admin portal</p>
        </div>

        {error && (
          <div className="alert-box alert-error">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Institute Email</label>
            <input
              id="email"
              type="email"
              placeholder="e.g. xyz.cs24@nip.ac.in"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="btn-primary-block"
            disabled={isLoading}
          >
            {isLoading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        <div className="demo-shortcuts">
          <p className="demo-title">Account access</p>
          <div className="demo-buttons">
            <button
              type="button"
              onClick={handleFillAdmin}
              className="btn-demo btn-demo-admin"
            >
              <Shield size={14} /> Clear for Admin Login
            </button>
            <button
              type="button"
              onClick={handleFillStudent}
              className="btn-demo btn-demo-student"
            >
              <GraduationCap size={14} /> Clear for Student Login
            </button>
          </div>
        </div>

        <div className="auth-footer">
          <p>
            Are you a student without an account?{' '}
            <Link to="/register">Register here</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
