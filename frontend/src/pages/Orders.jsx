import { useState, useEffect } from 'react'
import axios from 'axios'
import { ShoppingCart, Package, CheckCircle, XCircle } from 'lucide-react'

const API_URL =  'https://salesflow-ai.fastapicloud.dev'

function Orders() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchOrders()
  }, [])

  const fetchOrders = async () => {
    try {
      const res = await axios.get(`${API_URL}/dashboard/orders`)
      setOrders(res.data.orders)
    } catch (error) {
      console.error('Error fetching orders:', error)
    } finally {
      setLoading(false)
    }
  }

  // Filter orders by status
  const filteredOrders = orders.filter(order =>
    filter === 'all' ? true : order.status === filter
  )

  const getStatusColor = (status) => {
    const colors = {
      pending: { bg: '#fff8f0', color: '#dd6b20' },
      confirmed: { bg: '#f0f8ff', color: '#3182ce' },
      shipped: { bg: '#f5f0ff', color: '#805ad5' },
      delivered: { bg: '#e8f5e9', color: '#25D366' },
      cancelled: { bg: '#fff0f0', color: '#e53e3e' }
    }
    return colors[status] || { bg: '#f0f2f5', color: '#888' }
  }

  if (loading) return <div className="loading">Loading...</div>

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1>Orders</h1>
        <p>Track all your customer orders.</p>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#e8f5e9' }}>
            <ShoppingCart size={24} color="#25D366" />
          </div>
          <div className="stat-info">
            <h3>{orders.length}</h3>
            <p>Total Orders</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fff8f0' }}>
            <Package size={24} color="#dd6b20" />
          </div>
          <div className="stat-info">
            <h3>{orders.filter(o => o.status === 'pending').length}</h3>
            <p>Pending Orders</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#e8f5e9' }}>
            <CheckCircle size={24} color="#25D366" />
          </div>
          <div className="stat-info">
            <h3>{orders.filter(o => o.status === 'delivered').length}</h3>
            <p>Delivered Orders</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fff0f0' }}>
            <XCircle size={24} color="#e53e3e" />
          </div>
          <div className="stat-info">
            <h3>{orders.filter(o => o.status === 'cancelled').length}</h3>
            <p>Cancelled Orders</p>
          </div>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="card" style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        {['all', 'pending', 'confirmed', 'shipped', 'delivered', 'cancelled'].map((f) => (
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

      {/* Orders Table */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Customer</th>
              <th>Phone</th>
              <th>Product</th>
              <th>Quantity</th>
              <th>Total Price</th>
              <th>Status</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {filteredOrders.length === 0 ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', color: '#888', padding: '30px' }}>
                  No orders found
                </td>
              </tr>
            ) : (
              filteredOrders.map((order) => (
                <tr key={order.id}>
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
                        {order.contacts?.name ? order.contacts.name[0].toUpperCase() : '?'}
                      </div>
                      {order.contacts?.name || 'Unknown'}
                    </div>
                  </td>
                  <td>{order.contacts?.phone_number || '—'}</td>
                  <td>{order.products?.name || '—'}</td>
                  <td>{order.quantity}</td>
                  <td><strong>Rs. {order.total_price || 0}</strong></td>
                  <td>
                    <span style={{
                      padding: '4px 10px',
                      borderRadius: '20px',
                      fontSize: '12px',
                      fontWeight: '600',
                      background: getStatusColor(order.status).bg,
                      color: getStatusColor(order.status).color
                    }}>
                      {order.status.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ color: '#888', fontSize: '13px' }}>
                    {new Date(order.created_at).toLocaleDateString()}
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

export default Orders