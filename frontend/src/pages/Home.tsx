import { Link } from 'react-router-dom';
import './Home.css';

export default function Home() {
  return (
    <div className="home-container">
      <h1>Role Ready</h1>
      <p>Search, filter, and manage technical interview questions + this is a test</p>
      <div className="home-actions">
        <Link to="/questions" className="btn btn-primary">
          Browse Questions
        </Link>
        <Link to="/login" className="btn btn-secondary">
          Login
        </Link>
      </div>
    </div>
  );
}
