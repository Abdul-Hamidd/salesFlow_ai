import { useState, useEffect } from 'react'
import { Settings as SettingsIcon, Save, Clock, MessageSquare } from 'lucide-react'

function Settings() {
  const [settings, setSettings] = useState({
    business_name: '',
    greeting_message: '',
    follow_up_hours: 24,
    working_hours_start: '09:00',
    working_hours_end: '18:00'
  })
  const [saved, setSaved] = useState(false)

  const handleChange = (e) => {
    setSettings({ ...settings, [e.target.name]: e.target.value })
  }

  const handleSave = () => {
    // Save to localStorage for now
    localStorage.setItem('business_settings', JSON.stringify(settings))
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  useEffect(() => {
    const saved = localStorage.getItem('business_settings')
    if (saved) setSettings(JSON.parse(saved))
  }, [])

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1>Settings</h1>
        <p>Configure your WhatsApp CRM system.</p>
      </div>

      {/* Business Settings */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
          <SettingsIcon size={20} color="#25D366" />
          <h2 style={{ fontSize: '16px' }}>Business Settings</h2>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <div>
            <label style={{ fontSize: '13px', color: '#666', marginBottom: '5px', display: 'block' }}>
              Business Name
            </label>
            <input
              type="text"
              name="business_name"
              value={settings.business_name}
              onChange={handleChange}
              placeholder="Enter your business name"
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

          <div>
            <label style={{ fontSize: '13px', color: '#666', marginBottom: '5px', display: 'block' }}>
              Greeting Message
            </label>
            <textarea
              name="greeting_message"
              value={settings.greeting_message}
              onChange={handleChange}
              placeholder="Hello! Welcome to our store. How can I help you today?"
              rows={3}
              style={{
                width: '100%',
                padding: '10px 15px',
                border: '1px solid #eee',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none',
                resize: 'vertical'
              }}
            />
          </div>
        </div>
      </div>

      {/* Follow Up Settings */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
          <Clock size={20} color="#25D366" />
          <h2 style={{ fontSize: '16px' }}>Follow Up Settings</h2>
        </div>

        <div>
          <label style={{ fontSize: '13px', color: '#666', marginBottom: '5px', display: 'block' }}>
            Default Follow Up Hours
          </label>
          <select
            name="follow_up_hours"
            value={settings.follow_up_hours}
            onChange={handleChange}
            style={{
              width: '100%',
              padding: '10px 15px',
              border: '1px solid #eee',
              borderRadius: '8px',
              fontSize: '14px',
              outline: 'none'
            }}
          >
            <option value={2}>2 Hours (Hot Leads)</option>
            <option value={24}>24 Hours (Warm Leads)</option>
            <option value={72}>72 Hours (Cold Leads)</option>
          </select>
        </div>
      </div>

      {/* Working Hours */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
          <MessageSquare size={20} color="#25D366" />
          <h2 style={{ fontSize: '16px' }}>Working Hours</h2>
        </div>

        <div style={{ display: 'flex', gap: '15px' }}>
          <div style={{ flex: 1 }}>
            <label style={{ fontSize: '13px', color: '#666', marginBottom: '5px', display: 'block' }}>
              Start Time
            </label>
            <input
              type="time"
              name="working_hours_start"
              value={settings.working_hours_start}
              onChange={handleChange}
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

          <div style={{ flex: 1 }}>
            <label style={{ fontSize: '13px', color: '#666', marginBottom: '5px', display: 'block' }}>
              End Time
            </label>
            <input
              type="time"
              name="working_hours_end"
              value={settings.working_hours_end}
              onChange={handleChange}
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
        </div>
      </div>

      {/* Save Button */}
      <button
        onClick={handleSave}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '12px 30px',
          background: saved ? '#25D366' : '#25D366',
          color: 'white',
          border: 'none',
          borderRadius: '10px',
          fontSize: '15px',
          fontWeight: '600',
          cursor: 'pointer'
        }}
      >
        <Save size={18} />
        {saved ? 'Saved! ✅' : 'Save Settings'}
      </button>
    </div>
  )
}

export default Settings