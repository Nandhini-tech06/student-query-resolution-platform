import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldAlert, ArrowLeft } from 'lucide-react';

const Unauthorized = () => {
  const { user, role } = useAuth();
  const navigate = useNavigate();

  const handleGoHome = () => {
    if (role === 'ADMIN') {
      navigate('/admin/dashboard');
    } else if (role === 'STUDENT') {
      navigate('/student/dashboard');
    } else {
      navigate('/login');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card" style={{ textAlign: 'center' }}>
        <div className="auth-icon-wrapper" style={{ backgroundColor: '#fef2f2', margin: '0 auto 1.5rem auto' }}>
          <ShieldAlert size={36} color="#dc2626" />
        </div>
        <h2 style={{ color: '#991b1b' }}>403 - Access Denied</h2>
        <p style={{ marginTop: '0.5rem', color: '#4b5563' }}>
          You do not have the required permissions to access this page.
        </p>

        <div className="alert-box alert-error" style={{ margin: '1.5rem 0', textAlign: 'left' }}>
          <span>
            <strong>Current Role:</strong> {role || 'Unauthenticated'}
            <br />
            <strong>Account:</strong> {user?.email || 'None'}
            <br />
            Student and Admin access privileges are strictly separated by security policy.
          </span>
        </div>

        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <button onClick={handleGoHome} className="btn-primary">
            <ArrowLeft size={16} /> Return to Your Dashboard
          </button>
          <Link to="/login" className="btn-secondary">
            Switch Account
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Unauthorized;
