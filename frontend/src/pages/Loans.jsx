import React, { useState, useEffect } from 'react';
import api from '../api';

function LoansPage() {
  const [loans, setLoans] = useState([]);
  const [members, setMembers] = useState([]);
  const [books, setBooks] = useState([]);
  const [newLoan, setNewLoan] = useState({ member_id: '', book_id: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [loansRes, membersRes, booksRes] = await Promise.all([
        api.get('/loans/'),
        api.get('/members/'),
        api.get('/books/'),
      ]);
      setLoans(loansRes.data);
      setMembers(membersRes.data);
      setBooks(booksRes.data.filter(book => book.status === 'Available')); // Only show available books for new loans
      setError('');
    } catch (err) {
      setError('Failed to fetch data.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLoan = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/loans/', newLoan);
      setNewLoan({ member_id: '', book_id: '' });
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create loan.');
      console.error(err);
    }
  };

  const handleReturnLoan = async (loanId) => {
    setError('');
    if (!window.confirm('Are you sure you want to return this book?')) return;
    try {
      await api.post(`/loans/${loanId}/return`);
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to return loan.');
      console.error(err);
    }
  };

  if (loading) return <div className="text-center mt-8">Loading loans...</div>;

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6">Loans</h1>

      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">{error}</div>}

      <div className="mb-8 p-6 bg-white shadow-md rounded-lg">
        <h2 className="text-2xl font-semibold mb-4">Borrow Book (P1)</h2>
        <form onSubmit={handleCreateLoan} className="space-y-4">
          <div>
            <label htmlFor="member_id" className="block text-sm font-medium text-gray-700">Member</label>
            <select
              id="member_id"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              value={newLoan.member_id}
              onChange={(e) => setNewLoan({ ...newLoan, member_id: e.target.value })}
              required
            >
              <option value="">Select a Member</option>
              {members.map((member) => (
                <option key={member.id} value={member.id}>{member.name} ({member.email})</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="book_id" className="block text-sm font-medium text-gray-700">Book (Available)</label>
            <select
              id="book_id"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              value={newLoan.book_id}
              onChange={(e) => setNewLoan({ ...newLoan, book_id: e.target.value })}
              required
            >
              <option value="">Select an Available Book</option>
              {books.map((book) => (
                <option key={book.id} value={book.id}>{book.title} by {book.author}</option>
              ))}
            </select>
          </div>
          <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            Borrow Book
          </button>
        </form>
      </div>

      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-semibold mb-4">All Loans</h2>
        {loans.length === 0 ? (
          <p>No loans found.</p>
        ) : (
          <ul className="divide-y divide-gray-200">
            {loans.map((loan) => (
              <li key={loan.id} className="py-4 flex justify-between items-center">
                <div>
                  <p className="text-lg font-medium text-gray-900">Book: {loan.book.title} ({loan.book.isbn})</p>
                  <p className="text-md text-gray-700">Member: {loan.member.name} ({loan.member.email})</p>
                  <p className="text-sm text-gray-500">Loan Date: {new Date(loan.loan_date).toLocaleDateString()} - Due Date: {new Date(loan.due_date).toLocaleDateString()}</p>
                  {loan.return_date && <p className="text-sm text-gray-500">Return Date: {new Date(loan.return_date).toLocaleDateString()}</p>}
                  <p className={`font-semibold ${loan.status === 'Active' ? 'text-blue-600' : loan.status === 'Returned' ? 'text-green-600' : 'text-red-600'}`}>Status: {loan.status}</p>
                </div>
                {loan.status === 'Active' && (
                  <button
                    onClick={() => handleReturnLoan(loan.id)}
                    className="bg-green-600 text-white px-3 py-1 rounded-md hover:bg-green-700 text-sm"
                  >
                    Return Book (P2)
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default LoansPage;
