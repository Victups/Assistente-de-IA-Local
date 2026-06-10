import api from './api'

export async function uploadAudio(file) {
  const formData = new FormData()
  formData.append('file', file, file.name)

  const { data } = await api.post('/api/audio/upload', formData)

  return data
}

export async function sendAudioChatMessage(documentId, message) {
  const { data } = await api.post('/api/audio/chat', {
    document_id: documentId,
    message,
  })

  return data.response
}
