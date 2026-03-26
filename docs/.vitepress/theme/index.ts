import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import NoteExplorer from './components/NoteExplorer.vue'
import NotesCards from './components/NotesCards.vue'
import HomeTagStream from './components/HomeTagStream.vue'
import './custom.css'

const theme: Theme = {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('NoteExplorer', NoteExplorer)
    app.component('NotesCards', NotesCards)
    app.component('HomeTagStream', HomeTagStream)
  }
}

export default theme
