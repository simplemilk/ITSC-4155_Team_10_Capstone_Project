import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Register from './Register';

test('renders registration form', () => {
  render(<Register />);
  expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
});

test('shows error when submitting empty form', async () => {
  render(<Register />);
  fireEvent.click(screen.getByRole('button', { name: /Register/i }));
  expect(await screen.findByText(/Registration failed/i)).toBeInTheDocument();
});