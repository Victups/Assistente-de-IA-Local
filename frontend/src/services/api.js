import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? '' : 'http://localhost:8000'),
})

export function extractErrorMessage(error, fallbackMessage) {
  const status = error.response?.status
  const detail = error.response?.data?.detail
  const url = error.config?.url || ''

  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail) && detail.length) {
    return detail.map((item) => item.msg).join(', ')
  }

  if (status === 404) {
    if (url.includes('/audio/')) {
      return 'Serviço de áudio não encontrado. Reinicie o backend com a versão mais recente.'
    }

    if (url.includes('/conversations')) {
      return 'Histórico de conversas não disponível. Reinicie o backend com a versão mais recente.'
    }

    return 'Recurso não encontrado. Reinicie o backend: uvicorn app.main:app --reload --port 8000'
  }

  if (error.message === 'Network Error') {
    return 'Não foi possível conectar ao backend. Verifique se está rodando na porta 8000.'
  }

  return fallbackMessage
}

export async function checkBackendHealth() {
  const { data } = await api.get('/health')
  return data
}

export default api
