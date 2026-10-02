<template>
  <section class="page">
    <header class="page-head">
      <div>
        <h2>运营概览</h2>
        <p class="page-desc">
          汇总各业务模块的关键指标，先看总量再看异常。
          <span v-if="seedVersion">种子口径 {{ seedVersion }}，与各模块明细同一份数据。</span>
        </p>
      </div>
    </header>
    <div class="stat-row">
      <article v-for="card in cards" :key="card.label" class="stat-card">
        <span class="stat-label">{{ card.label }}</span>
        <strong class="stat-value">{{ card.value }}</strong>
      </article>
    </div>
    <table class="data-table">
      <thead>
        <tr><th>业务模块</th><th>记录总数</th><th>待处理</th><th>异常量</th></tr>
      </thead>
      <tbody>
        <tr v-for="row in moduleRows" :key="row.name">
          <td>{{ row.label }}</td>
          <td>{{ row.total }}</td>
          <td>{{ row.pending }}</td>
          <td>{{ row.abnormal }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { fetchJson } from '@/api/client'

type Overview = {
  seed_version?: string
  cards: { label: string; value: number }[]
  modules: { name: string; label: string; total: number; pending: number; abnormal: number }[]
}

const cards = ref<Overview['cards']>([])
const moduleRows = ref<Overview['modules']>([])
const seedVersion = ref('')

onMounted(async () => {
  try {
    const payload = await fetchJson<Overview>('/api/overview')
    cards.value = payload.cards
    moduleRows.value = payload.modules
    seedVersion.value = payload.seed_version ?? ''
  } catch {
    cards.value = [
      { label: '业务模块', value: 0 },
      { label: '记录总数', value: 0 },
      { label: '待处理', value: 0 },
      { label: '异常量', value: 0 },
    ]
    moduleRows.value = []
  }
})
</script>
