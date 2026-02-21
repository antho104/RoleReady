import { useState, useEffect } from 'react';
import { fetchAuthSession } from 'aws-amplify/auth';
import { useNavigate } from 'react-router-dom';
import './Admin.css';

interface Question {
  id?: string;
  question: string;
  category: string;
  competency_type: string;
  answer: string;
}

function Admin() {
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [editingQuestion, setEditingQuestion] = useState<Question | null>(null);
  const [showCreateForm, setShowCreateForm] = useState<boolean>(false);
  const [formData, setFormData] = useState<Question>({
    question: '',
    category: '',
    competency_type: '',
    answer: '',
  });
  const navigate = useNavigate();

  useEffect(() => {
    checkAdminAccess();
  }, []);

  const checkAdminAccess = async () => {
    try {
      const session = await fetchAuthSession();
      const groups = session.tokens?.accessToken?.payload['cognito:groups'] as string[] || [];

      if (groups.includes('Admin')) {
        setIsAdmin(true);
        fetchQuestions();
      } else {
        setIsAdmin(false);
        setLoading(false);
      }
    } catch (error) {
      console.error('Error checking admin access:', error);
      setIsAdmin(false);
      setLoading(false);
    }
  };

  const fetchQuestions = async () => {
    try {
      const session = await fetchAuthSession();
      const token = session.tokens?.idToken?.toString();

      const response = await fetch(`${import.meta.env.VITE_API_URL}questions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setQuestions(data);
      }
    } catch (error) {
      console.error('Error fetching questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateQuestion = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const session = await fetchAuthSession();
      const token = session.tokens?.idToken?.toString();

      const response = await fetch(`${import.meta.env.VITE_API_URL}questions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const newQuestion = await response.json();
        setQuestions([...questions, newQuestion]);
        setFormData({ question: '', category: '', competency_type: '', answer: '' });
        setShowCreateForm(false);
        alert('Question created successfully!');
      } else {
        const error = await response.json();
        alert(`Error: ${error.message || 'Failed to create question'}`);
      }
    } catch (error) {
      console.error('Error creating question:', error);
      alert('Error creating question');
    }
  };

  const handleUpdateQuestion = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!editingQuestion?.id) return;

    try {
      const session = await fetchAuthSession();
      const token = session.tokens?.idToken?.toString();

      const response = await fetch(`${import.meta.env.VITE_API_URL}questions/${editingQuestion.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editingQuestion),
      });

      if (response.ok) {
        const updated = await response.json();
        setQuestions(questions.map(q => q.id === updated.id ? updated : q));
        setEditingQuestion(null);
        alert('Question updated successfully!');
      } else {
        const error = await response.json();
        alert(`Error: ${error.message || 'Failed to update question'}`);
      }
    } catch (error) {
      console.error('Error updating question:', error);
      alert('Error updating question');
    }
  };

  const handleDeleteQuestion = async (id: string) => {
    if (!confirm('Are you sure you want to delete this question?')) {
      return;
    }

    try {
      const session = await fetchAuthSession();
      const token = session.tokens?.idToken?.toString();

      const response = await fetch(`${import.meta.env.VITE_API_URL}questions/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok || response.status === 204) {
        setQuestions(questions.filter(q => q.id !== id));
        alert('Question deleted successfully!');
      } else {
        alert('Error deleting question');
      }
    } catch (error) {
      console.error('Error deleting question:', error);
      alert('Error deleting question');
    }
  };

  if (loading) {
    return <div className="admin-container"><div className="loading">Loading...</div></div>;
  }

  if (!isAdmin) {
    return (
      <div className="admin-container">
        <div className="access-denied">
          <h1>🚫 Access Denied</h1>
          <p>You do not have administrator privileges.</p>
          <p>Only users in the Admin group can access this page.</p>
          <button onClick={() => navigate('/')}>Return to Home</button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>🛠️ Admin Dashboard</h1>
        <button onClick={() => navigate('/')}>Back to Home</button>
      </div>

      <div className="admin-actions">
        <button
          className="btn-primary"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? '❌ Cancel' : '➕ Create New Question'}
        </button>
      </div>

      {/* Create Question Form */}
      {showCreateForm && (
        <div className="question-form">
          <h2>Create New Question</h2>
          <form onSubmit={handleCreateQuestion}>
            <div className="form-group">
              <label>Question Text:</label>
              <textarea
                value={formData.question}
                onChange={(e) => setFormData({ ...formData, question: e.target.value })}
                required
                rows={4}
              />
            </div>

            <div className="form-group">
              <label>Category:</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                required
              >
                <option value="">Select category...</option>
                <option value="AWS">AWS</option>
                <option value="Azure">Azure</option>
                <option value="GCP">GCP</option>
                <option value="Leadership">Leadership</option>
                <option value="System Design">System Design</option>
              </select>
            </div>

            <div className="form-group">
              <label>Competency Type:</label>
              <select
                value={formData.competency_type}
                onChange={(e) => setFormData({ ...formData, competency_type: e.target.value })}
                required
              >
                <option value="">Select type...</option>
                <option value="Technical">Technical</option>
                <option value="Behavioral">Behavioral</option>
                <option value="Situational">Situational</option>
              </select>
            </div>

            <div className="form-group">
              <label>Model Answer (Optional):</label>
              <textarea
                value={formData.answer}
                onChange={(e) => setFormData({ ...formData, answer: e.target.value })}
                rows={6}
              />
            </div>

            <button type="submit" className="btn-success">Create Question</button>
          </form>
        </div>
      )}

      {/* Edit Question Form */}
      {editingQuestion && (
        <div className="question-form">
          <h2>Edit Question</h2>
          <form onSubmit={handleUpdateQuestion}>
            <div className="form-group">
              <label>Question Text:</label>
              <textarea
                value={editingQuestion.question}
                onChange={(e) => setEditingQuestion({ ...editingQuestion, question: e.target.value })}
                required
                rows={4}
              />
            </div>

            <div className="form-group">
              <label>Category:</label>
              <select
                value={editingQuestion.category}
                onChange={(e) => setEditingQuestion({ ...editingQuestion, category: e.target.value })}
                required
              >
                <option value="AWS">AWS</option>
                <option value="Azure">Azure</option>
                <option value="GCP">GCP</option>
                <option value="Leadership">Leadership</option>
                <option value="System Design">System Design</option>
              </select>
            </div>

            <div className="form-group">
              <label>Competency Type:</label>
              <select
                value={editingQuestion.competency_type}
                onChange={(e) => setEditingQuestion({ ...editingQuestion, competency_type: e.target.value })}
                required
              >
                <option value="Technical">Technical</option>
                <option value="Behavioral">Behavioral</option>
                <option value="Situational">Situational</option>
              </select>
            </div>

            <div className="form-group">
              <label>Model Answer:</label>
              <textarea
                value={editingQuestion.answer}
                onChange={(e) => setEditingQuestion({ ...editingQuestion, answer: e.target.value })}
                rows={6}
              />
            </div>

            <div className="form-buttons">
              <button type="submit" className="btn-success">Save Changes</button>
              <button type="button" onClick={() => setEditingQuestion(null)} className="btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Questions List */}
      <div className="questions-list">
        <h2>All Questions ({questions.length})</h2>

        {questions.length === 0 && <p className="no-questions">No questions found.</p>}

        {questions.map((q) => (
          <div key={q.id} className="question-card">
            <div className="question-content">
              <h3>{q.question}</h3>
              <div className="question-meta">
                <span className="badge">{q.category}</span>
                <span className="badge">{q.competency_type}</span>
              </div>
              {q.answer && (
                <details className="answer-details">
                  <summary>Model Answer</summary>
                  <p>{q.answer}</p>
                </details>
              )}
            </div>
            <div className="question-actions">
              <button className="btn-edit" onClick={() => setEditingQuestion(q)}>
                ✏️ Edit
              </button>
              <button className="btn-delete" onClick={() => handleDeleteQuestion(q.id!)}>
                🗑️ Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Admin;
