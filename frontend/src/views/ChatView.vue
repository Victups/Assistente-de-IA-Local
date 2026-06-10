<script setup>
import AppLayout from '../components/AppLayout.vue'
import ChatPanel from '../components/ChatPanel.vue'
import { useUnifiedChat } from '../composables/useUnifiedChat'

const {
  messages,
  loading,
  uploading,
  attachment,
  handleSend,
  handleFileUpload,
  removeAttachment,
  clearChat,
} = useUnifiedChat()
</script>

<template>
  <AppLayout title="Assistente de IA Local" @new-chat="clearChat">
    <ChatPanel
      :messages="messages"
      :loading="loading"
      :uploading="uploading"
      :attachment="attachment"
      welcome-message="Converse com o Phi-3, grave áudio pelo microfone ou anexe PDF e vídeo pelos ícones."
      @send="handleSend"
      @upload="handleFileUpload"
      @remove-attachment="removeAttachment"
    />
  </AppLayout>
</template>
