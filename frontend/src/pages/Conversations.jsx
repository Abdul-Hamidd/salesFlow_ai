import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { Send, Phone, Search, MessageSquare, RefreshCw, MoreVertical } from 'lucide-react'

const API_URL =  'https://salesflow-ai.fastapicloud.dev'

function Conversations() {
  const [contacts, setContacts] = useState([])
  const [selectedContact, setSelectedContact] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [search, setSearch] = useState('')
  const [lastUpdate, setLastUpdate] = useState(null)
  const messagesEndRef = useRef(null)
  const selectedContactRef = useRef(null)

  useEffect(() => { fetchContacts() }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      if (selectedContactRef.current) fetchMessages(selectedContactRef.current.id)
      fetchContacts()
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (selectedContact) {
      selectedContactRef.current = selectedContact
      fetchMessages(selectedContact.id)
    }
  }, [selectedContact])

  useEffect(() => { scrollToBottom() }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchContacts = async () => {
    try {
      const res = await axios.get(`${API_URL}/dashboard/contacts`)
      setContacts(res.data.contacts)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  const fetchMessages = async (contactId) => {
    try {
      const res = await axios.get(`${API_URL}/dashboard/conversations/${contactId}`)
      setMessages(res.data.conversations.reverse())
      setLastUpdate(new Date().toLocaleTimeString())
    } catch (e) { console.error(e) }
  }

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedContact) return
    setSending(true)
    try {
      await axios.post(`${API_URL}/dashboard/send-message`, {
        phone_number: selectedContact.phone_number,
        message: newMessage,
        contact_id: selectedContact.id
      })
      setNewMessage('')
      fetchMessages(selectedContact.id)
    } catch (e) { console.error(e) }
    finally { setSending(false) }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const filteredContacts = contacts.filter(c =>
    c.name?.toLowerCase().includes(search.toLowerCase()) ||
    c.phone_number?.includes(search)
  )

  const statusColor = { hot: '#e53e3e', warm: '#dd6b20', cold: '#3182ce' }
  const sentimentBg = { positive: '#e8f5e9', negative: '#fff0f0', urgent: '#fff8f0', neutral: 'white' }

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
      <p style={{ color: '#25D366', fontSize: '16px' }}>Loading...</p>
    </div>
  )

  return (
    <div style={{
      position: 'fixed',
      top: 0, bottom: 0,
      left: 0, right: 0,
      marginLeft: '250px',
      display: 'flex',
      flexDirection: 'column',
      background: '#f0f2f5',
      zIndex: 1
    }}>
      {/* Top Bar */}
      <div style={{
        height: '56px',
        background: '#075e54',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 20px',
        flexShrink: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <MessageSquare size={22} color="white" />
          <span style={{ color: 'white', fontWeight: '600', fontSize: '18px' }}>
            Conversations
          </span>
        </div>
        {lastUpdate && (
          <span style={{ color: 'rgba(255,255,255,0.7)', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '5px' }}>
            <RefreshCw size={11} />
            {lastUpdate}
          </span>
        )}
      </div>

      {/* Main Body */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

        {/* LEFT — Contacts */}
        <div style={{
          width: '360px',
          background: 'white',
          display: 'flex',
          flexDirection: 'column',
          borderRight: '1px solid #e0e0e0',
          flexShrink: 0
        }}>
          {/* Search Bar */}
          <div style={{ padding: '8px 12px', background: '#f0f2f5' }}>
            <div style={{ position: 'relative' }}>
              <Search size={16} color="#888" style={{
                position: 'absolute', left: '12px',
                top: '50%', transform: 'translateY(-50%)'
              }} />
              <input
                type="text"
                placeholder="Search or start new chat"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{
                  width: '100%',
                  padding: '9px 12px 9px 38px',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none',
                  background: 'white',
                  boxSizing: 'border-box'
                }}
              />
            </div>
          </div>

          {/* Contact List */}
          <div style={{ flex: 1, overflowY: 'auto' }}>
            {filteredContacts.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 20px', color: '#888' }}>
                <MessageSquare size={40} color="#ddd" style={{ marginBottom: '10px' }} />
                <p>No contacts found</p>
              </div>
            ) : (
              filteredContacts.map(contact => (
                <div
                  key={contact.id}
                  onClick={() => setSelectedContact(contact)}
                  style={{
                    padding: '13px 16px',
                    cursor: 'pointer',
                    borderBottom: '1px solid #f5f5f5',
                    background: selectedContact?.id === contact.id ? '#f0f2f5' : 'white',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '14px',
                    transition: 'background 0.15s'
                  }}
                >
                  <div style={{
                    width: '50px', height: '50px',
                    borderRadius: '50%',
                    background: selectedContact?.id === contact.id ? '#25D366' : '#dfe5e7',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: selectedContact?.id === contact.id ? 'white' : '#555',
                    fontWeight: '700', fontSize: '20px',
                    flexShrink: 0
                  }}>
                    {contact.name ? contact.name[0].toUpperCase() : '?'}
                  </div>

                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <p style={{
                        fontWeight: '600', fontSize: '15px',
                        color: '#111', margin: 0,
                        whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'
                      }}>
                        {contact.name || 'Unknown'}
                      </p>
                      {contact.leads?.[0] && (
                        <span style={{
                          fontSize: '11px', fontWeight: '600',
                          color: statusColor[contact.leads[0].status] || '#888',
                          flexShrink: 0, marginLeft: '8px'
                        }}>
                          {contact.leads[0].status.toUpperCase()}
                        </span>
                      )}
                    </div>
                    <p style={{
                      fontSize: '13px', color: '#888',
                      margin: '3px 0 0 0',
                      display: 'flex', alignItems: 'center', gap: '4px'
                    }}>
                      <Phone size={11} />
                      {contact.phone_number}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* RIGHT — Chat */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {selectedContact ? (
            <>
              {/* Chat Header */}
              <div style={{
                height: '60px',
                background: '#075e54',
                display: 'flex',
                alignItems: 'center',
                padding: '0 16px',
                gap: '14px',
                flexShrink: 0
              }}>
                <div style={{
                  width: '42px', height: '42px',
                  borderRadius: '50%', background: '#25D366',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'white', fontWeight: '700', fontSize: '18px'
                }}>
                  {selectedContact.name ? selectedContact.name[0].toUpperCase() : '?'}
                </div>
                <div style={{ flex: 1 }}>
                  <p style={{ fontWeight: '600', fontSize: '16px', color: 'white', margin: 0 }}>
                    {selectedContact.name || 'Unknown'}
                  </p>
                  <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)', margin: '1px 0 0 0' }}>
                    {selectedContact.phone_number}
                  </p>
                </div>
                {selectedContact.leads?.[0] && (
                  <div style={{ textAlign: 'right' }}>
                    <span style={{
                      background: 'rgba(255,255,255,0.2)',
                      color: 'white', padding: '3px 10px',
                      borderRadius: '12px', fontSize: '12px', fontWeight: '600'
                    }}>
                      {selectedContact.leads[0].status.toUpperCase()} · {selectedContact.leads[0].score}/100
                    </span>
                  </div>
                )}
                <MoreVertical size={20} color="rgba(255,255,255,0.8)" style={{ cursor: 'pointer' }} />
              </div>

              {/* Messages Area */}
              <div style={{
                flex: 1,
                overflowY: 'auto',
                padding: '16px 20px',
                background: '#e5ddd5',
                display: 'flex',
                flexDirection: 'column',
                gap: '6px'
              }}>
                {messages.length === 0 ? (
                  <div style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    height: '100%', flexDirection: 'column', gap: '12px'
                  }}>
                    <MessageSquare size={48} color="#ccc" />
                    <p style={{ color: '#999', fontSize: '15px' }}>No messages yet</p>
                  </div>
                ) : (
                  messages.map((msg, index) => (
                    <div key={index} style={{
                      display: 'flex',
                      justifyContent: msg.direction === 'outbound' ? 'flex-end' : 'flex-start'
                    }}>
                      <div style={{
                        maxWidth: '62%',
                        padding: '8px 12px 6px 12px',
                        borderRadius: msg.direction === 'outbound'
                          ? '8px 0px 8px 8px'
                          : '0px 8px 8px 8px',
                        background: msg.direction === 'outbound'
                          ? '#dcf8c6'
                          : (sentimentBg[msg.sentiment] || 'white'),
                        boxShadow: '0 1px 2px rgba(0,0,0,0.13)',
                        fontSize: '14.5px',
                        lineHeight: '1.5',
                        color: '#111'
                      }}>
                        {/* Inbound — Customer name + sentiment emoji */}
                        {msg.direction === 'inbound' && (
                          <p style={{
                            fontSize: '12px', color: '#25D366',
                            margin: '0 0 2px 0', fontWeight: '600',
                            display: 'flex', alignItems: 'center', gap: '5px'
                          }}>
                            {selectedContact.name || 'Customer'}
                            {msg.sentiment_emoji && (
                              <span style={{ fontSize: '14px' }}>
                                {msg.sentiment_emoji}
                              </span>
                            )}
                            {msg.sentiment && (
                              <span style={{
                                fontSize: '10px',
                                color: msg.sentiment === 'negative' ? '#e53e3e' :
                                       msg.sentiment === 'positive' ? '#25D366' :
                                       msg.sentiment === 'urgent' ? '#dd6b20' : '#888',
                                fontWeight: '500'
                              }}>
                                {msg.sentiment}
                              </span>
                            )}
                          </p>
                        )}

                        <p style={{ margin: 0, wordBreak: 'break-word' }}>{msg.message_text}</p>

                        <div style={{
                          display: 'flex', justifyContent: 'flex-end',
                          alignItems: 'center', gap: '4px', marginTop: '3px'
                        }}>
                          <span style={{ fontSize: '11px', color: '#888' }}>
                            {new Date(msg.created_at).toLocaleTimeString([], {
                              hour: '2-digit', minute: '2-digit'
                            })}
                          </span>
                          {msg.direction === 'outbound' && (
                            <span style={{ fontSize: '12px', color: '#53bdeb' }}>✓✓</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div style={{
                padding: '10px 16px',
                background: '#f0f2f5',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                flexShrink: 0
              }}>
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type a message"
                  style={{
                    flex: 1,
                    padding: '12px 18px',
                    border: 'none',
                    borderRadius: '24px',
                    fontSize: '15px',
                    outline: 'none',
                    background: 'white',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.08)'
                  }}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={sending || !newMessage.trim()}
                  style={{
                    width: '50px', height: '50px',
                    borderRadius: '50%',
                    background: sending || !newMessage.trim() ? '#ccc' : '#25D366',
                    border: 'none',
                    cursor: sending || !newMessage.trim() ? 'not-allowed' : 'pointer',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    flexShrink: 0,
                    boxShadow: '0 2px 6px rgba(0,0,0,0.2)',
                    transition: 'background 0.2s'
                  }}
                >
                  {sending
                    ? <RefreshCw size={20} color="white" />
                    : <Send size={20} color="white" />
                  }
                </button>
              </div>
            </>
          ) : (
            <div style={{
              flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexDirection: 'column', gap: '16px', background: '#f0f2f5'
            }}>
              <div style={{
                width: '80px', height: '80px', borderRadius: '50%',
                background: '#dfe5e7', display: 'flex', alignItems: 'center', justifyContent: 'center'
              }}>
                <MessageSquare size={36} color="#aaa" />
              </div>
              <p style={{ fontSize: '18px', color: '#aaa', fontWeight: '300' }}>
                Select a contact to start messaging
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Conversations