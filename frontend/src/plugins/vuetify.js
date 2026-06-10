import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'chatgpt',
    themes: {
      chatgpt: {
        dark: true,
        colors: {
          primary: '#FFFFFF',
          secondary: '#B4B4B4',
          background: '#212121',
          surface: '#171717',
          'surface-variant': '#2F2F2F',
          'on-surface': '#FFFFFF',
          'on-background': '#FFFFFF',
          border: '#424242',
          accent: '#10A37F',
        },
      },
    },
  },
  defaults: {
    VBtn: {
      ripple: false,
    },
  },
})
