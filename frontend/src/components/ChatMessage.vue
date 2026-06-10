<script setup>
defineProps({
  role: {
    type: String,
    required: true,
    validator: (value) => ['user', 'assistant'].includes(value),
  },
  content: {
    type: String,
    required: true,
  },
  transcriptionSource: {
    type: String,
    default: null,
    validator: (value) => !value || ['voice', 'video'].includes(value),
  },
})

const badgeLabel = {
  voice: 'Transcrição de voz',
  video: 'Transcrição de vídeo',
}
</script>

<template>
  <div
    class="message-row"
    :class="role === 'user' ? 'message-row--user' : 'message-row--assistant'"
  >
    <div class="message-inner">
      <div class="message-avatar" :class="`message-avatar--${role}`">
        <v-icon
          v-if="role === 'assistant'"
          icon="mdi-robot-outline"
          size="18"
        />
        <v-icon
          v-else-if="transcriptionSource === 'voice'"
          icon="mdi-microphone"
          size="18"
        />
        <v-icon
          v-else-if="transcriptionSource === 'video'"
          icon="mdi-video"
          size="18"
        />
        <v-icon
          v-else
          icon="mdi-account"
          size="18"
        />
      </div>

      <div class="message-body">
        <div class="message-header">
          <span class="message-label">
            {{ role === 'user' ? 'Você' : 'Assistente' }}
          </span>
          <span v-if="transcriptionSource" class="voice-badge">
            {{ badgeLabel[transcriptionSource] }}
          </span>
        </div>
        <div class="message-content text-pre-wrap">
          {{ content }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-row {
  width: 100%;
  padding: 1.25rem 1rem;
  border-bottom: 1px solid transparent;
}

.message-row--user {
  background: var(--chat-user-row);
}

.message-row--assistant {
  background: var(--chat-bg);
}

.message-inner {
  display: flex;
  gap: 1rem;
  max-width: var(--chat-max-width);
  margin: 0 auto;
  width: 100%;
}

.message-avatar {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  border-radius: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-avatar--assistant {
  background: var(--chat-accent);
  color: #fff;
}

.message-avatar--user {
  background: #5c5c5c;
  color: #ececec;
}

.message-body {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.375rem;
  flex-wrap: wrap;
}

.message-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff !important;
}

.voice-badge {
  font-size: 0.75rem;
  color: var(--chat-text-muted);
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  background: rgba(255, 255, 255, 0.06);
}

.message-content {
  font-size: 0.9375rem;
  line-height: 1.65;
  color: #ffffff !important;
  word-break: break-word;
}
</style>
