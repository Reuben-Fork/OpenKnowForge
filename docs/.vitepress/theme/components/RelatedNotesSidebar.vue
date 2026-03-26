<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, withBase } from 'vitepress'

type NoteItem = {
  slug?: string
  title: string
  date?: string
  updated_at?: string
  tags?: string[]
  link: string
}

type RelatedNote = NoteItem & {
  overlap: number
}

const route = useRoute()
const notes = ref<NoteItem[]>([])
const loading = ref(false)
const isEn = computed(() => route.path.startsWith('/en/'))

function normalizePath(value?: string): string {
  const raw = String(value || '').trim()
  if (!raw) {
    return '/'
  }
  const next = raw.replace(/\/+$/, '')
  return next || '/'
}

function isNoteDetailPath(value?: string): boolean {
  const normalized = normalizePath(value)
  return normalized.startsWith('/notes/entries/') && normalized !== '/notes/entries'
}

function parseTs(value?: string): number {
  if (!value) {
    return 0
  }
  const parsed = Date.parse(value)
  return Number.isNaN(parsed) ? 0 : parsed
}

function normalizeTag(value: string): string {
  return value.trim().toLowerCase()
}

function resolveLink(link: string): string {
  if (link.startsWith('http://') || link.startsWith('https://')) {
    return link
  }
  if (link.startsWith('/')) {
    return withBase(link)
  }
  return withBase(`/notes/${link.replace(/^\.\//, '')}`)
}

const enabled = computed(() => isNoteDetailPath(route.path))

const currentPath = computed(() => normalizePath(route.path))

const uiText = computed(() =>
  isEn.value
    ? {
        title: 'Related Notes',
        loading: 'Loading...',
        notIndexed: 'Current note is not indexed yet.',
        noTag: 'Current note has no tags.',
        empty: 'No notes with overlapping tags.'
      }
    : {
        title: '相关笔记',
        loading: '加载中...',
        notIndexed: '当前笔记尚未进入索引。',
        noTag: '当前笔记没有标签。',
        empty: '没有找到标签重叠的笔记。'
      }
)

const currentNote = computed<NoteItem | null>(() => {
  if (!enabled.value) {
    return null
  }
  return notes.value.find((item) => normalizePath(item.link) === currentPath.value) || null
})

const relatedNotes = computed<RelatedNote[]>(() => {
  const current = currentNote.value
  if (!current) {
    return []
  }

  const currentTags = (current.tags || []).map(normalizeTag).filter(Boolean)
  if (currentTags.length === 0) {
    return []
  }
  const tagSet = new Set(currentTags)

  return notes.value
    .filter((item) => normalizePath(item.link) !== currentPath.value)
    .map((item) => {
      const overlap = (item.tags || []).map(normalizeTag).filter((tag) => tagSet.has(tag)).length
      return {
        ...item,
        overlap
      }
    })
    .filter((item) => item.overlap > 0)
    .sort((a, b) => {
      if (b.overlap !== a.overlap) {
        return b.overlap - a.overlap
      }
      const timeDelta = parseTs(b.updated_at || b.date) - parseTs(a.updated_at || a.date)
      if (timeDelta !== 0) {
        return timeDelta
      }
      return a.title.localeCompare(b.title)
    })
})

function syncBodyClass(active: boolean): void {
  if (typeof document === 'undefined') {
    return
  }
  document.body.classList.toggle('related-sidebar-mode', active)
}

async function loadNotes(): Promise<void> {
  if (!enabled.value) {
    notes.value = []
    return
  }

  loading.value = true
  const candidates = Array.from(
    new Set([
      withBase('/search-index.json'),
      withBase('/.vitepress/public/search-index.json'),
      '/search-index.json',
      '/.vitepress/public/search-index.json'
    ])
  )

  try {
    for (const candidate of candidates) {
      const response = await fetch(candidate, { cache: 'no-store' })
      if (!response.ok) {
        continue
      }
      const payload = await response.json()
      notes.value = Array.isArray(payload?.notes) ? payload.notes : []
      return
    }

    notes.value = []
  } catch {
    notes.value = []
  } finally {
    loading.value = false
  }
}

watch(
  () => enabled.value,
  (value) => {
    syncBodyClass(value)
    if (value) {
      void loadNotes()
    } else {
      notes.value = []
    }
  },
  { immediate: true }
)

watch(
  () => route.path,
  () => {
    if (enabled.value) {
      void loadNotes()
    }
  }
)

onMounted(() => {
  syncBodyClass(enabled.value)
})

onBeforeUnmount(() => {
  syncBodyClass(false)
})
</script>

<template>
  <section v-if="enabled" class="related-notes-sidebar">
    <p class="related-notes-sidebar__title">{{ uiText.title }}</p>
    <p v-if="loading" class="related-notes-sidebar__meta">{{ uiText.loading }}</p>
    <p v-else-if="!currentNote" class="related-notes-sidebar__meta">{{ uiText.notIndexed }}</p>
    <p v-else-if="(currentNote.tags || []).length === 0" class="related-notes-sidebar__meta">{{ uiText.noTag }}</p>
    <ul v-else-if="relatedNotes.length > 0" class="related-notes-sidebar__list">
      <li v-for="note in relatedNotes" :key="`${note.link}-${note.overlap}`" class="related-notes-sidebar__item">
        <a :href="resolveLink(note.link)" class="related-notes-sidebar__link">{{ note.title }}</a>
      </li>
    </ul>
    <p v-else class="related-notes-sidebar__meta">{{ uiText.empty }}</p>
  </section>
</template>

<style scoped>
.related-notes-sidebar {
  margin: 0 0 12px;
}

.related-notes-sidebar__title {
  margin: 0 0 10px 0;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: none;
  color: var(--vp-c-text-1);
}

.related-notes-sidebar__meta {
  margin: 0;
  font-size: 12px;
  color: var(--vp-c-text-2);
}

.related-notes-sidebar__list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.related-notes-sidebar__item {
  margin: 0;
}

.related-notes-sidebar__link {
  display: inline-block;
  font-size: 13px;
  line-height: 1.3;
  color: var(--vp-c-text-2);
  text-decoration: none;
}

.related-notes-sidebar__link:hover {
  color: var(--vp-c-brand-1);
}
</style>
