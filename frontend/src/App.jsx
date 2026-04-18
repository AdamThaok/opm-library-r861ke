import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import MembersPage from './pages/Members';
import BooksPage from './pages/Books';
import LoansPage from './pages/Loans';
import ReservationsPage from './pages/Reservations';
import FinesPage from './pages/Fines';
import Navbar from './components/Navbar';

function App() {
  return (
    <Router>
      <Navbar />
      <div className="container mx-auto p-4">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/members" element={<MembersPage />} />
          <Route path="/books" element={<BooksPage />} />
          <Route path="/loans" element={<LoansPage />} />
          <Route path="/reservations" element={<ReservationsPage />} />
          <Route path="/fines" element={<FinesPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
