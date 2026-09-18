import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Users, 
  TrendingUp, 
  ShoppingCart, 
  Settings,
  MessageSquare,
  LogOut,
  MessagesSquare,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { useState } from 'react'
import supabase from '../supabaseClient'

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/conversations', icon: MessagesSquare, label: 'Conversations' },
  { path: '/contacts', icon: Users, label: 'Contacts' },
  { path: '/leads', icon: TrendingUp, label: 'Leads' },
  { path: '/orders', icon: ShoppingCart, label: 'Orders' },
  { path: '/settings', icon: Settings, label: 'Settings' },
]

function Navbar({ user, onCollapse }) {
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)

  const handleCollapse = () => {
    setCollapsed(!collapsed)
    onCollapse(!collapsed)
  }

  const handleLogout = async () => {
    await supabase.auth.signOut()
    window.location.href = '/'
  }

  return (
    <nav style={{
      width: collapsed ? '70px' : '250px',
      height: '100vh',
      background: 'white',
      position: 'fixed',
      left: 0,
      top: 0,
      display: 'flex',
      flexDirection: 'column',
      padding: '20px 0',
      boxShadow: '2px 0 10px rgba(0,0,0,0.08)',
      zIndex: 100,
      transition: 'width 0.3s ease',
      overflow: 'hidden'
    }}>
      {/* Logo + Collapse Button */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: collapsed ? 'center' : 'space-between',
        padding: collapsed ? '0 0 20px 0' : '0 15px 20px 20px',
        borderBottom: '1px solid #f0f0f0',
        minHeight: '50px'
      }}>
        {!collapsed && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <MessageSquare size={24} color="#25D366" />
            <span style={{ fontSize: '16px', fontWeight: '700', color: '#333', whiteSpace: 'nowrap' }}>
              WhatsApp CRM
            </span>
          </div>
        )}
        {collapsed && <MessageSquare size={24} color="#25D366" />}
        
        <button
          onClick={handleCollapse}
          style={{
            background: '#f0f2f5',
            border: 'none',
            borderRadius: '50%',
            width: '28px',
            height: '28px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            marginLeft: collapsed ? '0' : '5px'
          }}
        >
          {collapsed ? <ChevronRight size={16} color="#666" /> : <ChevronLeft size={16} color="#666" />}
        </button>
      </div>

      {/* Navigation Items */}
      <ul style={{ listStyle: 'none', padding: '20px 10px', flex: 1, margin: 0 }}>
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          return (
            <li key={item.path} style={{ marginBottom: '5px' }}>
              <Link
                to={item.path}
                title={collapsed ? item.label : ''}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: collapsed ? '0' : '12px',
                  padding: collapsed ? '12px' : '12px 15px',
                  borderRadius: '10px',
                  textDecoration: 'none',
                  color: isActive ? '#25D366' : '#888',
                  background: isActive ? '#e8f5e9' : 'transparent',
                  fontSize: '14px',
                  fontWeight: '500',
                  transition: 'all 0.2s',
                  justifyContent: collapsed ? 'center' : 'flex-start',
                  whiteSpace: 'nowrap'
                }}
              >
                <Icon size={20} />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            </li>
          )
        })}
      </ul>

      {/* User Info + Logout */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: collapsed ? '15px 10px' : '15px 20px',
        borderTop: '1px solid #f0f0f0',
        justifyContent: collapsed ? 'center' : 'space-between'
      }}>
        {!collapsed && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1, minWidth: 0 }}>
            <div style={{
              width: '8px', height: '8px',
              borderRadius: '50%', background: '#25D366', flexShrink: 0
            }}></div>
            <span style={{
              fontSize: '12px', color: '#888',
              overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'
            }}>
              {user?.email?.split('@')[0]}
            </span>
          </div>
        )}
        <button
          onClick={handleLogout}
          title="Logout"
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: '#e53e3e',
            display: 'flex',
            alignItems: 'center',
            padding: '5px',
            flexShrink: 0
          }}
        >
          <LogOut size={18} />
        </button>
      </div>
    </nav>
  )
}

export default Navbar