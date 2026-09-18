import { useState, useEffect } from 'react'
import axios from 'axios'
import { Users, Phone, Mail, MapPin } from 'lucide-react'

const API_URL =  'https://salesflow-ai.fastapicloud.dev'

function Contacts() {
  const [contacts, setContacts] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetchContacts()
  }, [])

  const fetchContacts = async () => {
    try {
      const res = await axios.get(`${API_URL}/dashboard/contacts`)
      setContacts(res.data.contacts)
    } catch (error) {
      console.error('Error fetching contacts:', error)
    } finally {
      setLoading(false)
    }
  }

  // Filter contacts by search
  const filteredContacts = contacts.filter(contact =>
    contact.name?.toLowerCase().includes(search.toLowerCase()) ||
    contact.phone_number?.includes(search)
  )

  if (loading) return <div className="loading">Loading...</div>

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1>Contacts</h1>
        <p>All your WhatsApp customers in one place.</p>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#e8f5e9' }}>
            <Users size={24} color="#25D366" />
          </div>
          <div className="stat-info">
            <h3>{contacts.length}</h3>
            <p>Total Contacts</p>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="card">
        <input
          type="text"
          placeholder="Search by name or phone number..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            width: '100%',
            padding: '10px 15px',
            border: '1px solid #eee',
            borderRadius: '8px',
            fontSize: '14px',
            outline: 'none'
          }}
        />
      </div>

      {/* Contacts Table */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Phone Number</th>
              <th>Email</th>
              <th>City</th>
              <th>Lead Status</th>
              <th>Lead Score</th>
              <th>Joined</th>
            </tr>
          </thead>
          <tbody>
            {filteredContacts.length === 0 ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', color: '#888', padding: '30px' }}>
                  No contacts found
                </td>
              </tr>
            ) : (
              filteredContacts.map((contact) => (
                <tr key={contact.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{
                        width: '35px',
                        height: '35px',
                        borderRadius: '50%',
                        background: '#25D366',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontWeight: '600',
                        fontSize: '14px'
                      }}>
                        {contact.name ? contact.name[0].toUpperCase() : '?'}
                      </div>
                      {contact.name || 'Unknown'}
                    </div>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <Phone size={14} color="#888" />
                      {contact.phone_number}
                    </div>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <Mail size={14} color="#888" />
                      {contact.email || '—'}
                    </div>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <MapPin size={14} color="#888" />
                      {contact.city || '—'}
                    </div>
                  </td>
                  <td>
                    {contact.leads?.[0] ? (
                      <span className={`badge badge-${contact.leads[0].status}`}>
                        {contact.leads[0].status.toUpperCase()}
                      </span>
                    ) : (
                      <span style={{ color: '#888' }}>—</span>
                    )}
                  </td>
                  <td>
                    {contact.leads?.[0] ? (
                      <strong>{contact.leads[0].score}/100</strong>
                    ) : (
                      <span style={{ color: '#888' }}>—</span>
                    )}
                  </td>
                  <td style={{ color: '#888', fontSize: '13px' }}>
                    {new Date(contact.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Contacts