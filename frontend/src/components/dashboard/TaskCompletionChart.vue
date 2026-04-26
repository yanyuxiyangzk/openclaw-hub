<template>
  <div class="chart-card">
    <div class="chart-header">
      <h3>任务完成趋势</h3>
      <el-select v-model="days" size="small" style="width: 100px" @change="fetchData">
        <el-option :value="7" label="近7天" />
        <el-option :value="14" label="近14天" />
        <el-option :value="30" label="近30天" />
      </el-select>
    </div>
    <div ref="chartRef" class="chart-container"></div>
    <div v-if="loading" class="chart-loading">加载中...</div>
    <div v-if="!loading && hasNoData" class="chart-empty">暂无数据</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { dashboardApi } from '../../api/dashboard'

const chartRef = ref<HTMLDivElement>()
let chartInstance: echarts.ECharts | null = null

const days = ref(7)
const loading = ref(false)
const hasNoData = ref(false)

const fetchData = async () => {
  if (!chartInstance) return
  loading.value = true
  try {
    const res = await dashboardApi.getTaskCompletionChart(days.value)
    if (res.data.code !== 0) return
    const { labels, completed, failed } = res.data.data
    hasNoData.value = completed.every((n: number) => n === 0) && failed.every((n: number) => n === 0)
    chartInstance.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['已完成', '已失败'], bottom: 0 },
      grid: { top: 10, right: 20, bottom: 50, left: 50 },
      xAxis: { type: 'category', data: labels },
      yAxis: { type: 'value', name: '任务数' },
      series: [
        { name: '已完成', type: 'line', data: completed, itemStyle: { color: '#67c23a' } },
        { name: '已失败', type: 'line', data: failed, itemStyle: { color: '#f56c6c' } },
      ],
    })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    fetchData()
  }
})

onUnmounted(() => {
  chartInstance?.dispose()
})
</script>

<style scoped>
.chart-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.chart-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}
.chart-container {
  width: 100%;
  height: 260px;
}
.chart-loading,
.chart-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #999;
}
</style>
