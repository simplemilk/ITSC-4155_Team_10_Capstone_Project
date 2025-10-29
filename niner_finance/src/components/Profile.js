import React, { useState } from 'react';

function Profile() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Simulate successful update
    setSuccessMessage('Profile updated successfully!');
    setTimeout(() => setSuccessMessage(''), 3000); // Clear message after 3 seconds
    console.log('Profile updated:', { name, email });
  };

  return (
    <div className="profile-container" style={{ padding: '20px', maxWidth: '500px', margin: '0 auto' }}>
      <h2>Profile Settings</h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <div>
          <label htmlFor="name" style={{ display: 'block', marginBottom: '5px' }}>Name:</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
          />
        </div>
        
        <div>
          <label htmlFor="email" style={{ display: 'block', marginBottom: '5px' }}>Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
          />
        </div>

        <button
          type="submit"
          style={{
            backgroundColor: '#4CAF50',
            color: 'white',
            padding: '10px',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Save Changes
        </button>

        <button
          type="button"
          onClick={() => console.log('Password reset requested')}
          style={{
            backgroundColor: '#2196F3',
            color: 'white',
            padding: '10px',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            marginTop: '10px'
          }}
        >
          Request Password Reset Email
        </button>

        {successMessage && (
          <div
            style={{
              backgroundColor: '#4CAF50',
              color: 'white',
              padding: '10px',
              borderRadius: '4px',
              marginTop: '10px',
              textAlign: 'center'
            }}
            role="alert"
          >
            {successMessage}
          </div>
        )}
      </form>
    </div>
  );
}

export default Profile;