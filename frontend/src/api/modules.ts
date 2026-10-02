/** 模块登记表与运营概览的取数封装：全前端共用一份，页面不再各自维护字段与状态。 */
import { fetchJson } from '@/api/client'

export type ModuleStat = { label: string; status: string }

export type ModuleMeta = {
  key: string
  title: string
  noun: string
  fields: string[]
  statuses: string[]
  actions: string[]
  stats: ModuleStat[]
}

export type OverviewModule = {
  key: string
  name: string
  created: number
  pending: number
  abnormal: number
  status_counts: Record<string, number>
}

export type Overview = {
  cards: { label: string; value: number }[]
  modules: OverviewModule[]
}

let metaCache: Promise<ModuleMeta[]> | null = null

export function fetchModules(): Promise<ModuleMeta[]> {
  // 登记表全站共用一份；失败时清掉缓存，下次重试而不是一直拿着 rejected Promise
  metaCache ??= fetchJson<ModuleMeta[]>('/api/modules').catch((error: unknown) => {
    metaCache = null
    throw error
  })
  return metaCache
}

export function fetchOverview(): Promise<Overview> {
  return fetchJson<Overview>('/api/overview')
}
