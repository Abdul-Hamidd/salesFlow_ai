import { useState, useEffect } from 'react'
import axios from 'axios'
import { Users, TrendingUp, ShoppingCart, DollarSign, Bell, FileText, Download } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const API_URL =   'https://salesflow-ai.fastapicloud.dev'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [statsRes, notifRes] = await Promise.all([
        axios.get(`${API_URL}/dashboard/stats`),
        axios.get(`${API_URL}/dashboard/notifications`)
      ])
      setStats(statsRes.data)
      setNotifications(notifRes.data.notifications)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadReport = async () => {
    setDownloading(true)
    try {
      const response = await axios.get(`${API_URL}/dashboard/download-report`, {
        responseType: 'blob'
      })
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `CRM_Report_${new Date().toISOString().split('T')[0]}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error downloading report:', error)
      alert('Error downloading report!')
    } finally {
      setDownloading(false)
    }
  }

  if (loading) return <div className="loading">Loading...</div>

  const leadsChartData = stats ? [
    { name: 'Hot', value: stats.leads.hot, fill: '#e53e3e' },
    { name: 'Warm', value: stats.leads.warm, fill: '#dd6b20' },
    { name: 'Cold', value: stats.leads.cold, fill: '#3182ce' },
  ] : []

  return (
    <div>
      {/* Page Header */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Dashboard</h1>
          <p>Welcome back! Here is your business overview.</p>
        </div>
        {/* Download Report Button */}
        <button
          onClick={handleDownloadReport}
          disabled={downloading}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 20px',
            background: downloading ? '#ccc' : '#075e54',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            fontSize: '14px',
            fontWeight: '600',
            cursor: downloading ? 'not-allowed' : 'pointer',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
            transition: 'all 0.2s'
          }}
        >
          {downloading ? (
            <>
              <FileText size={18} />
              Generating...
            </>
          ) : (
            <>
              <Download size={18} />
              Download Report
            </>
          )}
        </button>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#e8f5e9' }}>
            <Users size={24} color="#25D366" />
          </div>
          <div className="stat-info">
            <h3>{stats?.total_contacts || 0}</h3>
            <p>Total Contacts</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fff0f0' }}>
            <TrendingUp size={24} color="#e53e3e" />
          </div>
          <div className="stat-info">
            <h3>{stats?.leads.hot || 0}</h3>
            <p>Hot Leads 🔥</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#f0f8ff' }}>
            <ShoppingCart size={24} color="#3182ce" />
          </div>
          <div className="stat-info">
            <h3>{stats?.total_orders || 0}</h3>
            <p>Total Orders</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fffff0' }}>
            <DollarSign size={24} color="#d69e2e" />
          </div>
          <div className="stat-info">
            <h3>Rs. {stats?.total_revenue || 0}</h3>
            <p>Total Revenue</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#f5f0ff' }}>
            <Bell size={24} color="#805ad5" />
          </div>
          <div className="stat-info">
            <h3>{stats?.unread_notifications || 0}</h3>
            <p>Notifications</p>
          </div>
        </div>
      </div>

      {/* Leads Chart */}
      <div className="card">
        <h2 style={{ marginBottom: '20px', fontSize: '18px' }}>Leads Overview</h2>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={leadsChartData}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#25D366" radius={[5, 5, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Notifications */}
      <div className="card">
        <h2 style={{ marginBottom: '20px', fontSize: '18px' }}>Recent Notifications</h2>
        {notifications.length === 0 ? (
          <p style={{ color: '#888', textAlign: 'center', padding: '20px' }}>
            No new notifications
          </p>
        ) : (
          <div>
            {notifications.slice(0, 5).map((notif) => (
              <div key={notif.id} style={{
                padding: '12px',
                borderBottom: '1px solid #f0f0f0',
                borderRadius: '8px',
                marginBottom: '8px',
                background: '#f8f9fa'
              }}>
                <strong style={{ fontSize: '14px' }}>{notif.title}</strong>
                <p style={{ fontSize: '13px', color: '#666', margin: '4px 0' }}>{notif.message}</p>
                <small style={{ color: '#aaa' }}>{new Date(notif.created_at).toLocaleString()}</small>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard