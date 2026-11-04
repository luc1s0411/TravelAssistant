import type { Envelope } from './types'

const baseUrl = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')
let accessToken: string | null = null
// 只在内存中保留会话；刷新恢复策略由登录模块统一确定。
export function setAccessToken(value: string | null) { accessToken = value }

export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string, public requestId?: string, public details?: unknown) {
    super(message)
  }
}
interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown
  timeoutMs?: number
  idempotencyKey?: string
}
export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, timeoutMs = 15_000, idempotencyKey, ...init } = options
  const headers = new Headers(init.headers)
  if (body !== undefined) headers.set('Content-Type', 'application/json')
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`)
  if (idempotencyKey) headers.set('Idempotency-Key', idempotencyKey)
  const controller = new AbortController()
  const abortFromCaller = () => controller.abort()
  init.signal?.addEventListener('abort', abortFromCaller, { once: true })
  if (init.signal?.aborted) controller.abort()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const result = await fetch(`${baseUrl}${path}`, {
      ...init, headers, signal: controller.signal,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
    const payload = await result.json() as Envelope<T>
    if (!result.ok || payload.code !== 'OK') throw new ApiError(result.status, payload.code, payload.message, payload.request_id, payload.data)
    return payload.data
  } catch (error) {
    if (error instanceof ApiError) throw error
    if (controller.signal.aborted) throw new ApiError(0, 'REQUEST_ABORTED', '请求已超时或取消；请核实保存状态后重试')
    throw new ApiError(0, 'NETWORK_ERROR', '未取得有效响应，请检查网络和后端服务')
  } finally {
    clearTimeout(timer)
    init.signal?.removeEventListener('abort', abortFromCaller)
  }
}
export function queryString(values: Record<string, string | number | undefined>): string {
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(values)) if (value !== undefined) query.set(key, String(value))
  return `?${query.toString()}`
}
