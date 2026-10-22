
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UserPlus, AlertCircle, CheckCircle } from 'lucide-react';

const departments = [
  {
    label: 'Undergraduate Programmes',
    options: [
      'Computer Science and Engineering (B.E.)',
      'Artificial Intelligence and Data Science (B.Tech.)',
      'Artificial Intelligence and Machine Learning (B.Tech.)',
      'Information Technology (B.Tech.)',
      'Electronics and Communication Engineering (B.E.)',
      'Electrical and Electronics Engineering (B.E.)',
      'Electronics and Instrumentation Engineering (B.E.)',
      'Mechanical Engineering (B.E.)',
      'Mechatronics Engineering (B.E.)',
      'Biotechnology (B.Tech.)',
      'Agricultural Engineering (B.Tech.)',
      'Aeronautical Engineering (B.E.)',
      'Automobile Engineering (B.E.)',
      'Biomedical Engineering (B.E.)',
    ],
  },
  {
    label: 'Postgraduate Programmes',
    options: [
      'Master of Business Administration (MBA)',
      'Industrial Safety Engineering (M.E.)',
    ],
  },
];

const Register = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    student_id: '',
    department: 'Computer Science and Engineering (B.E.)',
    password: '',
    confirmPassword: '',
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const email = formData.email.trim().toLowerCase();

    if (!/^[^\s@]+@nip\.ac\.in$/.test(email)) {
      setError(
        'Please use your official institute email ending with @nip.ac.in.'
      );
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    setIsLoading(true);

    try {
      await register({
        full_name: formData.full_name,
        email,
        student_id: formData.student_id,
        department: formData.department,
        password: formData.password,
      });

      setSuccess('Account created successfully! Redirecting to sign in...');

      setTimeout(() => {
        navigate('/login');
      }, 1500);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          'Registration failed. Please verify your details.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-icon-wrapper">
            <UserPlus size={26} color="#2563eb" />
          </div>

          <h2>Student Registration</h2>
          <p>
            Create an account to query university services and view history
          </p>
        </div>

        {error && (
          <div className="alert-box alert-error">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="alert-box alert-success">
            <CheckCircle size={18} />
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="full_name">Full Name</label>
            <input
              id="full_name"
              name="full_name"
              type="text"
              placeholder="e.g. Alex Morgan"
              value={formData.full_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Institute Email</label>
            <input
              id="email"
              name="email"
              type="email"
              placeholder="e.g. student@nip.ac.in"
              value={formData.email}
              onChange={handleChange}
              required
            />
            <small>Only email addresses ending with @nip.ac.in are accepted.</small>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="student_id">Student ID / Roll No</label>
              <input
                id="student_id"
                name="student_id"
                type="text"
                placeholder="e.g. STU-2026-101"
                value={formData.student_id}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="department">Department / Programme</label>
              <select
                id="department"
                name="department"
                value={formData.department}
                onChange={handleChange}
                required
              >
                {departments.map((group) => (
                  <optgroup key={group.label} label={group.label}>
                    {group.options.map((department) => (
                      <option key={department} value={department}>
                        {department}
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              placeholder="Minimum 6 characters"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              placeholder="Re-enter password"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />
          </div>

          <button
            type="submit"
            className="btn-primary-block"
            disabled={isLoading}
          >
            {isLoading ? 'Creating Account...' : 'Register as Student'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
