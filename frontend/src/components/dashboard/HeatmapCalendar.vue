<template>
  <div class="chart-card">
    <div class="chart-header">
      <h3>活动热力图</h3>
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
    const res = await dashboardApi.getActivityHeatmap(days.value)
    if (res.data.code !== 0) return
    const { days: daysLabels, hours, values } = res.data.data

    // Build heatmap data: [hour, dayIndex, value]
    const heatmapData: [number, number, number][] = []
    for (let d = 0; d < values.length; d++) {
      for (let h = 0; h < values[d].length; h++) {
        heatmapData.push([h, d, values[d][h]])
      }
    }

    hasNoData.value = values.every((row: number[]) => row.every((v: number) => v === 0))

    chartInstance.setOption({
      tooltip: {
        formatter: (params: any) =>
          `${daysLabels[params.value[1]]} ${params.value[0]}:00<br/>活动: ${params.value[2]}次`,
      },
      grid: { top: 10, right: 60, bottom: 60, left: 60 },
      xAxis: {
        type: 'category',
        data: hours.map(h => `${h}:00`),
        name: '小时',
        splitArea: { show: true },
      },
      yAxis: {
        type: 'category',
        data: daysLabels,
        name: '星期',
        splitArea: { show: true },
      },
      visualMap: {
        min: 0,
        max: Math.max(...values.flat(), 1),
        calculable: true,
        orient: 'vertical',
        right: 10,
        top: 'center',
      },
      series: [{
        type: 'heatmap',
        data: heatmapData,
        label: { show: false },
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' },
        },
      }],
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
