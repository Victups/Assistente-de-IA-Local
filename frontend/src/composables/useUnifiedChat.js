import { onMounted, ref } from 'vue'
import { extractErrorMessage } from '../services/api'
import { sendAudioChatMessage, uploadAudio } from '../services/audioService'
import { sendChatMessage } from '../services/chatService'
import {
  addMessage,
  createConversation,
  deleteConversation,
  getConversation,
  getConversationAttachment,
  listConversations,
  updateConversation,
} from '../services/conversationService'
import { sendPdfChatMessage, uploadPdf } from '../services/pdfService'
import { sendVideoChatMessage, uploadVideo } from '../services/videoService'

const UPLOAD_CONFIG = {
  pdf: {
    uploadFn: uploadPdf,
    label: 'PDF',
    successPrefix: 'PDF anexado',
    uploadError: 'Não foi possível processar o PDF.',
    chatError: 'Não foi possível obter resposta sobre o PDF.',
  },
  audio: {
    uploadFn: uploadAudio,
    label: 'Gravação de voz',
    uploadError: 'Não foi possível transcrever o áudio gravado.',
    chatError: 'Não foi possível obter resposta sobre o áudio.',
  },
  video: {
    uploadFn: uploadVideo,
    label: 'Vídeo',
    successPrefix: 'Vídeo transcrito',
    uploadError: 'Não foi possível processar o vídeo.',
    chatError: 'Não foi possível obter resposta sobre o vídeo.',
  },
}

function mapMessageFromApi(message) {
  return {
    id: message.id,
    role: message.role,
    content: message.content,
    transcriptionSource: message.transcription_source || null,
    isSystem: message.is_system || false,
  }
}

function buildAttachment(documentId, docType, filename, contentLength, transcription) {
  return {
    document_id: documentId,
    doc_type: docType,
    filename,
    content_length: Number(contentLength) || transcription?.length || 0,
    transcription: transcription || '',
    preview: (transcription || '').slice(0, 500),
  }
}

export function useUnifiedChat() {
  const messages = ref([])
  const conversations = ref([])
  const currentConversationId = ref(null)
  const loading = ref(false)
  const uploading = ref(false)
  const initializing = ref(true)
  const attachment = ref(null)

  async function refreshConversations() {
    conversations.value = await listConversations()
  }

  async function persistMessage(message) {
    if (!currentConversationId.value) {
      return null
    }

    const saved = await addMessage(currentConversationId.value, message)
    await refreshConversations()
    return saved
  }

  async function loadConversation(conversationId) {
    const conversation = await getConversation(conversationId)
    currentConversationId.value = conversation.id
    messages.value = conversation.messages.map(mapMessageFromApi)
    attachment.value = null

    if (conversation.document_id && conversation.doc_type) {
      const context = await getConversationAttachment(conversationId)

      if (context) {
        attachment.value = buildAttachment(
          context.document_id,
          context.doc_type,
          context.filename,
          context.content_length,
          context.transcription,
        )
      }
    }
  }

  async function startNewConversation() {
    const conversation = await createConversation()
    currentConversationId.value = conversation.id
    messages.value = []
    attachment.value = null
    await refreshConversations()
    return conversation
  }

  async function selectConversation(conversationId) {
    if (conversationId === currentConversationId.value) {
      return
    }

    await loadConversation(conversationId)
  }

  async function removeConversation(conversationId) {
    await deleteConversation(conversationId)
    await refreshConversations()

    if (currentConversationId.value === conversationId) {
      if (conversations.value.length) {
        await loadConversation(conversations.value[0].id)
      } else {
        await startNewConversation()
      }
    }
  }

  async function handleSend(message) {
    loading.value = true

    const userMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: message,
    }

    messages.value.push(userMessage)

    try {
      const savedUser = await persistMessage(userMessage)
      if (savedUser) {
        userMessage.id = savedUser.id
      }

      let response

      if (attachment.value) {
        response = await sendDocumentChat(
          attachment.value.document_id,
          message,
          attachment.value.doc_type,
        )
      } else {
        response = await sendChatMessage(message)
      }

      const assistantMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response,
      }

      messages.value.push(assistantMessage)
      const savedAssistant = await persistMessage(assistantMessage)
      if (savedAssistant) {
        assistantMessage.id = savedAssistant.id
      }
    } catch (error) {
      const fallback = attachment.value
        ? UPLOAD_CONFIG[attachment.value.doc_type].chatError
        : 'Não foi possível obter resposta do assistente. Verifique o backend e o Ollama.'

      const errorMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: extractErrorMessage(error, fallback),
      }

      messages.value.push(errorMessage)
      await persistMessage(errorMessage)
    } finally {
      loading.value = false
    }
  }

  async function handleFileUpload(type, file) {
    const config = UPLOAD_CONFIG[type]
    uploading.value = true

    if (type !== 'audio' && type !== 'video') {
      const userMessage = {
        id: crypto.randomUUID(),
        role: 'user',
        content: `📎 ${config.label}: ${file.name}`,
        isAttachment: true,
      }

      messages.value.push(userMessage)
      await persistMessage(userMessage)
    }

    try {
      const result = await config.uploadFn(file)

      attachment.value = {
        document_id: result.document_id,
        doc_type: result.doc_type,
        filename: result.filename,
        content_length: result.content_length,
        transcription: result.transcription || result.preview || '',
        preview: result.preview || '',
      }

      await updateConversation(currentConversationId.value, {
        document_id: result.document_id,
        doc_type: result.doc_type,
        attachment_filename: result.filename,
      })

      if (type === 'audio' || type === 'video') {
        const transcription = result.transcription || result.preview || ''
        const userMessage = {
          id: crypto.randomUUID(),
          role: 'user',
          content: transcription,
          transcriptionSource: type === 'audio' ? 'voice' : 'video',
        }

        messages.value.push(userMessage)
        const saved = await persistMessage(userMessage)
        if (saved) {
          userMessage.id = saved.id
        }
      } else {
        const assistantMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: `${config.successPrefix}: ${result.filename} (${result.content_length.toLocaleString('pt-BR')} caracteres). Agora você pode fazer perguntas sobre este conteúdo.`,
          isSystem: true,
        }

        messages.value.push(assistantMessage)
        const saved = await persistMessage(assistantMessage)
        if (saved) {
          assistantMessage.id = saved.id
        }
      }

      await refreshConversations()
    } catch (error) {
      const errorMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: extractErrorMessage(error, config.uploadError),
      }

      messages.value.push(errorMessage)
      await persistMessage(errorMessage)
    } finally {
      uploading.value = false
    }
  }

  async function removeAttachment() {
    attachment.value = null

    if (currentConversationId.value) {
      await updateConversation(currentConversationId.value, {
        document_id: null,
        doc_type: null,
        attachment_filename: null,
      })
    }
  }

  async function clearChat() {
    await startNewConversation()
  }

  async function initialize() {
    initializing.value = true

    try {
      await refreshConversations()

      if (conversations.value.length) {
        await loadConversation(conversations.value[0].id)
      } else {
        await startNewConversation()
      }
    } finally {
      initializing.value = false
    }
  }

  onMounted(() => {
    initialize()
  })

  return {
    messages,
    conversations,
    currentConversationId,
    loading,
    uploading,
    initializing,
    attachment,
    handleSend,
    handleFileUpload,
    removeAttachment,
    clearChat,
    selectConversation,
    removeConversation,
    refreshConversations,
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
