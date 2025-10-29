import './App.css';
import Profile from './components/Profile';

function App() {
  return (
    <div className="App">
      <header className="App-header" style={{ backgroundColor: '#282c34', minHeight: '100px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', marginBottom: '20px' }}>
        <h1>Niner Finance</h1>
      </header>
      <main>
        <Profile />
      </main>
    </div>
  );
}

export default App;
