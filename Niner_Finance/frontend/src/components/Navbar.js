import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
  const [loggedIn, setLoggedIn] = useState(!!localStorage.getItem('username'));
  const navigate = useNavigate();

  useEffect(() => {
    const handleStorageChange = () => {
      setLoggedIn(!!localStorage.getItem('username'));
    };
    window.addEventListener('storage', handleStorageChange);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('username');
    localStorage.removeItem('userId'); // Also remove userId
    setLoggedIn(false);
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-left">
        {loggedIn ? (
          <button className="nav-btn login-btn" onClick={handleLogout}>
            Log Out
          </button>
        ) : (
          <>
            <Link to="/login" className="nav-btn login-btn">Login</Link>
            <Link to="/register" className="nav-btn register-btn">Register</Link>
          </>
        )}
      </div>
      <div className="navbar-right">
        <Link to="/categories" className="nav-btn">Categories</Link>
        <Link to="/" className="nav-btn">Home</Link>
      </div>
    </nav>
  );
}

export default Navbar;