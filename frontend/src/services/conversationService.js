import api from './api'

export async function listConversations() {
  const { data } = await api.get('/api/conversations')
  return data
}

export async function createConversation(title = 'Nova conversa') {
  const { data } = await api.post('/api/conversations', { title })
  return data
}

export async function getConversation(conversationId) {
  const { data } = await api.get(`/api/conversations/${conversationId}`)
  return data
}

export async function updateConversation(conversationId, payload) {
  const { data } = await api.patch(`/api/conversations/${conversationId}`, payload)
  return data
}

export async function deleteConversation(conversationId) {
  await api.delete(`/api/conversations/${conversationId}`)
}

export async function addMessage(conversationId, message) {
  const { data } = await api.post(`/api/conversations/${conversationId}/messages`, {
    role: message.role,
    content: message.content,
    transcription_source: message.transcriptionSource || null,
    is_system: message.isSystem || false,
  })
  return data
}

export async function getConversationAttachment(conversationId) {
  const { data } = await api.get(`/api/conversations/${conversationId}/attachment`)
  return data
}
