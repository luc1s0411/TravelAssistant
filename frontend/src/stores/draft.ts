import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Draft } from '../api/types'

export const useDraftStore = defineStore('draft', () => {
  const current = ref<Draft | null>(null)
  const loading = ref(false)
  // 接口成功后才能调用，不把浏览器状态视为后端持久保存。
  function acceptSavedDraft(draft: Draft) { current.value = draft }
  function clear() { current.value = null }
  return { current, loading, acceptSavedDraft, clear }
})
