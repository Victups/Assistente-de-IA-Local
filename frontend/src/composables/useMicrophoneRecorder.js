import { onUnmounted, ref } from 'vue'

function getSupportedMimeType() {
  const types = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/mp4',
    'audio/ogg;codecs=opus',
  ]

  return types.find((type) => MediaRecorder.isTypeSupported(type)) || ''
}

function extensionFromMime(mimeType) {
  if (mimeType.includes('webm')) {
    return '.webm'
  }

  if (mimeType.includes('ogg')) {
    return '.ogg'
  }

  if (mimeType.includes('mp4')) {
    return '.m4a'
  }

  return '.webm'
}

export function useMicrophoneRecorder() {
  const isRecording = ref(false)
  const recordingError = ref('')
  const recordingSeconds = ref(0)

  let mediaRecorder = null
  let mediaStream = null
  let chunks = []
  let timerInterval = null

  function clearTimer() {
    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }
  }

  function stopStream() {
    if (mediaStream) {
      mediaStream.getTracks().forEach((track) => track.stop())
      mediaStream = null
    }
  }

  function resetRecordingState() {
    clearTimer()
    recordingSeconds.value = 0
    chunks = []
  }

  async function startRecording() {
    recordingError.value = ''

    if (!navigator.mediaDevices?.getUserMedia) {
      recordingError.value = 'Seu navegador não suporta gravação de áudio.'
      return false
    }

    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mimeType = getSupportedMimeType()

      if (!mimeType) {
        recordingError.value = 'Não foi possível iniciar a gravação neste navegador.'
        stopStream()
        return false
      }

      chunks = []
      mediaRecorder = new MediaRecorder(mediaStream, { mimeType })

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data)
        }
      }

      mediaRecorder.start(250)
      isRecording.value = true
      recordingSeconds.value = 0

      timerInterval = setInterval(() => {
        recordingSeconds.value += 1
      }, 1000)

      return true
    } catch (error) {
      stopStream()

      if (error.name === 'NotAllowedError') {
        recordingError.value = 'Permissão do microfone negada. Autorize o acesso nas configurações do navegador.'
      } else if (error.name === 'NotFoundError') {
        recordingError.value = 'Nenhum microfone foi encontrado no dispositivo.'
      } else {
        recordingError.value = 'Não foi possível acessar o microfone.'
      }

      return false
    }
  }

  function stopRecording() {
    return new Promise((resolve, reject) => {
      if (!mediaRecorder || !isRecording.value) {
        resolve(null)
        return
      }

      const mimeType = mediaRecorder.mimeType || getSupportedMimeType()

      mediaRecorder.onstop = () => {
        clearTimer()
        isRecording.value = false
        stopStream()

        if (!chunks.length) {
          reject(new Error('Nenhum áudio foi gravado. Grave por pelo menos 1 segundo.'))
          return
        }

        const blob = new Blob(chunks, { type: mimeType })

        if (blob.size < 1000) {
          reject(new Error('Gravação muito curta. Fale por mais tempo antes de enviar.'))
          return
        }
        const extension = extensionFromMime(mimeType)
        const filename = `gravacao-${Date.now()}${extension}`
        const file = new File([blob], filename, { type: mimeType })

        chunks = []
        mediaRecorder = null
        resolve(file)
      }

      mediaRecorder.onerror = () => {
        clearTimer()
        isRecording.value = false
        stopStream()
        reject(new Error('Erro durante a gravação de áudio.'))
      }

      mediaRecorder.stop()
    })
  }

  function cancelRecording() {
    if (mediaRecorder && isRecording.value) {
      mediaRecorder.onstop = null
      mediaRecorder.stop()
    }

    clearTimer()
    isRecording.value = false
    stopStream()
    chunks = []
    mediaRecorder = null
  }

  onUnmounted(() => {
    cancelRecording()
  })

  return {
    isRecording,
    recordingError,
    recordingSeconds,
    startRecording,
    stopRecording,
    cancelRecording,
  }
}
