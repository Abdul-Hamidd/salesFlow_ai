import { useState, useEffect } from 'react'
import axios from 'axios'
import { TrendingUp } from 'lucide-react'

const API_URL =  'https://salesflow-ai.fastapicloud.dev'

function Leads() {
  const [leads, setLeads] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchLeads()
  }, [])

  const fetchLeads = async () => {
    try {
      const res = await axios.get(`${API_URL}/dashboard/leads`)
      setLeads(res.data.leads)
    } catch (error) {
      console.error('Error fetching leads:', error)
    } finally {
      setLoading(false)
    }
  }

  // Filter leads by status
  const filteredLeads = leads.filter(lead =>
    filter === 'all' ? true : lead.status === filter
  )

  const hotCount = leads.filter(l => l.status === 'hot').length
  const warmCount = leads.filter(l => l.status === 'warm').length
  const coldCount = leads.filter(l => l.status === 'cold').length

  if (loading) return <div className="loading">Loading...</div>

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1>Leads</h1>
        <p>Track and manage your sales leads.</p>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fff0f0' }}>
            <TrendingUp size={24} color="#e53e3e" />
          </div>
          <div className="stat-info">
            <h3>{hotCount}</h3>
            <p>Hot Leads 🔥</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fff8f0' }}>
            <TrendingUp size={24} color="#dd6b20" />
          </div>
          <div className="stat-info">
            <h3>{warmCount}</h3>
            <p>Warm Leads ⚡</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#f0f8ff' }}>
            <TrendingUp size={24} color="#3182ce" />
          </div>
          <div className="stat-info">
            <h3>{coldCount}</h3>
            <p>Cold Leads ❄️</p>
          </div>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="card" style={{ display: 'flex', gap: '10px' }}>
        {['all', 'hot', 'warm', 'cold'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: '8px 20px',
              borderRadius: '20px',
              border: 'none',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '13px',
              background: filter === f ? '#25D366' : '#f0f2f5',
              color: filter === f ? 'white' : '#888',
              transition: 'all 0.2s'
            }}
          >
            {f.toUpperCase()}
          </button>
        ))}
      </div>

      {/* Leads Table */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Customer</th>
              <th>Phone</th>
              <th>Score</th>
              <th>Status</th>
              <th>Notes</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {filteredLeads.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', color: '#888', padding: '30px' }}>
                  No leads found
                </td>
              </tr>
            ) : (
              filteredLeads.map((lead) => (
                <tr key={lead.id}>
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
                        fontWeight: '600'
                      }}>
                        {lead.contacts?.name ? lead.contacts.name[0].toUpperCase() : '?'}
                      </div>
                      {lead.contacts?.name || 'Unknown'}
                    </div>
                  </td>
                  <td>{lead.contacts?.phone_number || '—'}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{
                        width: '80px',
                        height: '6px',
                        borderRadius: '3px',
                        background: '#f0f0f0',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          width: `${lead.score}%`,
                          height: '100%',
                          background: lead.score >= 71 ? '#e53e3e' : lead.score >= 41 ? '#dd6b20' : '#3182ce',
                          borderRadius: '3px'
                        }} />
                      </div>
                      <strong>{lead.score}/100</strong>
                    </div>
                  </td>
                  <td>
                    <span className={`badge badge-${lead.status}`}>
                      {lead.status.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ color: '#888', fontSize: '13px', maxWidth: '200px' }}>
                    {lead.notes || '—'}
                  </td>
                  <td style={{ color: '#888', fontSize: '13px' }}>
                    {new Date(lead.created_at).toLocaleDateString()}
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

export default Leads