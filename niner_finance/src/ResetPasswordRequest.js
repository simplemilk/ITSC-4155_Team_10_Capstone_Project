import React, { useState, useEffect } from "react";
import { useParams, useHistory } from "react-router-dom";

const ResetPassword = () => {
  const { token } = useParams();
  const history = useHistory();
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      setMessage("Passwords do not match");
      return;
    }

    if (newPassword.length < 6) {
      setMessage("Password must be at least 6 characters long");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/reset-password/${token}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ newPassword }),
      });

      const data = await response.json();
      if (response.ok) {
        setMessage(data.message || "Password reset successfully!");
        setTimeout(() => {
          history.push("/");
        }, 2000);
      } else {
        setMessage(data.message || "Error resetting password.");
      }
    } catch (error) {
      console.error("Error:", error);
      setMessage("Error resetting password.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2>Reset Your Password</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            New Password:
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              minLength={6}
            />
          </label>
        </div>
        <div>
          <label>
            Confirm Password:
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={6}
            />
          </label>
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Resetting..." : "Reset Password"}
        </button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default ResetPassword;