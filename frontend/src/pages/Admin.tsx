import { useState, useMemo, useEffect } from 'react';
import { fetchAuthSession } from 'aws-amplify/auth';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getAllQuestions } from '../services/api';
import type { Question } from '../services/api';
import './Questions.css';
import './Admin.css';

function Admin() {
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [showCreateForm, setShowCreateForm] = useState<boolean>(false);
  const [editingQuestion, setEditingQuestion] = useState<Question | null>(null);
  const [formData, setFormData] = useState({
    question_text: '',
    category: '',
    difficulty: 'Medium',
    reference_answer: '',
  });
  const navigate = useNavigate();
  const { getAuthToken } = useAuth();

  useEffect(() => {
    checkAdminAccess();
  }, []);

  const checkAdminAccess = async () => {
    try {
      const session = await fetchAuthSession();
      const groups = session.tokens?.accessToken?.payload['cognito:groups'] as string[] || [];

      if (groups.includes('Admin')) {
        setIsAdmin(true);
        loadQuestions();
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

  const loadQuestions = async () => {
    try {
      setLoading(true);
      const token = await getAuthToken();
      const data = await getAllQuestions(token);
      setQuestions(data);
    } catch (error) {
      console.error('Error fetching questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = useMemo(() => {
    const cats = new Set(questions.map(q => q.category));
    return ['All', ...Array.from(cats)];
  }, [questions]);

  const difficulties = useMemo(() => {
    const diffs = new Set(questions.map(q => q.difficulty.toLowerCase()));
    return ['All', ...Array.from(diffs)];
  }, [questions]);

  const filteredQuestions = useMemo(() => {
    return questions.filter(question => {
      const matchesSearch = question.question_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           question.category.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesCategory = selectedCategory === 'All' || question.category === selectedCategory;
      const matchesDifficulty = selectedDifficulty === 'All' ||
                                question.difficulty.toLowerCase() === selectedDifficulty.toLowerCase();

      return matchesSearch && matchesCategory && matchesDifficulty;
    });
  }, [questions, searchTerm, selectedCategory, selectedDifficulty]);

  const getDifficultyClass = (difficulty: string) => {
    return `difficulty difficulty-${difficulty.toLowerCase()}`;
  };

  const capitalizeCategory = (category: string) => {
    return category.charAt(0).toUpperCase() + category.slice(1).toLowerCase();
  };

  const capitalizeDifficulty = (difficulty: string) => {
    return difficulty.charAt(0).toUpperCase() + difficulty.slice(1).toLowerCase();
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
        body: JSON.stringify({
          question_text: formData.question_text,
          category: formData.category,
          difficulty: formData.difficulty,
          reference_answer: formData.reference_answer,
        }),
      });

      if (response.ok) {
        await loadQuestions();
        setFormData({ question_text: '', category: '', difficulty: 'Medium', reference_answer: '' });
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
        body: JSON.stringify({
          question_text: editingQuestion.question_text,
          category: editingQuestion.category,
          difficulty: editingQuestion.difficulty,
          reference_answer: editingQuestion.reference_answer,
        }),
      });

      if (response.ok) {
        await loadQuestions();
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
        await loadQuestions();
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
    return (
      <div className="questions-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="questions-container">
        <div className="error-box">
          <h2>🚫 Access Denied</h2>
          <p>You do not have administrator privileges.</p>
          <p>Only users in the Admin group can access this page.</p>
          <button className="btn" onClick={() => navigate('/')}>Return to Home</button>
        </div>
      </div>
    );
  }

  return (
    <div className="questions-container">
      <header className="questions-header">
        <h1>🛠️ Admin Dashboard</h1>
        <p>Manage interview questions - Create, Edit, and Delete</p>
        <button className="btn btn-small" onClick={() => navigate('/')}>← Back to Home</button>
      </header>

      <div className="admin-actions">
        <button
          className="btn btn-primary"
          onClick={() => {
            setShowCreateForm(!showCreateForm);
            setEditingQuestion(null);
          }}
        >
          {showCreateForm ? '❌ Cancel' : '➕ Create New Question'}
        </button>
      </div>

      {/* Create Question Form */}
      {showCreateForm && (
        <div className="question-form-modal">
          <h2>Create New Question</h2>
          <form onSubmit={handleCreateQuestion}>
            <div className="form-group">
              <label>Question Text:</label>
              <textarea
                value={formData.question_text}
                onChange={(e) => setFormData({ ...formData, question_text: e.target.value })}
                required
                rows={4}
                placeholder="Enter the interview question..."
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Category:</label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  required
                  placeholder="e.g., AWS, System Design, Automation..."
                />
              </div>

              <div className="form-group">
                <label>Difficulty:</label>
                <select
                  value={formData.difficulty}
                  onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                  required
                >
                  <option value="Easy">Easy</option>
                  <option value="Medium">Medium</option>
                  <option value="Hard">Hard</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Reference Answer (Optional):</label>
              <textarea
                value={formData.reference_answer}
                onChange={(e) => setFormData({ ...formData, reference_answer: e.target.value })}
                rows={6}
                placeholder="Provide a model answer..."
              />
            </div>

            <button type="submit" className="btn btn-primary">Create Question</button>
          </form>
        </div>
      )}

      {/* Edit Question Form */}
      {editingQuestion && (
        <div className="question-form-modal">
          <h2>Edit Question</h2>
          <form onSubmit={handleUpdateQuestion}>
            <div className="form-group">
              <label>Question Text:</label>
              <textarea
                value={editingQuestion.question_text}
                onChange={(e) => setEditingQuestion({ ...editingQuestion, question_text: e.target.value })}
                required
                rows={4}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Category:</label>
                <input
                  type="text"
                  value={editingQuestion.category}
                  onChange={(e) => setEditingQuestion({ ...editingQuestion, category: e.target.value })}
                  required
                  placeholder="e.g., AWS, System Design, Automation..."
                />
              </div>

              <div className="form-group">
                <label>Difficulty:</label>
                <select
                  value={editingQuestion.difficulty}
                  onChange={(e) => setEditingQuestion({ ...editingQuestion, difficulty: e.target.value })}
                  required
                >
                  <option value="Easy">Easy</option>
                  <option value="Medium">Medium</option>
                  <option value="Hard">Hard</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Reference Answer:</label>
              <textarea
                value={editingQuestion.reference_answer}
                onChange={(e) => setEditingQuestion({ ...editingQuestion, reference_answer: e.target.value })}
                rows={6}
              />
            </div>

            <div className="form-buttons">
              <button type="submit" className="btn btn-primary">Save Changes</button>
              <button type="button" className="btn btn-secondary" onClick={() => setEditingQuestion(null)}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filters matching Questions page */}
      <div className="filters">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search questions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <label>Category:</label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Difficulty:</label>
          <select
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
          >
            {difficulties.map(diff => (
              <option key={diff} value={diff}>{capitalizeDifficulty(diff)}</option>
            ))}
          </select>
        </div>

        <button className="btn btn-small" onClick={loadQuestions}>
          🔄 Refresh
        </button>
      </div>

      {/* Questions List matching Questions page */}
      <div className="questions-list">
        {filteredQuestions.length === 0 ? (
          <p className="no-results">
            {questions.length === 0
              ? 'No questions available yet. Create some questions to get started!'
              : 'No questions found matching your filters.'}
          </p>
        ) : (
          filteredQuestions.map(question => (
            <div key={question.id} className="question-card">
              <div className="question-header">
                <h3>{question.question_text}</h3>
                <span className={getDifficultyClass(question.difficulty)}>
                  {capitalizeDifficulty(question.difficulty)}
                </span>
              </div>
              <div className="question-footer">
                <div className="question-tags">
                  <span className="tag">{capitalizeCategory(question.category)}</span>
                </div>
                <div className="admin-buttons">
                  <button
                    className="btn btn-small btn-edit"
                    onClick={() => {
                      setEditingQuestion(question);
                      setShowCreateForm(false);
                    }}
                  >
                    ✏️ Edit
                  </button>
                  <button
                    className="btn btn-small btn-delete"
                    onClick={() => handleDeleteQuestion(question.id)}
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="results-count">
        Showing {filteredQuestions.length} of {questions.length} questions
      </div>
    </div>
  );
}

export default Admin;
