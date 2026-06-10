import api from './api'

export async function uploadVideo(file) {
  const formData = new FormData()
  formData.append('file', file, file.name)

  const { data } = await api.post('/api/video/upload', formData)

  return data
}

export async function sendVideoChatMessage(documentId, message) {
  const { data } = await api.post('/api/video/chat', {
    document_id: documentId,
    message,
  })

  return data.response
}
