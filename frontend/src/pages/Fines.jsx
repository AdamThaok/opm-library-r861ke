import React, { useState, useEffect } from 'react';
import api from '../api';

function FinesPage() {
  const [fines, setFines] = useState([]);
  const [members, setMembers] = useState([]);
  const [loans, setLoans] = useState([]);
  const [newFine, setNewFine] = useState({ member_id: '', loan_id: '', amount: '', reason: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [finesRes, membersRes, loansRes] = await Promise.all([
        api.get('/fines/'),
        api.get('/members/'),
        api.get('/loans/'),
      ]);
      setFines(finesRes.data);
      setMembers(membersRes.data);
      setLoans(loansRes.data.filter(loan => loan.status === 'Active' || loan.status === 'Overdue')); // Only active/overdue loans for fines
      setError('');
    } catch (err) {
      setError('Failed to fetch data.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateFine = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const fineData = { ...newFine, amount: parseFloat(newFine.amount) };
      if (!fineData.loan_id) {
        delete fineData.loan_id; // Send null or omit if not selected
      }
      await api.post('/fines/', fineData);
      setNewFine({ member_id: '', loan_id: '', amount: '', reason: '' });
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to issue fine.');
      console.error(err);
    }
  };

  const handlePayFine = async (fineId) => {
    setError('');
    if (!window.confirm('Are you sure you want to mark this fine as paid?')) return;
    try {
      await api.post(`/fines/${fineId}/pay`);
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to pay fine.');
      console.error(err);
    }
  };

  if (loading) return <div className="text-center mt-8">Loading fines...</div>;

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6">Fines</h1>

      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">{error}</div>}

      <div className="mb-8 p-6 bg-white shadow-md rounded-lg">
        <h2 className="text-2xl font-semibold mb-4">Issue Fine (P5)</h2>
        <form onSubmit={handleCreateFine} className="space-y-4">
          <div>
            <label htmlFor="member_id" className="block text-sm font-medium text-gray-700">Member</label>
            <select
              id="member_id"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              value={newFine.member_id}
              onChange={(e) => setNewFine({ ...newFine, member_id: e.target.value })}
              required
            >
              <option value="">Select a Member</option>
              {members.map((member) => (
                <option key={member.id} value={member.id}>{member.name} ({member.email})</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="loan_id" className="block text-sm font-medium text-gray-700">Associated Loan (Optional)</label>
            <select
              id="loan_id"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              value={newFine.loan_id}
              onChange={(e) => setNewFine({ ...newFine, loan_id: e.target.value })}
            >
              <option value="">No specific loan</option>
              {loans.map((loan) => (
                <option key={loan.id} value={loan.id}>
                  {loan.member.name} - {loan.book.title} (Status: {loan.status})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="amount" className="block text-sm font-medium text-gray-700">Amount</label>
            <input
              type="number"
              id="amount"
              step="0.01"
              min="0.01"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              value={newFine.amount}
              onChange={(e) => setNewFine({ ...newFine, amount: e.target.value })}
              required
            />
          </div>
          <div>
            <label htmlFor="reason" className="block text-sm font-medium text-gray-700">Reason</label>
            <input
              type="text"
              id="reason"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              value={newFine.reason}
              onChange={(e) => setNewFine({ ...newFine, reason: e.target.value })}
              required
            />
          </div>
          <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            Issue Fine
          </button>
        </form>
      </div>

      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-semibold mb-4">All Fines</h2>
        {fines.length === 0 ? (
          <p>No fines found.</p>
        ) : (
          <ul className="divide-y divide-gray-200">
            {fines.map((fine) => (
              <li key={fine.id} className="py-4 flex justify-between items-center">
                <div>
                  <p className="text-lg font-medium text-gray-900">Member: {fine.member.name}</p>
                  <p className="text-md text-gray-700">Reason: {fine.reason}</p>
                  <p className="text-sm text-gray-500">Amount: ${fine.amount}</p>
                  {fine.loan && <p className="text-sm text-gray-500">Loan: {fine.loan.book.title} (ID: {fine.loan.id.substring(0, 8)}...)</p>}
                  <p className={`font-semibold ${fine.status === 'Unpaid' ? 'text-red-600' : 'text-green-600'}`}>Status: {fine.status}</p>
                </div>
                {fine.status === 'Unpaid' && (
                  <button
                    onClick={() => handlePayFine(fine.id)}
                    className="bg-green-600 text-white px-3 py-1 rounded-md hover:bg-green-700 text-sm"
                  >
                    Pay Fine (P6)
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

export default FinesPage;
