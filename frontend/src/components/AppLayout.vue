<script setup>
import { ref } from 'vue'

defineProps({
  title: {
    type: String,
    default: 'Assistente de IA Local',
  },
  conversations: {
    type: Array,
    default: () => [],
  },
  currentConversationId: {
    type: String,
    default: null,
  },
  creatingConversation: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['new-chat', 'select-conversation', 'delete-conversation'])

const drawer = ref(true)
const rail = ref(false)

function formatDate(value) {
  if (!value) {
    return ''
  }

  const date = new Date(value)
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
  })
}
</script>

<template>
  <v-navigation-drawer
    v-model="drawer"
    :rail="rail"
    permanent
    class="sidebar border-e"
    width="280"
  >
    <div class="sidebar-header">
      <v-btn
        type="button"
        block
        variant="flat"
        class="new-chat-btn"
        prepend-icon="mdi-plus"
        :loading="creatingConversation"
        :disabled="creatingConversation"
        @click="emit('new-chat')"
      >
        <span v-if="!rail">Nova conversa</span>
      </v-btn>
    </div>

    <div v-if="!rail" class="history-section">
      <div class="history-title">Histórico</div>

      <div v-if="!conversations.length" class="history-empty">
        Nenhuma conversa salva ainda.
      </div>

      <v-list
        v-else
        density="compact"
        nav
        class="history-list"
      >
        <v-list-item
          v-for="conversation in conversations"
          :key="conversation.id"
          :title="conversation.title"
          :subtitle="formatDate(conversation.updated_at)"
          :active="conversation.id === currentConversationId"
          rounded="lg"
          class="history-item"
          @click="emit('select-conversation', conversation.id)"
        >
          <template #append>
            <v-btn
              icon="mdi-delete-outline"
              variant="text"
              size="x-small"
              class="delete-btn"
              @click.stop="emit('delete-conversation', conversation.id)"
            />
          </template>
        </v-list-item>
      </v-list>
    </div>

    <template #append>
      <div class="sidebar-footer">
        <v-btn
          icon
          variant="text"
          size="small"
          class="rail-toggle"
          @click="rail = !rail"
        >
          <v-icon :icon="rail ? 'mdi-chevron-right' : 'mdi-chevron-left'" />
        </v-btn>
        <div v-if="!rail" class="sidebar-brand">
          <v-icon icon="mdi-robot-outline" size="18" class="me-2" />
          <span>Phi-3 · Local</span>
        </div>
      </div>
    </template>
  </v-navigation-drawer>

  <v-app-bar flat height="48" class="top-bar border-b">
    <v-app-bar-nav-icon
      class="d-lg-none"
      size="small"
      @click="drawer = !drawer"
    />

    <v-app-bar-title class="top-bar-title">
      {{ title }}
    </v-app-bar-title>
  </v-app-bar>

  <v-main class="main-content">
    <slot />
  </v-main>
</template>

<style scoped>
.sidebar {
  background: var(--chat-sidebar) !important;
  border-color: var(--chat-border) !important;
}

.sidebar-header {
  padding: 0.75rem;
}

.new-chat-btn {
  background: #2f2f2f !important;
  color: #ffffff !important;
  text-transform: none;
  letter-spacing: normal;
  font-weight: 500;
  justify-content: flex-start;
  border: 1px solid var(--chat-border) !important;
  min-height: 2.75rem;
}

.new-chat-btn:hover:not(:disabled) {
  background: #3a3a3a !important;
}

.new-chat-btn:disabled {
  opacity: 0.7;
}

.history-section {
  display: flex;
  flex-direction: column;
  min-height: 0;
  flex: 1;
  overflow: hidden;
  padding: 0 0.5rem;
}

.history-title {
  padding: 0.5rem 0.75rem 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--chat-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.history-empty {
  padding: 0.75rem;
  font-size: 0.8125rem;
  color: var(--chat-text-muted);
}

.history-list {
  overflow-y: auto;
  flex: 1;
  padding-bottom: 0.5rem;
}

.history-item {
  color: var(--chat-text) !important;
}

.history-item :deep(.v-list-item-title) {
  color: var(--chat-text) !important;
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-item :deep(.v-list-item-subtitle) {
  color: var(--chat-text-muted) !important;
  font-size: 0.75rem;
}

.delete-btn {
  opacity: 0;
  color: var(--chat-text-muted) !important;
}

.history-item:hover .delete-btn {
  opacity: 1;
}

.sidebar-footer {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-top: 1px solid var(--chat-border);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  font-size: 0.8125rem;
  color: var(--chat-text-muted);
}

.rail-toggle {
  color: var(--chat-text-muted) !important;
}

.top-bar {
  background: var(--chat-bg) !important;
  border-color: var(--chat-border) !important;
}

.top-bar-title {
  font-size: 0.9375rem !important;
  font-weight: 500;
  color: var(--chat-text);
}

.main-content {
  background: var(--chat-bg);
  padding: 0 !important;
}
</style>
