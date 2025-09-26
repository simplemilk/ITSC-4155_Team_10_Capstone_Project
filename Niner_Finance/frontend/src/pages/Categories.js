import React, { useEffect, useState } from 'react';

export default function Categories() {
  const [categories, setCategories] = useState([]);
  const [selectedId, setSelectedId] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('http://localhost:4000/api/categories')
      .then(res => res.json())
      .then(data => setCategories(data))
      .catch(() => setError('Failed to load categories.'));
  }, []);

  const selectedCategory = categories.find(cat => String(cat.id) === selectedId);

  return (
    <div className="categories-root">
      <h1>Choose a Category</h1>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <select
        value={selectedId}
        onChange={e => setSelectedId(e.target.value)}
      >
         <option value="">-- Select Category --</option>
        {categories.map(cat => (
          <option key={cat.id} value={cat.id}>{cat.name}</option>
        ))}
      </select>
      {selectedCategory && Array.isArray(selectedCategory.subcategories) && (
        <div>
          <h2>Subcategories for {selectedCategory.name}</h2>
          {selectedCategory.subcategories.length === 0 ? (
            <p>No subcategories yet.</p>
          ) : (
            <ul>
              {selectedCategory.subcategories.map(sub => (
                <li key={sub.id}>{sub.name}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
);
}