<script setup>
import { ref } from 'vue'

defineProps({
  title: {
    type: String,
    default: 'Assistente de IA Local',
  },
})

const emit = defineEmits(['new-chat'])

const drawer = ref(true)
const rail = ref(false)
</script>

<template>
  <v-navigation-drawer
    v-model="drawer"
    :rail="rail"
    permanent
    class="sidebar border-e"
    width="260"
  >
    <div class="sidebar-header">
      <v-btn
        block
        variant="outlined"
        class="new-chat-btn"
        prepend-icon="mdi-plus"
        @click="emit('new-chat')"
      >
        <span v-if="!rail">Nova conversa</span>
      </v-btn>
    </div>

    <v-spacer />

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
  border-color: var(--chat-border) !important;
  color: var(--chat-text) !important;
  text-transform: none;
  letter-spacing: normal;
  font-weight: 500;
  justify-content: flex-start;
}

.new-chat-btn:hover {
  background: #2a2a2a !important;
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
