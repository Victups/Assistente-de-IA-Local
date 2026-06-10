<script setup>
import { nextTick, ref, watch } from 'vue'
import ChatInput from './ChatInput.vue'
import ChatLoading from './ChatLoading.vue'
import ChatMessage from './ChatMessage.vue'

const props = defineProps({
  messages: {
    type: Array,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  uploading: {
    type: Boolean,
    default: false,
  },
  attachment: {
    type: Object,
    default: null,
  },
  welcomeMessage: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['send', 'upload', 'remove-attachment'])

const messagesContainer = ref(null)

async function scrollToBottom() {
  await nextTick()

  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(
  () => [props.messages.length, props.loading, props.uploading],
  () => {
    scrollToBottom()
  },
)
</script>

<template>
  <div class="chat-panel">
    <div
      ref="messagesContainer"
      class="messages-area"
    >
      <div
        v-if="!messages.length && !loading && !uploading"
        class="welcome-state"
      >
        <div class="welcome-icon">
          <v-icon icon="mdi-robot-outline" size="28" color="#fff" />
        </div>
        <h2 class="welcome-title">Como posso ajudar?</h2>
        <p class="welcome-text">{{ welcomeMessage }}</p>
      </div>

      <template v-else>
        <ChatMessage
          v-for="item in messages"
          :key="item.id"
          :role="item.role"
          :content="item.content"
        />

        <ChatLoading
          v-if="loading || uploading"
          :label="uploading ? 'Processando arquivo...' : 'O assistente está pensando...'"
        />
      </template>
    </div>

    <ChatInput
      :loading="loading"
      :uploading="uploading"
      :attachment="attachment"
      @send="emit('send', $event)"
      @upload="(type, file) => emit('upload', type, file)"
      @remove-attachment="emit('remove-attachment')"
    />
  </div>
</template>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 48px);
  background: var(--chat-bg);
}

.messages-area {
  flex: 1;
  overflow-y: auto;
}

.welcome-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  padding: 2rem;
  text-align: center;
}

.welcome-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.5rem;
  background: var(--chat-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
}

.welcome-title {
  margin: 0 0 0.5rem;
  font-size: 1.75rem;
  font-weight: 500;
  color: var(--chat-text);
}

.welcome-text {
  margin: 0;
  max-width: 28rem;
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--chat-text-muted);
}
</style>
