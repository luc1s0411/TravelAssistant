import { queryString, request } from './client'
import type * as T from './types'

const id = encodeURIComponent
export const authApi = {
  login: (body: T.LoginRequest) => request<T.LoginResult>('/auth/login', { method: 'POST', body }),
  logout: () => request<null>('/auth/logout', { method: 'POST' }),
  me: () => request<T.User>('/auth/me'),
}
export const draftApi = {
  create: (body: T.DraftCreate) => request<T.Draft>('/drafts', { method: 'POST', body }),
  get: (draftId: string) => request<T.Draft>(`/drafts/${id(draftId)}`),
  update: (draftId: string, body: T.DraftUpdate) => request<T.Draft>(`/drafts/${id(draftId)}`, { method: 'PATCH', body }),
  addSelection: (draftId: string, body: T.SelectionCreate, key: string) => request<T.Draft>(`/drafts/${id(draftId)}/selections`, { method: 'POST', body, idempotencyKey: key }),
  removeSelection: (draftId: string, selectionId: string, revision: number) => request<T.Draft>(`/drafts/${id(draftId)}/selections/${id(selectionId)}?expected_revision=${revision}`, { method: 'DELETE' }),
  message: (draftId: string, message: string) => request<T.AssistantReply>(`/drafts/${id(draftId)}/assistant/messages`, { method: 'POST', body: { message } }),
  confirm: (draftId: string, body: T.ConfirmRequest) => request<T.ConfirmedInput>(`/drafts/${id(draftId)}/confirm`, { method: 'POST', body }),
}
export const catalogApi = {
  search: (draftId: string, category: T.Category, cursor?: string) => request<T.Page<T.CatalogItem>>(`/catalog/search${queryString({ draft_id: draftId, category, cursor })}`),
  get: (itemRef: string) => request<T.CatalogItem>(`/catalog/items/${id(itemRef)}`),
}
export const planApi = {
  create: (body: T.PlanCreate, key: string) => request<T.PlanningRequest>('/plans', { method: 'POST', body, idempotencyKey: key }),
  getRequest: (requestId: string) => request<T.PlanningRequest>(`/planning-requests/${id(requestId)}`),
  list: (cursor?: string) => request<T.Page<T.PlanSummary>>(`/plans${queryString({ cursor })}`),
  get: (planId: string) => request<T.Plan>(`/plans/${id(planId)}`),
  rename: (planId: string, body: T.PlanRename) => request<T.PlanSummary>(`/plans/${id(planId)}`, { method: 'PATCH', body }),
  archive: (planId: string, version: number) => request<null>(`/plans/${id(planId)}?expected_version=${version}`, { method: 'DELETE' }),
  items: (planId: string, date?: string, category?: T.Category) => request<T.PlanItem[]>(`/plans/${id(planId)}/items${queryString({ date, category })}`),
  message: (planId: string, message: string) => request<T.AssistantReply>(`/plans/${id(planId)}/assistant/messages`, { method: 'POST', body: { message } }),
  preview: (planId: string, body: T.RevisionRequest) => request<T.RevisionPreview>(`/plans/${id(planId)}/revisions/preview`, { method: 'POST', body, timeoutMs: 120_000 }),
  confirmRevision: (planId: string, previewId: string, version: number, key: string) => request<T.Plan>(`/plans/${id(planId)}/revisions/${id(previewId)}/confirm`, { method: 'POST', body: { expected_version: version }, idempotencyKey: key, timeoutMs: 120_000 }),
}
export const integrationApi = {
  route: (body: T.RouteRequest) => request<T.RouteResult>('/routes/estimate', { method: 'POST', body }),
  weather: (date: string, longitude: number, latitude: number) => request<T.WeatherResult>(`/weather${queryString({ date, longitude, latitude })}`),
}
