<script setup>
import AppLayout from '../components/AppLayout.vue'
import ChatPanel from '../components/ChatPanel.vue'
import { useUnifiedChat } from '../composables/useUnifiedChat'

const {
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
} = useUnifiedChat()
</script>

<template>
  <AppLayout
    title="Assistente de IA Local"
    :conversations="conversations"
    :current-conversation-id="currentConversationId"
    @new-chat="clearChat"
    @select-conversation="selectConversation"
    @delete-conversation="removeConversation"
  >
    <div v-if="initializing" class="loading-state">
      <v-progress-circular indeterminate color="#10a37f" size="28" />
      <span>Carregando histórico...</span>
    </div>

    <ChatPanel
      v-else
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

<style scoped>
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  height: calc(100vh - 48px);
  color: var(--chat-text-muted);
}
</style>
