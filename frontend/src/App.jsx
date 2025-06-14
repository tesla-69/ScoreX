import React from 'react';
import ResumeUploader from './components/ResumeUploader';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Resume Parser</h1>
      </header>
      <main>
        <ResumeUploader />
      </main>
    </div>
  );
}

export default App;