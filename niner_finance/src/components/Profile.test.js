import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Profile from './Profile';

describe('Profile Component', () => {
  test('renders profile form with all elements', () => {
    render(<Profile />);
    
    // Check if all form elements are present
    expect(screen.getByLabelText(/name:/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email:/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save changes/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /request password reset email/i })).toBeInTheDocument();
  });

  test('allows input of name and email', () => {
    render(<Profile />);
    
    const nameInput = screen.getByLabelText(/name:/i);
    const emailInput = screen.getByLabelText(/email:/i);

    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(emailInput, { target: { value: 'john@example.com' } });

    expect(nameInput.value).toBe('John Doe');
    expect(emailInput.value).toBe('john@example.com');
  });

  test('shows success message when form is submitted', async () => {
    render(<Profile />);
    
    // Fill out the form
    fireEvent.change(screen.getByLabelText(/name:/i), { target: { value: 'John Doe' } });
    fireEvent.change(screen.getByLabelText(/email:/i), { target: { value: 'john@example.com' } });
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /save changes/i }));

    // Check if success message appears
    expect(await screen.findByRole('alert')).toHaveTextContent(/profile updated successfully/i);

    // Verify message disappears after 3 seconds
    await waitFor(() => {
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    }, { timeout: 4000 });
  });

  test('validates email format', () => {
    render(<Profile />);
    
    const emailInput = screen.getByLabelText(/email:/i);
    
    // Test invalid email
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    expect(emailInput.validity.valid).toBeFalsy();
    
    // Test valid email
    fireEvent.change(emailInput, { target: { value: 'valid@email.com' } });
    expect(emailInput.validity.valid).toBeTruthy();
  });
});