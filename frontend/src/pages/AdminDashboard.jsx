import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { systemService, authService, adminKnowledgeService } from '../services/api';
import {
  Shield,
  UploadCloud,
  FileText,
  Archive,
  Database,
  Globe,
  ThumbsUp,
  Activity,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Layers,
  Server,
  Plus,
  Trash2,
  Edit3,
  Search,
  X,
  Check,
  RotateCcw
} from 'lucide-react';

const CATEGORIES = [
  'academics',
  'examinations',
  'fees',
  'hostel',
  'library',
  'placements',
  'certificates',
  'transport',
  'admissions',
  'rules',
  'general'
];

const AdminDashboard = () => {
  const { user } = useAuth();
  const [healthData, setHealthData] = useState(null);
  const [adminTestResult, setAdminTestResult] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  // Knowledge Base State
  const [documents, setDocuments] = useState([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState('');
  
  // Feedback Stats State
  const [feedbackStats, setFeedbackStats] = useState({
    total_queries: 0,
    resolved_queries: 0,
    resolution_rate: 100,
    helpful_feedback: 0,
    unhelpful_feedback: 0,
    satisfaction_rate: 100
  });

  // Modal State for Add / Edit
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState('add'); // 'add' or 'edit'
  const [editingItemId, setEditingItemId] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    category: 'academics',
    content: '',
    source_name: '',
    source_url: '',
    tags: '',
    is_active: true
  });
  const [formError, setFormError] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const fetchDocuments = async () => {
    setIsLoadingDocs(true);
    try {
      const params = {};
      if (searchQuery) params.q = searchQuery;
      if (selectedCategoryFilter) params.category = selectedCategoryFilter;
      const data = await adminKnowledgeService.list(params);
      setDocuments(data);
    } catch (err) {
      console.error("Failed to load documents:", err);
    } finally {
      setIsLoadingDocs(false);
    }
  };

  const fetchStats = async () => {
    try {
      const stats = await adminKnowledgeService.getStats();
      setFeedbackStats(stats);
    } catch (err) {
      console.error("Failed to load feedback stats:", err);
    }
  };

  const fetchHealth = async () => {
    setIsRefreshing(true);
    try {
      const data = await systemService.getHealth();
      setHealthData(data);
    } catch (err) {
      console.error("Health check error:", err);
      setHealthData({ status: "error", error: "Failed to connect to backend" });
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    fetchStats();
    fetchDocuments();
    authService.testAdminRole()
      .then((res) => setAdminTestResult(res))
      .catch((err) => console.error("Admin role check failed", err));
  }, []);

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      fetchDocuments();
    }, 300);
    return () => clearTimeout(delayDebounce);
  }, [searchQuery, selectedCategoryFilter]);

  const handleOpenAddModal = () => {
    setModalMode('add');
    setEditingItemId(null);
    setFormData({
      title: '',
      category: 'academics',
      content: '',
      source_name: '',
      source_url: '',
      tags: '',
      is_active: true
    });
    setFormError('');
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (item) => {
    setModalMode('edit');
    setEditingItemId(item.id);
    setFormData({
      title: item.title,
      category: item.category,
      content: item.content,
      source_name: item.source_name,
      source_url: item.source_url || '',
      tags: item.tags || '',
      is_active: item.is_active
    });
    setFormError('');
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSaveDocument = async (e) => {
    e.preventDefault();
    setFormError('');

    if (!formData.title || !formData.content || !formData.source_name) {
      setFormError('Please fill in Title, Content, and Authority Source Name.');
      return;
    }

    setIsSaving(true);
    try {
      if (modalMode === 'add') {
        await adminKnowledgeService.create(formData);
      } else {
        await adminKnowledgeService.update(editingItemId, formData);
      }
      setIsModalOpen(false);
      fetchDocuments();
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Failed to save knowledge item.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleToggleStatus = async (id) => {
    try {
      await adminKnowledgeService.toggleStatus(id);
      setDocuments((prev) =>
        prev.map((doc) => (doc.id === id ? { ...doc, is_active: !doc.is_active } : doc))
      );
    } catch (err) {
      console.error("Toggle status error:", err);
    }
  };

  const handleDelete = async (id, title) => {
    if (window.confirm(`Are you sure you want to delete knowledge record:\n"${title}"?`)) {
      try {
        await adminKnowledgeService.delete(id);
        setDocuments((prev) => prev.filter((doc) => doc.id !== id));
      } catch (err) {
        console.error("Delete error:", err);
        alert("Failed to delete document.");
      }
    }
  };

  return (
    <div className="dashboard-container">
      {/* Admin Profile Header */}
      <div className="dashboard-header-card admin-header">
        <div className="header-flex">
          <div className="profile-identity">
            <div className="avatar-circle avatar-admin">
              <Shield size={32} color="#ffffff" />
            </div>
            <div>
              <div className="name-role-row">
                <h1>{user?.full_name || 'Administrator'}</h1>
                <span className="badge-role-admin">System Admin</span>
              </div>
              <p className="student-metadata">
                <span><strong>Admin Portal:</strong> Dynamic Knowledge Management & Governance</span>
                <span className="dot-separator">•</span>
                <span><strong>Role:</strong> {user?.role}</span>
                <span className="dot-separator">•</span>
                <span><strong>Email:</strong> {user?.email}</span>
              </p>
            </div>
          </div>

          <div className="header-actions">
            <button onClick={fetchHealth} className="btn-secondary-sm" disabled={isRefreshing}>
              <RefreshCw size={14} className={isRefreshing ? 'spin' : ''} />
              <span>Refresh Health</span>
            </button>
          </div>
        </div>
      </div>

      {/* System Health Status Bar */}
      <div className="health-status-grid">
        <div className="health-card">
          <div className="health-icon green">
            <Server size={20} />
          </div>
          <div>
            <div className="health-title">Backend API</div>
            <div className="health-val">
              {healthData?.status === "healthy" ? "Healthy (HTTP 200)" : "Connecting..."}
            </div>
            <div className="health-sub">FastAPI v{healthData?.version || "1.0.0"}</div>
          </div>
        </div>

        <div className="health-card">
          <div className="health-icon blue">
            <Database size={20} />
          </div>
          <div>
            <div className="health-title">Database</div>
            <div className="health-val">
              {healthData?.database?.status === "connected"
                ? `Connected (${healthData.database.type})`
                : "Checking..."}
            </div>
            <div className="health-sub">{documents.length} Active Records</div>
          </div>
        </div>

        <div className="health-card">
          <div className="health-icon purple">
            <Activity size={20} />
          </div>
          <div>
            <div className="health-title">Role Guard Status</div>
            <div className="health-val">
              {adminTestResult ? "RBAC Enforced" : "Verifying..."}
            </div>
            <div className="health-sub">Admin / Student Segregated</div>
          </div>
        </div>

        <div className="health-card">
          <div className="health-icon amber">
            <Layers size={20} />
          </div>
          <div>
            <div className="health-title">RAG Engine</div>
            <div className="health-val">Dynamic Grounding</div>
            <div className="health-sub">Zero-Retraining Updates</div>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Main Column: Knowledge Base Management */}
        <div className="dashboard-main-panel">
          <div className="panel-card">
            <div className="card-title-row">
              <div className="icon-badge">
                <FileText size={20} color="#2563eb" />
              </div>
              <div style={{ flex: 1 }}>
                <h2>Institutional Knowledge Base Management</h2>
                <p>Add, edit, archive, or delete policy circulars in real-time without retraining the AI</p>
              </div>
              <button className="btn-primary-sm" onClick={handleOpenAddModal}>
                <Plus size={15} style={{ marginRight: 4 }} /> Add New Knowledge
              </button>
            </div>

            {/* Filter & Search Bar */}
            <div className="knowledge-filter-bar">
              <div className="search-input-wrapper">
                <Search size={16} color="#64748b" />
                <input
                  type="text"
                  placeholder="Search by title, authority, or keywords..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              <select
                className="category-filter-select"
                value={selectedCategoryFilter}
                onChange={(e) => setSelectedCategoryFilter(e.target.value)}
              >
                <option value="">All Categories</option>
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>{cat.toUpperCase()}</option>
                ))}
              </select>
            </div>

            {/* Knowledge Table */}
            <div className="table-responsive" style={{ marginTop: '1rem' }}>
              {isLoadingDocs ? (
                <p style={{ color: '#64748b', padding: '1rem 0' }}>Loading knowledge records...</p>
              ) : documents.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '2rem 0', color: '#64748b' }}>
                  <p>No knowledge records matched your search query.</p>
                </div>
              ) : (
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Title & Source</th>
                      <th>Category</th>
                      <th>Status</th>
                      <th>Last Modified</th>
                      <th style={{ textAlign: 'right' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map((doc) => (
                      <tr key={doc.id}>
                        <td style={{ maxWidth: '320px' }}>
                          <div className="table-doc-title">{doc.title}</div>
                          <div className="table-doc-sub">
                            Source: <strong>{doc.source_name}</strong>
                          </div>
                          <div className="table-doc-content-snippet">
                            {doc.content.substring(0, 100)}...
                          </div>
                        </td>
                        <td>
                          <span className="badge-category">{doc.category.toUpperCase()}</span>
                        </td>
                        <td>
                          <span className={`badge-status ${doc.is_active ? 'status-active' : 'status-archived'}`}>
                            {doc.is_active ? 'ACTIVE' : 'ARCHIVED'}
                          </span>
                        </td>
                        <td style={{ fontSize: '0.8rem', color: '#64748b' }}>
                          {new Date(doc.updated_at).toLocaleDateString()}
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          <div className="table-actions-group">
                            <button
                              onClick={() => handleToggleStatus(doc.id)}
                              className={`btn-action-outline ${doc.is_active ? '' : 'btn-activate'}`}
                              title={doc.is_active ? 'Archive this document' : 'Reactivate this document'}
                            >
                              <Archive size={13} style={{ marginRight: 4 }} />
                              {doc.is_active ? 'Archive' : 'Activate'}
                            </button>

                            <button
                              onClick={() => handleOpenEditModal(doc)}
                              className="btn-action-outline"
                              title="Edit Knowledge"
                            >
                              <Edit3 size={13} />
                            </button>

                            <button
                              onClick={() => handleDelete(doc.id, doc.title)}
                              className="btn-action-outline btn-delete"
                              title="Delete Record"
                            >
                              <Trash2 size={13} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          {/* Student Feedback & Satisfaction Section */}
          <div className="panel-card" style={{ marginTop: '1.5rem' }}>
            <div className="card-title-row">
              <div className="icon-badge">
                <ThumbsUp size={20} color="#2563eb" />
              </div>
              <div>
                <h2>Real-Time Student Query Resolution Metrics</h2>
                <p>Live telemetry computed directly from student resolution logs</p>
              </div>
            </div>

            <div className="feedback-summary-row">
              <div className="feedback-stat">
                <span className="stat-number">{feedbackStats.satisfaction_rate}%</span>
                <span className="stat-label">Student Satisfaction Rate</span>
              </div>
              <div className="feedback-stat">
                <span className="stat-number">{feedbackStats.total_queries}</span>
                <span className="stat-label">Total Queries Handled</span>
              </div>
              <div className="feedback-stat">
                <span className="stat-number">{feedbackStats.helpful_feedback}</span>
                <span className="stat-label">Positive Feedback Ratings</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Governance Guidelines */}
        <div className="dashboard-side-panel">
          <div className="panel-card">
            <h3>Knowledge Management Rules</h3>
            <ul className="rules-bullet-list" style={{ marginTop: '0.75rem' }}>
              <li>
                <strong>Instant Effect:</strong> Any added or updated document becomes immediately searchable by students in the next query.
              </li>
              <li>
                <strong>Archiving:</strong> Outdated rules should be switched to "Archived". The RAG retriever automatically ignores archived documents.
              </li>
              <li>
                <strong>Citations:</strong> Every knowledge item must specify the official Authority Source Name (e.g. Dean's Office, Exam Branch).
              </li>
              <li>
                <strong>Anti-Hallucination:</strong> Answers are only produced when a student's question matches verified active knowledge above the confidence threshold.
              </li>
            </ul>
          </div>

          <div className="panel-card" style={{ marginTop: '1.5rem' }}>
            <h3>Admin Privileges Boundary</h3>
            <p className="subtext">
              Only authenticated administrators can create, edit, or archive knowledge records. Student accounts are blocked with HTTP 403 Forbidden.
            </p>
            <div className="security-notice-box">
              <span>🛡️ RBAC Administrator Governance Enforced</span>
            </div>
          </div>
        </div>
      </div>

      {/* Add / Edit Knowledge Modal */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>{modalMode === 'add' ? 'Add New Knowledge Document' : 'Edit Knowledge Document'}</h3>
              <button onClick={handleCloseModal} className="btn-close-modal">
                <X size={20} />
              </button>
            </div>

            {formError && (
              <div className="alert-box alert-error" style={{ marginBottom: '1rem' }}>
                <AlertTriangle size={16} />
                <span>{formError}</span>
              </div>
            )}

            <form onSubmit={handleSaveDocument} className="modal-form">
              <div className="form-group">
                <label>Document Title *</label>
                <input
                  name="title"
                  type="text"
                  placeholder="e.g. End-Semester Examination Registration Guidelines"
                  value={formData.title}
                  onChange={handleFormChange}
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Category *</label>
                  <select
                    name="category"
                    value={formData.category}
                    onChange={handleFormChange}
                    required
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>{cat.toUpperCase()}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Authority Source Name *</label>
                  <input
                    name="source_name"
                    type="text"
                    placeholder="e.g. Controller of Examinations Notification #12"
                    value={formData.source_name}
                    onChange={handleFormChange}
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Source Document URL (Optional)</label>
                  <input
                    name="source_url"
                    type="url"
                    placeholder="https://university.edu/circulars/..."
                    value={formData.source_url}
                    onChange={handleFormChange}
                  />
                </div>

                <div className="form-group">
                  <label>Search Keywords / Tags</label>
                  <input
                    name="tags"
                    type="text"
                    placeholder="e.g. exam, hall ticket, fees, deadline"
                    value={formData.tags}
                    onChange={handleFormChange}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Institutional Content & Policy Details *</label>
                <textarea
                  name="content"
                  rows={6}
                  placeholder="Enter the full, precise verified factual instructions, eligibility criteria, fees, deadlines, or regulations..."
                  value={formData.content}
                  onChange={handleFormChange}
                  required
                />
              </div>

              <div className="form-group checkbox-row" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  id="is_active_check"
                  name="is_active"
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={handleFormChange}
                  style={{ width: 'auto' }}
                />
                <label htmlFor="is_active_check" style={{ marginBottom: 0, cursor: 'pointer' }}>
                  Active Status (Uncheck to archive and exclude from student queries)
                </label>
              </div>

              <div className="modal-actions">
                <button type="button" onClick={handleCloseModal} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={isSaving}>
                  {isSaving ? 'Saving...' : modalMode === 'add' ? 'Save & Publish to Knowledge Base' : 'Update Document'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
