/** 模块页共用口径：列名、动作、统计卡都从后端登记表取，统计数值与概览、明细同源。 */
import { computed, onMounted, ref } from 'vue'

import { fetchModules, fetchOverview } from '@/api/modules'

export type StatCard = { label: string; value: number }

export function useModuleMeta(moduleKey: string) {
  const columns = ref<string[]>([])
  const actions = ref<string[]>([])
  const stats = ref<StatCard[]>([])
  const statDefs = ref<{ label: string; status: string }[]>([])

  const filterFields = computed(() => columns.value.slice(0, 3))

  async function refreshStats() {
    // 统计卡与运营概览、模块列表数自后端同一份数据；失败时保持现有卡片不动
    try {
      const overview = await fetchOverview()
      const current = overview.modules.find((item) => item.key === moduleKey)
      const counts = current?.status_counts ?? {}
      stats.value = statDefs.value.map((def) => ({
        label: def.label,
        value: counts[def.status] ?? 0,
      }))
    } catch {
      // 概览暂时取不到时不打断列表展示
    }
  }

  onMounted(async () => {
    try {
      const modules = await fetchModules()
      const meta = modules.find((item) => item.key === moduleKey)
      columns.value = meta?.fields ?? []
      actions.value = meta?.actions ?? []
      statDefs.value = meta?.stats ?? []
    } catch {
      columns.value = []
      actions.value = []
      statDefs.value = []
    }
    await refreshStats()
  })

  return { columns, actions, stats, filterFields, refreshStats }
}
