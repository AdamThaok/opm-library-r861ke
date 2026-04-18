import React from 'react';

function HomePage() {
  return (
    <div className="text-center mt-10">
      <h1 className="text-4xl font-bold text-gray-800">Welcome to the OPM Library System</h1>
      <p className="mt-4 text-lg text-gray-600">Manage members, books, loans, reservations, and fines efficiently.</p>
      <div className="mt-8">
        <img src="https://via.placeholder.com/600x300?text=Library+System" alt="Library System" className="mx-auto rounded-lg shadow-lg" />
      </div>
      <div className="mt-8 flex justify-center space-x-4">
        <a href="/members" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">View Members</a>
        <a href="/books" className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">View Books</a>
        <a href="/loans" className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded">View Loans</a>
      </div>
    </div>
  );
}

export default HomePage;
