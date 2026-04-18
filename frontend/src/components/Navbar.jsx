import React from 'react';
import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav className="bg-gray-800 p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-white text-xl font-bold">OPM Library</Link>
        <div className="space-x-4">
          <Link to="/members" className="text-gray-300 hover:text-white">Members</Link>
          <Link to="/books" className="text-gray-300 hover:text-white">Books</Link>
          <Link to="/loans" className="text-gray-300 hover:text-white">Loans</Link>
          <Link to="/reservations" className="text-gray-300 hover:text-white">Reservations</Link>
          <Link to="/fines" className="text-gray-300 hover:text-white">Fines</Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
