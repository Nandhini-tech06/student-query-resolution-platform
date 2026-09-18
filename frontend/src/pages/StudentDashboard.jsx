import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { authService, queryService } from '../services/api';
import {
  GraduationCap,
  MessageSquare,
  History,
  ThumbsUp,
  ThumbsDown,
  Send,
  BookOpen,
  Calendar,
  Building,
  Home,
  Truck,
  CreditCard,
  Briefcase,
  Award,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Sparkles,
  HelpCircle,
  Clock
} from 'lucide-react';

const CATEGORIES = [
  { id: 'academics', label: 'Academics', icon: BookOpen },
  { id: 'examinations', label: 'Examinations', icon: Calendar },
  { id: 'fees', label: 'Fees & Accounts', icon: CreditCard },
  { id: 'hostel', label: 'Hostel & Mess', icon: Home },
  { id: 'library', label: 'Library', icon: BookOpen },
  { id: 'placements', label: 'Placements', icon: Briefcase },
  { id: 'certificates', label: 'Certificates', icon: Award },
  { id: 'transport', label: 'Transport', icon: Truck },
  { id: 'rules', label: 'Rules & Safety', icon: Building },
];

const PROMPT_SUGGESTIONS = [
  "What is the minimum attendance required to appear for exams?",
  "How much late fine is charged if tuition fee payment is delayed?",
  "What are the hostel curfew timings and outstation leave rules?",
  "How many books can undergraduate students borrow from the library?",
  "What is the procedure to get an official Bonafide Certificate?"
];

const StudentDashboard = () => {
  const { user } = useAuth();
  const [selectedCategory, setSelectedCategory] = useState('academics');
  const [queryInput, setQueryInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentAnswer, setCurrentAnswer] = useState(null);
  const [history, setHistory] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [testApiResult, setTestApiResult] = useState(null);
  const [feedbackSuccessId, setFeedbackSuccessId] = useState(null);

  const fetchHistory = async () => {
    try {
      const data = await queryService.getHistory();
      setHistory(data);
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  useEffect(() => {
    authService.testStudentRole()
      .then((res) => setTestApiResult(res))
      .catch((err) => console.error("Student test failed", err));

    fetchHistory();
  }, []);

  const handleQuerySubmit = async (e) => {
    if (e) e.preventDefault();
    if (!queryInput.trim() || isSubmitting) return;

    setIsSubmitting(true);
    setCurrentAnswer(null);

    try {
      const response = await queryService.ask(queryInput, selectedCategory);
      setCurrentAnswer(response);
      setQueryInput('');
      fetchHistory(); // Refresh history
    } catch (err) {
      console.error("Error asking query:", err);
      setCurrentAnswer({
        is_resolved: false,
        question: queryInput,
        answer: "Failed to communicate with the Query Resolution backend. Please ensure the server is active.",
        sources: []
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setQueryInput(suggestion);
  };

  const handleFeedback = async (queryId, rating) => {
    try {
      await queryService.submitFeedback(queryId, rating);
      setFeedbackSuccessId(queryId);
      // Update local history
      setHistory((prev) =>
        prev.map((item) => (item.id === queryId ? { ...item, feedback_rating: rating } : item))
      );
      setTimeout(() => setFeedbackSuccessId(null), 2500);
    } catch (err) {
      console.error("Feedback error:", err);
    }
  };

  return (
    <div className="dashboard-container">
      {/* Student Profile Header */}
      <div className="dashboard-header-card">
        <div className="header-flex">
          <div className="profile-identity">
            <div className="avatar-circle">
              <GraduationCap size={32} color="#ffffff" />
            </div>
            <div>
              <div className="name-role-row">
                <h1>{user?.full_name || 'Student Portal'}</h1>
                <span className="badge-role-student">Student Account</span>
              </div>
              <p className="student-metadata">
                <span><strong>Student ID:</strong> {user?.student_id || 'STU-2026-999'}</span>
                <span className="dot-separator">•</span>
                <span><strong>Department:</strong> {user?.department || 'Computer Science'}</span>
                <span className="dot-separator">•</span>
                <span><strong>Email:</strong> {user?.email}</span>
              </p>
            </div>
          </div>

          <div className="auth-status-chip">
            <ShieldCheck size={18} color="#16a34a" />
            <span>RBAC Verified: {testApiResult ? "Student Access Active" : "Verifying..."}</span>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Left Column: Ask Query & Live Resolution */}
        <div className="dashboard-main-panel">
          <div className="panel-card">
            <div className="card-title-row">
              <div className="icon-badge">
                <Sparkles size={20} color="#2563eb" />
              </div>
              <div>
                <h2>Ask a Student Service Query</h2>
                <p>Retrieval-Augmented Generation (RAG) backed by verified university knowledge</p>
              </div>
            </div>

            <div className="service-category-selector">
              <label className="section-label">Select Service Domain:</label>
              <div className="category-chips">
                {CATEGORIES.map((cat) => {
                  const Icon = cat.icon;
                  const isSelected = selectedCategory === cat.id;
                  return (
                    <button
                      key={cat.id}
                      type="button"
                      onClick={() => setSelectedCategory(cat.id)}
                      className={`chip-btn ${isSelected ? 'active' : ''}`}
                    >
                      <Icon size={14} />
                      <span>{cat.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="prompt-suggestions-box">
              <span className="suggestions-label">Try asking:</span>
              <div className="suggestions-list">
                {PROMPT_SUGGESTIONS.map((suggestion, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="suggestion-pill"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>

            <form onSubmit={handleQuerySubmit} className="query-input-form" style={{ marginTop: '1rem' }}>
              <textarea
                id="student-query"
                rows={3}
                placeholder="Ask any question regarding exams, fees, attendance, hostel, library..."
                value={queryInput}
                onChange={(e) => setQueryInput(e.target.value)}
                disabled={isSubmitting}
              />

              <div className="form-action-row">
                <span className="info-note">
                  🔒 Strictly grounded on verified institutional circulars & policies
                </span>
                <button type="submit" className="btn-primary" disabled={isSubmitting || !queryInput.trim()}>
                  <Send size={16} />
                  <span>{isSubmitting ? 'Retrieving Answer...' : 'Submit Query'}</span>
                </button>
              </div>
            </form>
          </div>

          {/* Live Answer Card */}
          {currentAnswer && (
            <div className="panel-card" style={{ marginTop: '1.5rem', borderLeft: currentAnswer.is_resolved ? '4px solid #2563eb' : '4px solid #f59e0b' }}>
              <div className="card-title-row">
                <div className="icon-badge" style={{ background: currentAnswer.is_resolved ? '#eff6ff' : '#fffbeb' }}>
                  {currentAnswer.is_resolved ? (
                    <CheckCircle2 size={20} color="#2563eb" />
                  ) : (
                    <AlertCircle size={20} color="#d97706" />
                  )}
                </div>
                <div style={{ flex: 1 }}>
                  <h2>{currentAnswer.is_resolved ? 'Verified Resolution' : 'Information Unavailable in Official Records'}</h2>
                  <p>Query: "{currentAnswer.question}"</p>
                </div>
              </div>

              <div className="answer-content-area" style={{ whiteSpace: 'pre-line', lineHeight: '1.6', fontSize: '0.95rem' }}>
                {currentAnswer.answer}
              </div>

              {/* Source References */}
              {currentAnswer.sources && currentAnswer.sources.length > 0 && (
                <div className="sources-citation-block">
                  <span className="sources-block-title">Verified Source Documents:</span>
                  <div className="source-citations-list">
                    {currentAnswer.sources.map((src, i) => (
                      <div key={i} className="source-citation-chip">
                        <BookOpen size={13} color="#2563eb" />
                        <span className="src-title"><strong>{src.title}</strong></span>
                        <span className="src-authority">• {src.source_name}</span>
                        {src.source_url && (
                          <a href={src.source_url} target="_blank" rel="noreferrer" className="src-link">
                            <ExternalLink size={12} />
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Quick Feedback Bar */}
              {currentAnswer.id && (
                <div className="history-feedback-bar" style={{ marginTop: '1.25rem' }}>
                  <span className="feedback-prompt">Was this resolution helpful?</span>
                  <div className="feedback-actions">
                    <button
                      onClick={() => handleFeedback(currentAnswer.id, 'HELPFUL')}
                      className="btn-feedback"
                      title="Mark as Helpful"
                    >
                      <ThumbsUp size={14} color="#16a34a" /> Helpful
                    </button>
                    <button
                      onClick={() => handleFeedback(currentAnswer.id, 'UNHELPFUL')}
                      className="btn-feedback"
                      title="Mark as Not Helpful"
                    >
                      <ThumbsDown size={14} color="#dc2626" /> Needs Improvement
                    </button>
                    {feedbackSuccessId === currentAnswer.id && (
                      <span className="feedback-success-msg">✓ Thank you for your feedback!</span>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Query History Section */}
          <div className="panel-card" style={{ marginTop: '1.5rem' }}>
            <div className="card-title-row">
              <div className="icon-badge">
                <History size={20} color="#2563eb" />
              </div>
              <div style={{ flex: 1 }}>
                <h2>My Query History & Resolutions</h2>
                <p>Personal log of queries asked and verified resolutions provided</p>
              </div>
            </div>

            {isLoadingHistory ? (
              <p style={{ color: '#64748b', fontSize: '0.9rem' }}>Loading previous queries...</p>
            ) : history.length === 0 ? (
              <div className="empty-history-box">
                <HelpCircle size={32} color="#94a3b8" />
                <p>No queries asked yet. Ask your first question above!</p>
              </div>
            ) : (
              <div className="history-list">
                {history.map((item) => (
                  <div key={item.id} className="history-item">
                    <div className="history-header">
                      <span className="history-category-badge">{item.category || 'General'}</span>
                      <span className="history-time">
                        <Clock size={12} style={{ marginRight: 4 }} />
                        {new Date(item.created_at).toLocaleString()}
                      </span>
                      <span className={`history-status-badge ${item.is_resolved ? 'status-green' : 'status-amber'}`}>
                        {item.is_resolved ? '✓ Resolved' : '⚠ Record Unavailable'}
                      </span>
                    </div>

                    <h4 className="history-question">"{item.question}"</h4>
                    <div className="history-answer-preview" style={{ whiteSpace: 'pre-line' }}>
                      {item.answer}
                    </div>

                    {item.sources && item.sources.length > 0 && (
                      <div className="history-sources-row">
                        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#475569' }}>Sources:</span>
                        {item.sources.map((s, idx) => (
                          <span key={idx} className="badge-source-inline">
                            {s.title} ({s.source_name})
                          </span>
                        ))}
                      </div>
                    )}

                    <div className="history-feedback-bar">
                      <span className="feedback-prompt">Feedback:</span>
                      <div className="feedback-actions">
                        <button
                          onClick={() => handleFeedback(item.id, 'HELPFUL')}
                          className={`btn-feedback ${item.feedback_rating === 'HELPFUL' ? 'active-feedback-good' : ''}`}
                        >
                          <ThumbsUp size={13} /> {item.feedback_rating === 'HELPFUL' ? 'Helpful (Recorded)' : 'Helpful'}
                        </button>
                        <button
                          onClick={() => handleFeedback(item.id, 'UNHELPFUL')}
                          className={`btn-feedback ${item.feedback_rating === 'UNHELPFUL' ? 'active-feedback-bad' : ''}`}
                        >
                          <ThumbsDown size={13} /> {item.feedback_rating === 'UNHELPFUL' ? 'Not Helpful (Recorded)' : 'Not Helpful'}
                        </button>
                        {feedbackSuccessId === item.id && (
                          <span className="feedback-success-msg">✓ Recorded</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Authorized Information & Services */}
        <div className="dashboard-side-panel">
          <div className="panel-card">
            <h3>Verified University Knowledge</h3>
            <p className="subtext">The platform answers queries across verified university domains:</p>
            <ul className="service-feature-list">
              <li>
                <strong>Academic Policies:</strong> Attendance criteria, 10-point grading, SGPA/CGPA, branch changes.
              </li>
              <li>
                <strong>Examinations Desk:</strong> Hall ticket eligibility, supplementary exams, challenge revaluation.
              </li>
              <li>
                <strong>Fees & Accounts:</strong> Payment gateways, semester deadlines, late fine tiers.
              </li>
              <li>
                <strong>Hostel & Mess:</strong> Biometric curfew, leave pass approval, caution deposit.
              </li>
              <li>
                <strong>Central Library:</strong> Book borrowing quotas, renewal, overdue fines, IEEE access.
              </li>
              <li>
                <strong>Campus Transport:</strong> Daily bus routes, timings, night shuttle schedules.
              </li>
              <li>
                <strong>Placements:</strong> Minimum CGPA eligibility, dream company policies.
              </li>
              <li>
                <strong>Certificates:</strong> Bonafide certificates, transcripts, duplicate ID card issuance.
              </li>
            </ul>
          </div>

          <div className="panel-card" style={{ marginTop: '1.5rem' }}>
            <h3>Anti-Hallucination Guarantee</h3>
            <p className="subtext">
              The AI is strictly constrained to approved institutional documents. If verified facts are not present in current bylaws, the system will never guess.
            </p>
            <div className="security-notice-box">
              <span>🛡️ RAG Verification & Grounding Active</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
