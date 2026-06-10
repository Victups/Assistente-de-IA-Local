import { ref } from 'vue'
import { extractErrorMessage } from '../services/api'
import { sendAudioChatMessage, uploadAudio } from '../services/audioService'
import { sendChatMessage } from '../services/chatService'
import { sendPdfChatMessage, uploadPdf } from '../services/pdfService'
import { sendVideoChatMessage, uploadVideo } from '../services/videoService'

const UPLOAD_CONFIG = {
  pdf: {
    uploadFn: uploadPdf,
    icon: 'mdi-file-pdf-box',
    label: 'PDF',
    processingMessage: 'Processando PDF...',
    successPrefix: 'PDF anexado',
    uploadError: 'Não foi possível processar o PDF.',
    chatError: 'Não foi possível obter resposta sobre o PDF.',
  },
  audio: {
    uploadFn: uploadAudio,
    icon: 'mdi-microphone',
    label: 'Gravação de voz',
    processingMessage: 'Transcrevendo áudio...',
    successPrefix: 'Áudio gravado e transcrito',
    uploadError: 'Não foi possível transcrever o áudio gravado.',
    chatError: 'Não foi possível obter resposta sobre o áudio.',
  },
  video: {
    uploadFn: uploadVideo,
    icon: 'mdi-video',
    label: 'Vídeo',
    processingMessage: 'Processando vídeo...',
    successPrefix: 'Vídeo transcrito',
    uploadError: 'Não foi possível processar o vídeo.',
    chatError: 'Não foi possível obter resposta sobre o vídeo.',
  },
}

export function useUnifiedChat() {
  const messages = ref([])
  const loading = ref(false)
  const uploading = ref(false)
  const attachment = ref(null)

  async function handleSend(message) {
    loading.value = true

    messages.value.push({
      id: crypto.randomUUID(),
      role: 'user',
      content: message,
    })

    try {
      let response

      if (attachment.value) {
        response = await sendDocumentChat(attachment.value.document_id, message, attachment.value.doc_type)
      } else {
        response = await sendChatMessage(message)
      }

      messages.value.push({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response,
      })
    } catch (error) {
      const fallback = attachment.value
        ? UPLOAD_CONFIG[attachment.value.doc_type].chatError
        : 'Não foi possível obter resposta do assistente. Verifique o backend e o Ollama.'

      messages.value.push({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: extractErrorMessage(error, fallback),
      })
    } finally {
      loading.value = false
    }
  }

  async function handleFileUpload(type, file) {
    const config = UPLOAD_CONFIG[type]
    uploading.value = true

    const userMessage = type === 'audio'
      ? `🎤 ${config.label} enviada`
      : `📎 ${config.label}: ${file.name}`

    messages.value.push({
      id: crypto.randomUUID(),
      role: 'user',
      content: userMessage,
      isAttachment: true,
    })

    try {
      const result = await config.uploadFn(file)
      attachment.value = result

      messages.value.push({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `${config.successPrefix}: ${result.filename} (${result.content_length.toLocaleString('pt-BR')} caracteres). Agora você pode fazer perguntas sobre este conteúdo.`,
        isSystem: true,
      })
    } catch (error) {
      messages.value.push({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: extractErrorMessage(error, config.uploadError),
      })
    } finally {
      uploading.value = false
    }
  }

  function removeAttachment() {
    attachment.value = null
  }

  function clearChat() {
    messages.value = []
    attachment.value = null
  }

  return {
    messages,
    loading,
    uploading,
    attachment,
    handleSend,
    handleFileUpload,
    removeAttachment,
    clearChat,
  }
}

async function sendDocumentChat(documentId, message, docType) {
  if (docType === 'pdf') {
    return sendPdfChatMessage(documentId, message)
  }

  if (docType === 'audio') {
    return sendAudioChatMessage(documentId, message)
  }

  return sendVideoChatMessage(documentId, message)
}
