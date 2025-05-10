<template>
  <div v-if="loading" class="text-center py-5">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">加载中...</span>
    </div>
  </div>
  
  <div v-else-if="dataset" class="data-analysis">
    <div class="d-flex justify-content-between align-items-start mb-4">
      <div>
        <h2>数据分析与预测</h2>
        <p class="text-muted">{{ dataset.name }}</p>
      </div>
      <div>
        <router-link 
          :to="`/dataset/${dataset.id}`" 
          class="btn btn-outline-secondary"
        >
          返回数据集
        </router-link>
      </div>
    </div>
    
    <!-- 分析选项卡 -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <a 
          class="nav-link" 
          :class="{ active: activeTab === 'visualization' }"
          href="#"
          @click.prevent="activeTab = 'visualization'"
        >
          数据可视化
        </a>
      </li>
      <li class="nav-item">
        <a 
          class="nav-link" 
          :class="{ active: activeTab === 'prediction' }"
          href="#"
          @click.prevent="activeTab = 'prediction'"
        >
          房价预测
        </a>
      </li>
    </ul>
    
    <!-- 可视化面板 -->
    <div v-if="activeTab === 'visualization'" class="visualization-panel">
      <div class="row">
        <div class="col-md-4">
          <div class="card shadow-sm">
            <div class="card-header">
              <h5 class="mb-0">创建图表</h5>
            </div>
            <div class="card-body">
              <div v-if="visualizationError" class="alert alert-danger">
                {{ visualizationError }}
              </div>
              
              <form @submit.prevent="createVisualization">
                <div class="mb-3">
                  <label for="chartName" class="form-label">图表名称</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="chartName" 
                    v-model="visualizationForm.name"
                    required
                  >
                </div>
                
                <div class="mb-3">
                  <label for="chartType" class="form-label">图表类型</label>
                  <select 
                    class="form-select" 
                    id="chartType" 
                    v-model="visualizationForm.chartType"
                    required
                  >
                    <option value="">选择图表类型</option>
                    <option value="bar">柱状图</option>
                    <option value="line">折线图</option>
                    <option value="scatter">散点图</option>
                    <option value="histogram">直方图</option>
                    <option value="box">箱线图</option>
                    <option value="heatmap">相关性热图</option>
                  </select>
                </div>
                
                <!-- 根据图表类型显示不同的配置选项 -->
                <template v-if="visualizationForm.chartType && visualizationForm.chartType !== 'heatmap'">
                  <div class="mb-3" v-if="visualizationForm.chartType !== 'histogram'">
                    <label for="xAxis" class="form-label">X轴</label>
                    <select 
                      class="form-select" 
                      id="xAxis" 
                      v-model="visualizationForm.config.x"
                      required
                    >
                      <option value="">选择列</option>
                      <option 
                        v-for="col in columns" 
                        :key="col.name" 
                        :value="col.name"
                      >
                        {{ col.name }}
                      </option>
                    </select>
                  </div>
                  
                  <div class="mb-3" v-if="visualizationForm.chartType !== 'histogram'">
                    <label for="yAxis" class="form-label">Y轴</label>
                    <select 
                      class="form-select" 
                      id="yAxis" 
                      v-model="visualizationForm.config.y"
                      required
                    >
                      <option value="">选择列</option>
                      <option 
                        v-for="col in numericColumns" 
                        :key="col.name" 
                        :value="col.name"
                      >
                        {{ col.name }}
                      </option>
                    </select>
                  </div>
                  
                  <div class="mb-3" v-if="visualizationForm.chartType === 'histogram'">
                    <label for="histColumn" class="form-label">数据列</label>
                    <select 
                      class="form-select" 
                      id="histColumn" 
                      v-model="visualizationForm.config.x"
                      required
                    >
                      <option value="">选择列</option>
                      <option 
                        v-for="col in numericColumns" 
                        :key="col.name" 
                        :value="col.name"
                      >
                        {{ col.name }}
                      </option>
                    </select>
                  </div>
                  
                  <div class="mb-3" v-if="['bar', 'line', 'scatter'].includes(visualizationForm.chartType)">
                    <label for="hue" class="form-label">分组 (可选)</label>
                    <select 
                      class="form-select" 
                      id="hue" 
                      v-model="visualizationForm.config.hue"
                    >
                      <option value="">不分组</option>
                      <option 
                        v-for="col in categoricalColumns" 
                        :key="col.name" 
                        :value="col.name"
                      >
                        {{ col.name }}
                      </option>
                    </select>
                  </div>
                  
                  <div class="mb-3" v-if="visualizationForm.chartType === 'histogram'">
                    <label for="bins" class="form-label">分箱数量</label>
                    <input 
                      type="number" 
                      class="form-control" 
                      id="bins" 
                      v-model.number="visualizationForm.config.bins"
                      min="5"
                      max="50"
                      value="10"
                    >
                  </div>
                </template>
                
                <template v-if="visualizationForm.chartType === 'heatmap'">
                  <div class="mb-3">
                    <label class="form-label">选择要包含的列</label>
                    <div class="form-check" v-for="col in numericColumns" :key="col.name">
                      <input 
                        class="form-check-input" 
                        type="checkbox" 
                        :id="`col-${col.name}`"
                        :value="col.name"
                        v-model="visualizationForm.config.columns"
                      >
                      <label class="form-check-label" :for="`col-${col.name}`">
                        {{ col.name }}
                      </label>
                    </div>
                    <div class="form-text" v-if="visualizationForm.config.columns.length < 2">
                      请至少选择两列进行相关性分析
                    </div>
                  </div>
                </template>
                
                <div class="mb-3">
                  <label for="chartTitle" class="form-label">图表标题 (可选)</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="chartTitle" 
                    v-model="visualizationForm.config.title"
                    placeholder="图表标题"
                  >
                </div>
                
                <div class="d-grid">
                  <button 
                    type="submit" 
                    class="btn btn-primary"
                    :disabled="creatingVisualization || !canCreateVisualization"
                  >
                    <span v-if="creatingVisualization" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    {{ creatingVisualization ? '生成中...' : '生成图表' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
        
        <div class="col-md-8">
          <div class="card shadow-sm">
            <div class="card-header">
              <h5 class="mb-0">图表预览</h5>
            </div>
            <div class="card-body text-center p-4">
              <div v-if="currentVisualization" class="mb-3">
                <h6>{{ currentVisualization.name }}</h6>
                <img 
                  :src="currentVisualization.imageUrl" 
                  alt="Visualization" 
                  class="img-fluid border rounded"
                >
              </div>
              <div v-else class="py-5 text-muted">
                <i class="bi bi-bar-chart-line display-1 mb-3"></i>
                <p>创建图表后在此处显示</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 预测面板 -->
    <div v-if="activeTab === 'prediction'" class="prediction-panel">
      <div class="row">
        <div class="col-md-4">
          <div class="card shadow-sm">
            <div class="card-header">
              <h5 class="mb-0">训练预测模型</h5>
            </div>
            <div class="card-body">
              <div v-if="predictionError" class="alert alert-danger">
                {{ predictionError }}
              </div>
              
              <form @submit.prevent="trainPredictionModel">
                <div class="mb-3">
                  <label for="modelName" class="form-label">模型名称</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="modelName" 
                    v-model="predictionForm.name"
                    required
                  >
                </div>
                
                <div class="mb-3">
                  <label for="algorithm" class="form-label">算法</label>
                  <select 
                    class="form-select" 
                    id="algorithm" 
                    v-model="predictionForm.algorithm"
                    required
                  >
                    <option value="">选择算法</option>
                    <option value="linear_regression">线性回归</option>
                    <option value="random_forest">随机森林</option>
                  </select>
                </div>
                
                <div class="mb-3">
                  <label for="target" class="form-label">目标变量 (房价)</label>
                  <select 
                    class="form-select" 
                    id="target" 
                    v-model="predictionForm.target"
                    required
                  >
                    <option value="">选择目标列</option>
                    <option 
                      v-for="col in numericColumns" 
                      :key="col.name" 
                      :value="col.name"
                    >
                      {{ col.name }}
                    </option>
                  </select>
                </div>
                
                <div class="mb-3">
                  <label class="form-label">特征变量</label>
                  <div 
                    v-for="col in columns" 
                    :key="col.name"
                    class="form-check"
                  >
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      :id="`feature-${col.name}`"
                      :value="col.name"
                      v-model="predictionForm.features"
                      :disabled="predictionForm.target === col.name"
                    >
                    <label class="form-check-label" :for="`feature-${col.name}`">
                      {{ col.name }}
                    </label>
                  </div>
                  <div class="form-text" v-if="predictionForm.features.length === 0">
                    请至少选择一个特征
                  </div>
                </div>
                
                <div class="d-grid">
                  <button 
                    type="submit" 
                    class="btn btn-primary"
                    :disabled="trainingModel || !canTrainModel"
                  >
                    <span v-if="trainingModel" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    {{ trainingModel ? '训练中...' : '训练模型' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
        
        <div class="col-md-8">
          <div class="card shadow-sm mb-4">
            <div class="card-header">
              <h5 class="mb-0">模型评估</h5>
            </div>
            <div class="card-body">
              <div v-if="currentPrediction" class="mb-3">
                <h6>{{ currentPrediction.name }} ({{ getAlgorithmLabel(currentPrediction.algorithm) }})</h6>
                
                <div class="row text-center mt-4">
                  <div class="col-md-4">
                    <div class="card bg-light">
                      <div class="card-body">
                        <h2 class="text-primary">{{ formatNumber(currentPrediction.metrics.r2) }}</h2>
                        <p class="mb-0">R² 决定系数</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="card bg-light">
                      <div class="card-body">
                        <h2 class="text-primary">{{ formatNumber(currentPrediction.metrics.mse) }}</h2>
                        <p class="mb-0">均方误差 (MSE)</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="card bg-light">
                      <div class="card-body">
                        <h2 class="text-primary">{{ formatNumber(currentPrediction.metrics.rmse) }}</h2>
                        <p class="mb-0">均方根误差 (RMSE)</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="mt-4">
                  <h6>使用的特征:</h6>
                  <div class="d-flex flex-wrap gap-2">
                    <span 
                      v-for="feature in currentPrediction.features" 
                      :key="feature"
                      class="badge bg-secondary"
                    >
                      {{ feature }}
                    </span>
                  </div>
                </div>
              </div>
              <div v-else class="py-5 text-center text-muted">
                <i class="bi bi-cpu display-1 mb-3"></i>
                <p>训练模型后在此处显示评估指标</p>
              </div>
            </div>
          </div>
          
          <div class="card shadow-sm">
            <div class="card-header">
              <h5 class="mb-0">历史模型</h5>
            </div>
            <div class="card-body">
              <div v-if="loadingPredictions" class="text-center py-3">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                  <span class="visually-hidden">加载中...</span>
                </div>
                <span class="ms-2">加载历史模型...</span>
              </div>
              
              <div v-else-if="predictions.length === 0" class="text-center py-3 text-muted">
                暂无历史模型
              </div>
              
              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>名称</th>
                      <th>算法</th>
                      <th>R²</th>
                      <th>RMSE</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="prediction in predictions" :key="prediction.id">
                      <td>{{ prediction.name }}</td>
                      <td>{{ getAlgorithmLabel(prediction.algorithm) }}</td>
                      <td>{{ formatNumber(prediction.metrics.r2) }}</td>
                      <td>{{ formatNumber(prediction.metrics.rmse) }}</td>
                      <td>
                        <button 
                          class="btn btn-sm btn-outline-primary"
                          @click="selectPrediction(prediction)"
                        >
                          查看
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataAnalysis',
  data() {
    return {
      loading: true,
      activeTab: 'visualization',
      columns: [],
      
      // 可视化相关
      visualizationForm: {
        name: '',
        chartType: '',
        config: {
          x: '',
          y: '',
          hue: '',
          title: '',
          bins: 10,
          columns: []
        }
      },
      creatingVisualization: false,
      visualizationError: null,
      currentVisualization: null,
      
      // 预测相关
      predictionForm: {
        name: '',
        algorithm: '',
        target: '',
        features: []
      },
      trainingModel: false,
      predictionError: null,
      currentPrediction: null,
      predictions: [],
      loadingPredictions: false
    }
  },
  computed: {
    dataset() {
      return this.$store.getters.currentDataset
    },
    datasetId() {
      return Number(this.$route.params.id)
    },
    numericColumns() {
      return this.columns.filter(col => col.type === 'numeric')
    },
    categoricalColumns() {
      return this.columns.filter(col => col.type === 'categorical')
    },
    canCreateVisualization() {
      const { chartType, config } = this.visualizationForm
      
      if (!chartType) return false
      
      if (chartType === 'histogram') {
        return !!config.x
      }
      
      if (chartType === 'heatmap') {
        return config.columns && config.columns.length >= 2
      }
      
      return !!config.x && !!config.y
    },
    canTrainModel() {
      const { algorithm, target, features } = this.predictionForm
      return !!algorithm && !!target && features.length > 0
    }
  },
  mounted() {
    this.fetchDataset()
  },
  watch: {
    activeTab(newTab) {
      if (newTab === 'prediction' && !this.predictions.length && !this.loadingPredictions) {
        this.fetchPredictions()
      }
    },
    'predictionForm.target'(newValue) {
      // 当目标变量改变时，移除特征列表中的目标变量
      if (newValue && this.predictionForm.features.includes(newValue)) {
        this.predictionForm.features = this.predictionForm.features.filter(f => f !== newValue)
      }
    }
  },
  methods: {
    async fetchDataset() {
      this.loading = true
      
      try {
        const result = await this.$store.dispatch('fetchDataset', this.datasetId)
        
        if (result.success) {
          this.columns = JSON.parse(this.dataset.columns)
          
          // 如果是预测标签，加载历史预测
          if (this.activeTab === 'prediction') {
            this.fetchPredictions()
          }
        }
      } catch (err) {
        console.error('获取数据集失败', err)
      } finally {
        this.loading = false
      }
    },
    
    async createVisualization() {
      if (!this.canCreateVisualization) return
      
      this.creatingVisualization = true
      this.visualizationError = null
      
      try {
        const result = await this.$store.dispatch('createVisualization', {
          datasetId: this.datasetId,
          chartType: this.visualizationForm.chartType,
          config: this.visualizationForm.config,
          name: this.visualizationForm.name
        })
        
        if (result.success) {
          this.currentVisualization = {
            name: this.visualizationForm.name,
            chartType: this.visualizationForm.chartType,
            imageUrl: result.imageUrl
          }
          
          // 重置表单
          this.visualizationForm.name = ''
          this.visualizationForm.config.title = ''
        } else {
          this.visualizationError = result.error
        }
      } catch (err) {
        this.visualizationError = '创建可视化失败'
        console.error(err)
      } finally {
        this.creatingVisualization = false
      }
    },
    
    async fetchPredictions() {
      this.loadingPredictions = true
      
      try {
        const result = await this.$store.dispatch('getPredictions', this.datasetId)
        
        if (result.success) {
          this.predictions = result.predictions
          
          // 如果有预测记录，默认选择第一个
          if (this.predictions.length > 0) {
            this.selectPrediction(this.predictions[0])
          }
        }
      } catch (err) {
        console.error('获取预测记录失败', err)
      } finally {
        this.loadingPredictions = false
      }
    },
    
    async trainPredictionModel() {
      if (!this.canTrainModel) return
      
      this.trainingModel = true
      this.predictionError = null
      
      try {
        const result = await this.$store.dispatch('trainModel', {
          datasetId: this.datasetId,
          algorithm: this.predictionForm.algorithm,
          features: this.predictionForm.features,
          target: this.predictionForm.target,
          name: this.predictionForm.name
        })
        
        if (result.success) {
          // 重新获取预测记录
          await this.fetchPredictions()
          
          // 重置表单
          this.predictionForm.name = ''
        } else {
          this.predictionError = result.error
        }
      } catch (err) {
        this.predictionError = '模型训练失败'
        console.error(err)
      } finally {
        this.trainingModel = false
      }
    },
    
    selectPrediction(prediction) {
      this.currentPrediction = prediction
    },
    
    getAlgorithmLabel(algorithm) {
      const algorithmMap = {
        'linear_regression': '线性回归',
        'random_forest': '随机森林'
      }
      return algorithmMap[algorithm] || algorithm
    },
    
    formatNumber(value) {
      if (typeof value !== 'number') return value
      
      // 显示3位小数
      return value.toFixed(3)
    }
  }
}
</script>

<style scoped>
.card {
  transition: all 0.3s ease;
}
.card:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}
</style> 