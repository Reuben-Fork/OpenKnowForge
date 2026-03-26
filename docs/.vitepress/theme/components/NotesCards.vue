<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, withBase } from 'vitepress'

type NoteItem = {
  slug?: string
  title: string
  excerpt?: string
  date?: string
  created_at?: string
  updated_at?: string
  submitted_at?: string
  status?: string
  tags?: string[]
  link: string
}

const notes = ref<NoteItem[]>([])
const loading = ref(true)
const error = ref('')
const showDrafts = ref(false)
const route = useRoute()

const POLL_INTERVAL_MS = 2500
const SHOW_DRAFTS_STORAGE_KEY = 'okf_show_drafts'
let pollTimer: number | undefined

const isEn = computed(() => route.path.startsWith('/en/'))

const uiText = computed(() =>
  isEn.value
    ? {
        previewFallback: 'No content preview',
        loading: 'Loading notes...',
        empty: 'No notes yet.',
        loadError: 'Failed to load search index. Check docs/public/search-index.json.',
        toggleLabel: 'Show Drafts',
        toggleOn: 'ON',
        toggleOff: 'OFF'
      }
    : {
        previewFallback: '暂无内容预览',
        loading: '正在加载笔记...',
        empty: '还没有笔记。',
        loadError: '读取搜索索引失败，请检查 docs/public/search-index.json。',
        toggleLabel: '显示草稿',
        toggleOn: '开',
        toggleOff: '关'
      }
)

function normalizeStatus(value?: string): 'mature' | 'draft' {
  const raw = String(value || '').trim().toLowerCase()
  if (raw === 'draft') {
    return 'draft'
  }
  if (raw === 'published' || raw === 'mature' || !raw) {
    return 'mature'
  }
  return 'mature'
}

function plainTextPreview(value?: string): string {
  const raw = String(value || '')
  if (!raw) {
    return uiText.value.previewFallback
  }

  const withoutHtml = raw.replace(/<[^>]*>/g, ' ')
  const withoutMd = withoutHtml.replace(/[`*_#>\[\]()~\-]+/g, ' ')
  const normalized = withoutMd.replace(/\s+/g, ' ').trim()
  if (!normalized) {
    return uiText.value.previewFallback
  }
  return normalized
}

function parseTs(value?: string): number {
  if (!value) {
    return 0
  }
  const parsed = Date.parse(value)
  return Number.isNaN(parsed) ? 0 : parsed
}

const visibleNotes = computed(() => {
  if (showDrafts.value) {
    return notes.value
  }
  return notes.value.filter((note) => normalizeStatus(note.status) !== 'draft')
})

const sortedNotes = computed(() => {
  return [...visibleNotes.value].sort((a, b) => {
    const aTs = parseTs(a.updated_at || a.date)
    const bTs = parseTs(b.updated_at || b.date)
    return bTs - aTs
  })
})

function hydrateDraftVisibility(): void {
  if (typeof window === 'undefined') {
    return
  }
  const saved = window.localStorage.getItem(SHOW_DRAFTS_STORAGE_KEY)
  if (!saved) {
    return
  }
  showDrafts.value = saved === '1'
}

function toggleShowDrafts(): void {
  showDrafts.value = !showDrafts.value
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(SHOW_DRAFTS_STORAGE_KEY, showDrafts.value ? '1' : '0')
  }
}

function resolveLink(link: string): string {
  if (link.startsWith('http://') || link.startsWith('https://')) {
    return link
  }
  if (link.startsWith('/')) {
    if (isEn.value && (link === '/notes' || link.startsWith('/notes/'))) {
      return withBase(`/en${link}`)
    }
    return withBase(link)
  }
  const normalized = `/notes/${link.replace(/^\.\//, '')}`
  if (isEn.value) {
    return withBase(`/en${normalized}`)
  }
  return withBase(normalized)
}

async function loadNotes(isInitial: boolean): Promise<void> {
  const candidates = Array.from(
    new Set([
      withBase('/search-index.json'),
      withBase('/.vitepress/public/search-index.json'),
      '/search-index.json',
      '/.vitepress/public/search-index.json'
    ])
  )

  for (const candidate of candidates) {
    try {
      const response = await fetch(candidate, { cache: 'no-store' })
      if (!response.ok) {
        continue
      }
      const payload = await response.json()
      notes.value = Array.isArray(payload?.notes) ? payload.notes : []
      error.value = ''
      return
    } catch {
      continue
    }
  }

  if (isInitial) {
    error.value = uiText.value.loadError
  }
}

onMounted(async () => {
  hydrateDraftVisibility()
  await loadNotes(true)
  loading.value = false

  pollTimer = window.setInterval(() => {
    void loadNotes(false)
  }, POLL_INTERVAL_MS)
})

onBeforeUnmount(() => {
  if (pollTimer !== undefined) {
    window.clearInterval(pollTimer)
  }
})
</script>

<template>
  <div v-if="!loading && !error" class="note-cards__controls">
    <button type="button" class="note-cards__toggle" @click="toggleShowDrafts">
      {{ uiText.toggleLabel }}: {{ showDrafts ? uiText.toggleOn : uiText.toggleOff }}
    </button>
  </div>

  <p v-if="loading">{{ uiText.loading }}</p>
  <p v-else-if="error" class="note-cards-error">{{ error }}</p>
  <p v-else-if="sortedNotes.length === 0">{{ uiText.empty }}</p>

  <div v-if="!loading && !error && sortedNotes.length > 0" class="notes-cards">
    <a v-for="note in sortedNotes" :key="`${note.link}-${note.updated_at || note.date}`" class="note-card" :href="resolveLink(note.link)">
      <h3>{{ note.title }}</h3>
      <p class="note-card__preview">{{ plainTextPreview(note.excerpt) }}</p>
      <div class="note-card__tags">
        <span v-for="tag in note.tags || []" :key="`${note.link}-${tag}`" class="note-card__tag">#{{ tag }}</span>
      </div>
    </a>
  </div>
</template>

<style scoped>
.note-cards-error {
  color: #b91c1c;
}

.note-cards__controls {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.note-cards__toggle {
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  border-radius: 10px;
  padding: 6px 12px;
  font-size: 13px;
  cursor: pointer;
}

.note-cards__toggle:hover {
  opacity: 0.88;
}

.dark .note-cards-error {
  color: #fca5a5;
}
</style>
