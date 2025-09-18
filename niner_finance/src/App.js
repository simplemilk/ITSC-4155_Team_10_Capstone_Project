import logo from './logo.svg';
import './App.css';
import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import ResetPasswordRequest from './ResetPasswordRequest';
import ResetPassword from './ResetPassword';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <p>
            Edit <code>src/App.js</code> and save to reload.
          </p>
          <a
            className="App-link"
            href="https://reactjs.org"
            target="_blank"
            rel="noopener noreferrer"
          >
            Learn React
          </a>
        </header>

        <Switch>
          <Route path="/" exact component={ResetPasswordRequest} />
          
          <Route path="/reset-password/:token" component={ResetPassword} />
        </Switch>
      </div>
    </Router>
  );
}

export default App;
