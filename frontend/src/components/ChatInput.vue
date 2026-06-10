<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useMicrophoneRecorder } from '../composables/useMicrophoneRecorder'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
  uploading: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  attachment: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['send', 'upload', 'remove-attachment'])

const message = ref('')
const pdfInput = ref(null)
const videoInput = ref(null)
const textareaRef = ref(null)

const {
  isRecording,
  recordingError,
  recordingSeconds,
  startRecording,
  stopRecording,
  cancelRecording,
} = useMicrophoneRecorder()

const isBusy = computed(() => props.loading || props.uploading || isRecording.value)
const canSend = computed(() => message.value.trim() && !isBusy.value && !props.disabled)

const formattedRecordingTime = computed(() => {
  const minutes = Math.floor(recordingSeconds.value / 60)
  const seconds = recordingSeconds.value % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})

const placeholder = computed(() => {
  if (isRecording.value) {
    return 'Gravando áudio... clique em parar quando terminar.'
  }

  if (props.uploading) {
    return 'Aguarde o processamento do arquivo...'
  }

  if (props.attachment?.doc_type === 'pdf') {
    return 'Pergunte sobre o PDF anexado...'
  }

  if (props.attachment?.doc_type === 'audio') {
    return 'Pergunte sobre o áudio gravado...'
  }

  if (props.attachment?.doc_type === 'video') {
    return 'Pergunte sobre o vídeo transcrito...'
  }

  return 'Envie uma mensagem...'
})

const attachmentIcon = computed(() => {
  const icons = {
    pdf: 'mdi-file-pdf-box',
    audio: 'mdi-microphone',
    video: 'mdi-video',
  }

  return icons[props.attachment?.doc_type] || 'mdi-paperclip'
})

function resizeTextarea() {
  const el = textareaRef.value

  if (!el) {
    return
  }

  el.style.height = 'auto'
  el.style.height = `${Math.min(el.scrollHeight, 200)}px`
}

function handleSend() {
  const trimmedMessage = message.value.trim()

  if (!trimmedMessage || isBusy.value || props.disabled) {
    return
  }

  emit('send', trimmedMessage)
  message.value = ''

  nextTick(() => {
    resizeTextarea()
  })
}

function handleKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSend()
  }
}

function openFilePicker(type) {
  if (props.loading || props.uploading || isRecording.value) {
    return
  }

  if (type === 'pdf') {
    pdfInput.value?.click()
  } else if (type === 'video') {
    videoInput.value?.click()
  }
}

async function toggleMicrophone() {
  if (props.loading || props.uploading) {
    return
  }

  recordingError.value = ''

  if (isRecording.value) {
    try {
      const file = await stopRecording()

      if (file) {
        emit('upload', 'audio', file)
      }
    } catch (error) {
      recordingError.value = error.message || 'Não foi possível finalizar a gravação.'
    }

    return
  }

  await startRecording()
}

function handleCancelRecording() {
  cancelRecording()
}

function handleFileChange(type, event) {
  const file = event.target.files?.[0]
  event.target.value = ''

  if (file) {
    emit('upload', type, file)
  }
}

watch(message, () => {
  nextTick(resizeTextarea)
})

onMounted(() => {
  resizeTextarea()
})
</script>

<template>
  <div class="input-area">
    <div class="input-wrapper">
      <div
        class="compose-box"
        :class="{ 'compose-box--recording': isRecording }"
      >
        <div v-if="attachment" class="attachment-chip">
          <v-chip
            closable
            size="small"
            variant="flat"
            class="file-chip"
            :prepend-icon="attachmentIcon"
            :disabled="loading || uploading || isRecording"
            @click:close="emit('remove-attachment')"
          >
            {{ attachment.filename }}
          </v-chip>
        </div>

        <div v-if="isRecording" class="recording-banner">
          <span class="recording-dot" />
          <span class="recording-text">Gravando {{ formattedRecordingTime }}</span>
          <button
            type="button"
            class="recording-cancel"
            @click="handleCancelRecording"
          >
            Cancelar
          </button>
        </div>

        <textarea
          ref="textareaRef"
          v-model="message"
          class="compose-textarea"
          :placeholder="placeholder"
          rows="1"
          :disabled="loading || uploading || disabled || isRecording"
          @keydown="handleKeydown"
          @input="resizeTextarea"
        />

        <div class="compose-actions">
          <div class="attach-buttons">
            <v-tooltip text="Anexar PDF" location="top">
              <template #activator="{ props: tooltipProps }">
                <button
                  v-bind="tooltipProps"
                  type="button"
                  class="icon-btn"
                  :disabled="loading || uploading || isRecording"
                  @click="openFilePicker('pdf')"
                >
                  <v-icon icon="mdi-file-pdf-box" size="20" />
                </button>
              </template>
            </v-tooltip>

            <v-tooltip :text="isRecording ? 'Parar e enviar áudio' : 'Gravar áudio pelo microfone'" location="top">
              <template #activator="{ props: tooltipProps }">
                <button
                  v-bind="tooltipProps"
                  type="button"
                  class="icon-btn mic-btn"
                  :class="{ 'mic-btn--recording': isRecording }"
                  :disabled="loading || uploading"
                  @click="toggleMicrophone"
                >
                  <v-icon :icon="isRecording ? 'mdi-stop' : 'mdi-microphone'" size="20" />
                </button>
              </template>
            </v-tooltip>

            <v-tooltip text="Anexar vídeo" location="top">
              <template #activator="{ props: tooltipProps }">
                <button
                  v-bind="tooltipProps"
                  type="button"
                  class="icon-btn"
                  :disabled="loading || uploading || isRecording"
                  @click="openFilePicker('video')"
                >
                  <v-icon icon="mdi-video" size="20" />
                </button>
              </template>
            </v-tooltip>
          </div>

          <button
            type="button"
            class="send-btn"
            :class="{ 'send-btn--active': canSend }"
            :disabled="!canSend"
            @click="handleSend"
          >
            <v-progress-circular
              v-if="loading"
              indeterminate
              size="16"
              width="2"
              color="#212121"
            />
            <v-icon v-else icon="mdi-arrow-up" size="20" />
          </button>
        </div>
      </div>

      <p v-if="recordingError" class="input-error">
        {{ recordingError }}
      </p>

      <p v-else class="input-hint">
        Microfone: clique para gravar, clique novamente para enviar · PDF e vídeo por anexo
      </p>
    </div>

    <input
      ref="pdfInput"
      type="file"
      accept=".pdf,application/pdf"
      hidden
      @change="handleFileChange('pdf', $event)"
    >
    <input
      ref="videoInput"
      type="file"
      accept=".mp4,.webm,.avi,.mov,.mkv,video/*"
      hidden
      @change="handleFileChange('video', $event)"
    >
  </div>
</template>

<style scoped>
.input-area {
  padding: 0.75rem 1rem 1.25rem;
  background: var(--chat-bg);
  border-top: 1px solid var(--chat-border);
}

.input-wrapper {
  max-width: var(--chat-max-width);
  margin: 0 auto;
}

.compose-box {
  background: var(--chat-input-bg);
  border: 1px solid var(--chat-border);
  border-radius: 1.5rem;
  padding: 0.75rem 1rem;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.05);
  transition: border-color 0.2s;
}

.compose-box--recording {
  border-color: #e55353;
}

.attachment-chip {
  padding-bottom: 0.5rem;
}

.file-chip {
  background: #404040 !important;
  color: var(--chat-text) !important;
}

.recording-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(229, 83, 83, 0.12);
  border-radius: 0.75rem;
}

.recording-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: #e55353;
  animation: blink 1s ease-in-out infinite;
}

.recording-text {
  flex: 1;
  font-size: 0.875rem;
  color: #ffffff;
  font-weight: 500;
}

.recording-cancel {
  border: none;
  background: transparent;
  color: var(--chat-text-muted);
  font-size: 0.8125rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
}

.recording-cancel:hover {
  background: #404040;
  color: #ffffff;
}

@keyframes blink {
  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.3;
  }
}

.compose-textarea {
  display: block;
  width: 100%;
  min-height: 2.75rem;
  max-height: 12.5rem;
  padding: 0.5rem 0;
  margin: 0;
  border: none;
  outline: none;
  resize: none;
  overflow-y: auto;
  background: transparent;
  color: #ffffff;
  caret-color: #ffffff;
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.6;
  field-sizing: content;
}

.compose-textarea::placeholder {
  color: var(--chat-text-muted);
}

.compose-textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.compose-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.5rem;
}

.attach-buttons {
  display: flex;
  gap: 0.125rem;
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: none;
  border-radius: 0.5rem;
  background: transparent;
  color: var(--chat-text-muted);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.icon-btn:hover:not(:disabled) {
  background: #404040;
  color: var(--chat-text);
}

.icon-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.mic-btn--recording {
  background: rgba(229, 83, 83, 0.2) !important;
  color: #ff6b6b !important;
}

.send-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: none;
  border-radius: 50%;
  background: #515151;
  color: #8e8e8e;
  cursor: not-allowed;
  transition: background 0.15s, color 0.15s;
}

.send-btn--active {
  background: #ececec;
  color: #212121;
  cursor: pointer;
}

.send-btn--active:hover {
  background: #fff;
}

.input-hint {
  margin: 0.625rem 0 0;
  text-align: center;
  font-size: 0.75rem;
  color: var(--chat-text-muted);
}

.input-error {
  margin: 0.625rem 0 0;
  text-align: center;
  font-size: 0.75rem;
  color: #ff6b6b;
}
</style>
