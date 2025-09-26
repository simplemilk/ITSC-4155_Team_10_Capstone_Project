import React from 'react';
import {Link} from 'react-router-dom';
import './Navbar.css';

export default function Navbar() {
    return (
        <nav className="navbar">
            <Link to="/register">Register</Link>
            <Link to="/">Home</Link>
        </nav>
    );
}
