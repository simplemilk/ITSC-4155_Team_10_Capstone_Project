import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Navbar from './components/Navbar';
import Register from './components/Register';
import Home from './pages/Home';
import Categories from './pages/Categories';
import ForgotPasswordPage from './pages/ForgetPassword';
import ResetPasswordPage from './pages/ResetPassword';
import Login from './pages/Login';
import { useEffect } from 'react';

function App() {
  useEffect(() => {
    localStorage.removeItem('username');
  }, []);

  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/home" element={<Home />} />
        <Route path="/categories" element={<Categories />} />
        <Route path="/login/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/register/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
