import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, User as UserIcon, Shield, GraduationCap } from 'lucide-react';

const Navbar = () => {
  const { user, isAuthenticated, role, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <div className="brand-icon">
            <GraduationCap size={24} color="#2563eb" />
          </div>
          <div>
            <span className="brand-title">Student Query Platform</span>
            <span className="brand-badge">Milestone 1</span>
          </div>
        </Link>

        <nav className="navbar-nav">
          {isAuthenticated ? (
            <div className="nav-user-section">
              <div className="user-profile-badge">
                {role === 'ADMIN' ? (
                  <span className="role-tag role-admin">
                    <Shield size={13} style={{ marginRight: 4 }} /> Admin
                  </span>
                ) : (
                  <span className="role-tag role-student">
                    <UserIcon size={13} style={{ marginRight: 4 }} /> Student
                  </span>
                )}
                <span className="user-name">{user?.full_name || user?.email}</span>
              </div>
              <button onClick={handleLogout} className="btn-logout" title="Sign Out">
                <LogOut size={16} />
                <span>Logout</span>
              </button>
            </div>
          ) : (
            <div className="nav-guest-section">
              <Link to="/login" className="nav-link">Sign In</Link>
              <Link to="/register" className="btn-primary-sm">Register</Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Navbar;
