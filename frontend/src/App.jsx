import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Fragment } from 'react';
import { Disclosure, Menu, Transition } from '@headlessui/react';
import { Bars3Icon, XMarkIcon, UserCircleIcon } from '@heroicons/react/24/outline';
import Dashboard from './components/Dashboard';
import ResumeJDUploader from './components/Input';

const navigation = [
  { name: 'Dashboard', href: '/' },
  { name: 'Job Descriptions', href: '/jobs' },
  { name: 'CV Management', href: '/cvs' },
  { name: 'Resume Matches', href: '/matches' },
  { name: 'Interviews', href: '/interviews' },
];
// adding a comment to test git commit
function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

function AppContent() {
  const location = useLocation();

  return (
    
      <div><ResumeJDUploader/></div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;