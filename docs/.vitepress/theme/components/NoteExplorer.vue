<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, withBase } from 'vitepress'

type NoteItem = {
  slug?: string
  title: string
  date?: string
  created_at?: string
  updated_at?: string
  submitted_at?: string
  tags?: string[]
  link: string
}

const notes = ref<NoteItem[]>([])
const query = ref('')
const loading = ref(true)
const error = ref('')
const route = useRoute()

const POLL_INTERVAL_MS = 2500
let pollTimer: number | undefined

const isEn = computed(() => route.path.startsWith('/en/'))

const uiText = computed(() =>
  isEn.value
    ? {
        unknown: 'unknown',
        searchPlaceholder: 'Search titles or tags...',
        loading: 'Loading notes...',
        loadError: 'Failed to load search index. Check docs/public/search-index.json.',
        noteCountSuffix: 'notes',
        lastEdited: 'Last edited',
        created: 'Created'
      }
    : {
        unknown: '未知',
        searchPlaceholder: '搜索标题或标签...',
        loading: '正在加载笔记...',
        loadError: '读取搜索索引失败，请检查 docs/public/search-index.json。',
        noteCountSuffix: '条笔记',
        lastEdited: '最后编辑',
        created: '创建时间'
      }
)

function applyQueryFromUrl(): void {
  if (typeof window === 'undefined') {
    return
  }
  const params = new URLSearchParams(window.location.search)
  const raw = (params.get('q') || '').trim()
  query.value = raw.startsWith('#') ? raw.slice(1) : raw
}

function parseTs(value?: string): number {
  if (!value) {
    return 0
  }
  const parsed = Date.parse(value)
  return Number.isNaN(parsed) ? 0 : parsed
}

function formatLocalTime(value?: string): string {
  const raw = String(value || '').trim()
  if (!raw) {
    return uiText.value.unknown
  }

  // Keep date-only values stable instead of letting timezone shifts change the day.
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
    return raw
  }

  const parsed = new Date(raw)
  if (Number.isNaN(parsed.getTime())) {
    return raw
  }

  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
    timeZoneName: 'short'
  }).format(parsed)
}

function sortByUpdatedDesc(items: NoteItem[]): NoteItem[] {
  return [...items].sort((a, b) => {
    const aTs = parseTs(a.updated_at || a.date)
    const bTs = parseTs(b.updated_at || b.date)
    return bTs - aTs
  })
}

const filteredNotes = computed(() => {
  const q = query.value.trim().toLowerCase()
  const base = q
    ? notes.value.filter((note) => {
        const haystack = [note.title, ...(note.tags || [])].join(' ').toLowerCase()
        return haystack.includes(q)
      })
    : notes.value

  return sortByUpdatedDesc(base)
})

function resolveLink(link: string): string {
  if (link.startsWith('http://') || link.startsWith('https://')) {
    return link
  }
  if (link.startsWith('/')) {
    return withBase(link)
  }
  return withBase(`/notes/${link.replace(/^\.\//, '')}`)
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
      const next = sortByUpdatedDesc(Array.isArray(payload?.notes) ? payload.notes : [])
      notes.value = next
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
  applyQueryFromUrl()
  await loadNotes(true)
  loading.value = false

  window.addEventListener('popstate', applyQueryFromUrl)

  pollTimer = window.setInterval(() => {
    void loadNotes(false)
  }, POLL_INTERVAL_MS)
})

onBeforeUnmount(() => {
  window.removeEventListener('popstate', applyQueryFromUrl)
  if (pollTimer !== undefined) {
    window.clearInterval(pollTimer)
  }
})
</script>

<template>
  <section class="note-explorer">
    <div class="note-explorer__controls">
      <input
        v-model="query"
        class="note-explorer__search"
        type="search"
        :placeholder="uiText.searchPlaceholder"
      />
    </div>

    <p v-if="loading" class="note-explorer__meta">{{ uiText.loading }}</p>
    <p v-else-if="error" class="note-explorer__error">{{ error }}</p>
    <p v-else class="note-explorer__meta">
      {{ filteredNotes.length }} / {{ notes.length }} {{ uiText.noteCountSuffix }}
    </p>

    <ol v-if="!loading && !error" class="note-explorer__list">
      <li v-for="note in filteredNotes" :key="`${note.link}-${note.updated_at || note.date}`" class="note-explorer__item">
        <a :href="resolveLink(note.link)" class="note-explorer__title">{{ note.title }}</a>
        <div class="note-explorer__time-row">
          <span class="note-explorer__time">{{ uiText.lastEdited }}: {{ formatLocalTime(note.updated_at || note.date) }}</span>
          <span class="note-explorer__time">{{ uiText.created }}: {{ formatLocalTime(note.created_at) }}</span>
        </div>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.note-explorer {
  border: 1px solid var(--vp-c-divider);
  border-radius: 16px;
  background: linear-gradient(170deg, rgba(255, 255, 255, 0.95), rgba(240, 253, 250, 0.95));
  padding: 18px;
}

.note-explorer__controls {
  display: grid;
  gap: 10px;
}

.note-explorer__search {
  width: 100%;
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  padding: 10px 12px;
  background: #fff;
}

.note-explorer__meta,
.note-explorer__error {
  margin-top: 12px;
  margin-bottom: 8px;
  font-size: 14px;
}

.note-explorer__error {
  color: #b91c1c;
}

.note-explorer__list {
  margin: 0;
  padding-left: 20px;
  display: grid;
  gap: 8px;
}

.note-explorer__item {
  padding: 6px 0;
}

.note-explorer__title {
  font-weight: 600;
  text-decoration: none;
}

.note-explorer__time-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 4px;
}

.note-explorer__time {
  color: var(--vp-c-text-2);
  font-size: 12px;
}

.dark .note-explorer {
  background: linear-gradient(165deg, rgba(12, 18, 31, 0.95), rgba(8, 47, 73, 0.35));
  border-color: rgba(148, 163, 184, 0.28);
}

.dark .note-explorer__search {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(148, 163, 184, 0.28);
}

.dark .note-explorer__error {
  color: #fca5a5;
}
</style>
