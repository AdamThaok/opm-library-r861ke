import React, { useState, useEffect } from 'react';
import api from '../api';

function ReservationsPage() {
  const [reservations, setReservations] = useState([]);
  const [members, setMembers] = useState([]);
  const [books, setBooks] = useState([]);
  const [newReservation, setNewReservation] = useState({ member_id: '', book_id: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [reservationsRes, membersRes, booksRes] = await Promise.all([
        api.get('/reservations/'),
        api.get('/members/'),
        api.get('/books/'),
      ]);
      setReservations(reservationsRes.data);
      setMembers(membersRes.data);
      setBooks(booksRes.data.filter(book => book.status === 'Available')); // Only show available books for new reservations
      setError('');
    } catch (err) {
      setError('Failed to fetch data.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateReservation = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/reservations/', newReservation);
      setNewReservation({ member_id: '', book_id: '' });
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create reservation.');
      console.error(err);
    }
  };

  const handleCancelReservation = async (reservationId) => {
    setError('');
    if (!window.confirm('Are you sure you want to cancel this reservation?')) return;
    try {
      await api.post(`/reservations/${reservationId}/cancel`);
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to cancel reservation.');
      console.error(err);
    }
  };

  if (loading) return <div className="text-center mt-8">Loading reservations...</div>;

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6">Reservations</h1>

      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">{error}</div>}

      <div className="mb-8 p-6 bg-white shadow-md rounded-lg">
        <h2 className="text-2xl font-semibold mb-4">Reserve Book (P3)</h2>
        <form onSubmit={handleCreateReservation} className="space-y-4">
          <div>
            <label htmlFor="member_id" className="block text-sm font-medium text-gray-700">Member</label>
            <select
              id="member_id"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              value={newReservation.member_id}
              onChange={(e) => setNewReservation({ ...newReservation, member_id: e.target.value })}
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
              value={newReservation.book_id}
              onChange={(e) => setNewReservation({ ...newReservation, book_id: e.target.value })}
              required
            >
              <option value="">Select an Available Book</option>
              {books.map((book) => (
                <option key={book.id} value={book.id}>{book.title} by {book.author}</option>
              ))}
            </select>
          </div>
          <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            Reserve Book
          </button>
        </form>
      </div>

      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-semibold mb-4">All Reservations</h2>
        {reservations.length === 0 ? (
          <p>No reservations found.</p>
        ) : (
          <ul className="divide-y divide-gray-200">
            {reservations.map((reservation) => (
              <li key={reservation.id} className="py-4 flex justify-between items-center">
                <div>
                  <p className="text-lg font-medium text-gray-900">Book: {reservation.book.title} ({reservation.book.isbn})</p>
                  <p className="text-md text-gray-700">Member: {reservation.member.name} ({reservation.member.email})</p>
                  <p className="text-sm text-gray-500">Reservation Date: {new Date(reservation.reservation_date).toLocaleDateString()}</p>
                  <p className={`font-semibold ${reservation.status === 'Pending' ? 'text-yellow-600' : 'text-gray-600'}`}>Status: {reservation.status}</p>
                </div>
                {reservation.status === 'Pending' && (
                  <button
                    onClick={() => handleCancelReservation(reservation.id)}
                    className="bg-red-600 text-white px-3 py-1 rounded-md hover:bg-red-700 text-sm"
                  >
                    Cancel Reservation (P4)
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

export default ReservationsPage;
