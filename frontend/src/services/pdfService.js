import api from './api'

export async function uploadPdf(file) {
  const formData = new FormData()
  formData.append('file', file, file.name)

  const { data } = await api.post('/api/pdf/upload', formData)

  return data
}

export async function sendPdfChatMessage(documentId, message) {
  const { data } = await api.post('/api/pdf/chat', {
    document_id: documentId,
    message,
  })

  return data.response
}
