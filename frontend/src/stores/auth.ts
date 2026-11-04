import { defineStore } from 'pinia'
import { ref } from 'vue'
import { setAccessToken } from '../api/client'
import type { LoginResult, User } from '../api/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  function acceptSession(result: LoginResult) { setAccessToken(result.access_token); user.value = result.user }
  function clearSession() { setAccessToken(null); user.value = null }
  return { user, acceptSession, clearSession }
})
