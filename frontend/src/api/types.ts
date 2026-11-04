// 来自后端 OpenAPI 的唯一类型快照；更新后运行 npm run api:types。
import type { components } from './generated'
type Schema = components['schemas']
export type Category = 'lodging' | 'dining' | 'attraction'
export type TripInput = Schema['DraftCreate']['trip']
export type Draft = Schema['DraftOut']
export type DraftCreate = Schema['DraftCreate']
export type DraftUpdate = Schema['DraftUpdate']
export type SelectionCreate = Schema['SelectionCreate']
export type CatalogItem = Schema['CatalogItem']
export type LoginRequest = Schema['LoginRequest']
export type LoginResult = Schema['LoginResult']
export type User = Schema['UserOut']
export type AssistantReply = Schema['AssistantReply']
export type ConfirmRequest = Schema['ConfirmRequest']
export type ConfirmedInput = Schema['ConfirmedInput']
export type PlanCreate = Schema['PlanCreate']
export type PlanningRequest = Schema['PlanningRequestOut']
export type PlanRename = Schema['PlanRename']
export type Plan = Schema['PlanOut']
export type PlanSummary = Schema['PlanSummary']
export type PlanItem = Schema['PlanItem']
export type RevisionRequest = Schema['RevisionRequest']
export type RevisionPreview = Schema['RevisionPreview']
export type RouteRequest = Schema['RouteRequest']
export type RouteResult = Schema['RouteResult']
export type WeatherResult = Schema['WeatherResult']
export interface Envelope<T> { code: string; message: string; data: T; request_id: string }
export interface Page<T> { items: T[]; next_cursor: string | null; has_more: boolean }
