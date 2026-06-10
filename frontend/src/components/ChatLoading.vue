<script setup>
defineProps({
  label: {
    type: String,
    default: 'O assistente está pensando...',
  },
})
</script>

<template>
  <div class="message-row message-row--assistant">
    <div class="message-inner">
      <div class="message-avatar message-avatar--assistant">
        <v-icon icon="mdi-robot-outline" size="18" />
      </div>

      <div class="message-body">
        <div class="message-label">Assistente</div>
        <div class="loading-dots">
          <span />
          <span />
          <span />
        </div>
        <span class="loading-label">{{ label }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-row {
  width: 100%;
  padding: 1.25rem 1rem;
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
  background: var(--chat-accent);
  color: #fff;
}

.message-body {
  flex: 1;
}

.message-label {
  font-size: 0.8125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.loading-dots {
  display: inline-flex;
  gap: 4px;
  margin-right: 8px;
  vertical-align: middle;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--chat-text-muted);
  animation: pulse 1.4s ease-in-out infinite;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

.loading-label {
  font-size: 0.875rem;
  color: #ffffff;
}

.message-label {
  color: #ffffff !important;
}

@keyframes pulse {
  0%,
  80%,
  100% {
    opacity: 0.3;
    transform: scale(0.85);
  }

  40% {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
