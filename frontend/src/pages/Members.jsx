import React, { useState, useEffect } from 'react';
import api from '../api';

function MembersPage() {
  const [members, setMembers] = useState([]);
  const [newMember, setNewMember] = useState({ name: '', email: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMembers();
  }, []);

  const fetchMembers = async () => {
    setLoading(true);
    try {
      const response = await api.get('/members/');
      setMembers(response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch members.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMember = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/members/', newMember);
      setNewMember({ name: '', email: '' });
      fetchMembers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create member.');
      console.error(err);
    }
  };

  if (loading) return <div className="text-center mt-8">Loading members...</div>;

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6">Members</h1>

      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">{error}</div>}

      <div className="mb-8 p-6 bg-white shadow-md rounded-lg">
        <h2 className="text-2xl font-semibold mb-4">Add New Member</h2>
        <form onSubmit={handleCreateMember} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">Name</label>
            <input
              type="text"
              id="name"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              value={newMember.name}
              onChange={(e) => setNewMember({ ...newMember, name: e.target.value })}
              required
            />
          </div>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              id="email"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              value={newMember.email}
              onChange={(e) => setNewMember({ ...newMember, email: e.target.value })}
              required
            />
          </div>
          <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            Create Member
          </button>
        </form>
      </div>

      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-semibold mb-4">All Members</h2>
        {members.length === 0 ? (
          <p>No members found.</p>
        ) : (
          <ul className="divide-y divide-gray-200">
            {members.map((member) => (
              <li key={member.id} className="py-4 flex justify-between items-center">
                <div>
                  <p className="text-lg font-medium text-gray-900">{member.name}</p>
                  <p className="text-sm text-gray-500">{member.email}</p>
                </div>
                <span className="text-xs text-gray-400">ID: {member.id.substring(0, 8)}...</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default MembersPage;
