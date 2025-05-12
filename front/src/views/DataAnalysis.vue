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
      <li class="nav-item">
        <a 
          class="nav-link" 
          :class="{ active: activeTab === 'advanced' }"
          href="#"
          @click.prevent="activeTab = 'advanced'"
        >
          高级分析
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
                    <div class="mb-2">
                      <button 
                        type="button" 
                        class="btn btn-sm btn-outline-secondary"
                        @click="selectAllColumnsForHeatmap"
                      >
                        全选
                      </button>
                      <button 
                        type="button" 
                        class="btn btn-sm btn-outline-secondary ms-2"
                        @click="unselectAllColumnsForHeatmap"
                      >
                        取消全选
                      </button>
                    </div>
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
          <div class="card shadow-sm mb-4">
            <div class="card-header">
              <h5 class="mb-0">房价预测模型训练</h5>
            </div>
            <div class="card-body">
              <div v-if="predictionError" class="alert alert-danger">
                {{ predictionError }}
              </div>
              
              <form @submit.prevent="trainHousePriceModel">
                <div class="mb-3">
                  <label for="modelName" class="form-label">模型名称</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="modelName" 
                    v-model="housePriceForm.name"
                    placeholder="房价预测模型"
                    required
                  >
                </div>
                
                <p class="text-muted small mb-3">
                  当前选择的数据集 <strong>{{ dataset.name }}</strong> 将用于训练模型。
                  训练将自动选择目标变量(SalePrice)和相关特征。
                </p>
                
                <div class="d-grid">
                  <button 
                    type="submit" 
                    class="btn btn-primary"
                    :disabled="trainingHousePriceModel"
                  >
                    <span v-if="trainingHousePriceModel" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    {{ trainingHousePriceModel ? '训练中...' : '开始训练' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
          
          <div class="card shadow-sm" v-if="currentPrediction">
            <div class="card-header">
              <h5 class="mb-0">使用模型预测</h5>
            </div>
            <div class="card-body">
              <div v-if="predictionResultError" class="alert alert-danger">
                {{ predictionResultError }}
              </div>
              
              <form @submit.prevent="predictHousePrice">
                <div class="mb-3">
                  <label for="testFile" class="form-label">上传测试文件 (CSV)</label>
                  <div class="input-group">
                    <input 
                      type="file" 
                      class="form-control" 
                      id="testFile" 
                      accept=".csv"
                      ref="testFileInput"
                      @change="handleTestFileChange"
                      required
                    >
                  </div>
                  <div class="form-text">
                    上传不含SalePrice列的测试数据集CSV文件，其他列需与训练集一致
                  </div>
                </div>
                
                <div class="d-grid">
                  <button 
                    type="submit" 
                    class="btn btn-success"
                    :disabled="predictingHousePrice || !testFile"
                  >
                    <span v-if="predictingHousePrice" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    {{ predictingHousePrice ? '预测中...' : '开始预测' }}
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
                <h6>{{ currentPrediction.name }} (XGBoost 回归模型)</h6>
                
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
              </div>
              <div v-else class="py-5 text-center text-muted">
                <i class="bi bi-cpu display-1 mb-3"></i>
                <p>训练模型后在此处显示评估指标</p>
              </div>
            </div>
          </div>
          
          <!-- 预测结果 -->
          <div class="card shadow-sm mb-4" v-if="predictionResults">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">预测结果</h5>
              <span class="badge bg-primary">总计: {{ predictionResults.total_predictions }} 条预测</span>
            </div>
            <div class="card-body">
              <div class="mb-4">
                <h6>统计摘要</h6>
                <div class="row text-center">
                  <div class="col">
                    <div class="card bg-light">
                      <div class="card-body py-2">
                        <h5 class="mb-0">${{ formatLargeNumber(predictionResults.summary.mean) }}</h5>
                        <small class="text-muted">平均价格</small>
                      </div>
                    </div>
                  </div>
                  <div class="col">
                    <div class="card bg-light">
                      <div class="card-body py-2">
                        <h5 class="mb-0">${{ formatLargeNumber(predictionResults.summary.median) }}</h5>
                        <small class="text-muted">中位价格</small>
                      </div>
                    </div>
                  </div>
                  <div class="col">
                    <div class="card bg-light">
                      <div class="card-body py-2">
                        <h5 class="mb-0">${{ formatLargeNumber(predictionResults.summary.min) }}</h5>
                        <small class="text-muted">最低价格</small>
                      </div>
                    </div>
                  </div>
                  <div class="col">
                    <div class="card bg-light">
                      <div class="card-body py-2">
                        <h5 class="mb-0">${{ formatLargeNumber(predictionResults.summary.max) }}</h5>
                        <small class="text-muted">最高价格</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <h6>预测详情 (前100条)</h6>
              <div class="table-responsive">
                <table class="table table-sm table-striped">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>预测价格</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="result in predictionResults.predictions" :key="result.id">
                      <td>{{ result.id }}</td>
                      <td>${{ formatLargeNumber(result.predicted_price) }}</td>
                    </tr>
                  </tbody>
                </table>
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
                      <th>R²</th>
                      <th>RMSE</th>
                      <th>创建时间</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="prediction in predictions" :key="prediction.id">
                      <td>{{ prediction.name }}</td>
                      <td>{{ formatNumber(prediction.metrics.r2) }}</td>
                      <td>{{ formatNumber(prediction.metrics.rmse) }}</td>
                      <td>{{ formatDate(prediction.created_at) }}</td>
                      <td>
                        <button 
                          class="btn btn-sm btn-outline-primary"
                          @click="selectPrediction(prediction)"
                        >
                          选择模型
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
    
    <!-- 高级分析面板 -->
    <div v-if="activeTab === 'advanced'" class="advanced-analysis-panel">
      <div class="row">
        <div class="col-md-4">
          <div class="card shadow-sm">
            <div class="card-header">
              <h5 class="mb-0">高级数据分析</h5>
            </div>
            <div class="card-body">
              <div v-if="analysisError" class="alert alert-danger">
                {{ analysisError }}
              </div>
              
              <form @submit.prevent="performAdvancedAnalysis">
                <!-- 分析类型选择 -->
                <div class="mb-3">
                  <label class="form-label">分析类型</label>
                  <select 
                    class="form-select" 
                    v-model="advancedAnalysisForm.analysisType"
                    @change="onAnalysisTypeChange"
                    required
                  >
                    <option value="">选择分析类型</option>
                    <option value="clustering">聚类分析</option>
                    <option value="classification">分类分析</option>
                    <option value="dimensionality_reduction">降维分析</option>
                  </select>
                </div>
                
                <!-- 分析名称 -->
                <div class="mb-3" v-if="advancedAnalysisForm.analysisType">
                  <label for="analysisName" class="form-label">分析名称 (可选)</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="analysisName" 
                    v-model="advancedAnalysisForm.name"
                    placeholder="为此分析命名"
                  >
                </div>
                
                <!-- 算法选择 -->
                <div class="mb-3" v-if="advancedAnalysisForm.analysisType">
                  <label class="form-label">选择算法</label>
                  <select 
                    class="form-select" 
                    v-model="advancedAnalysisForm.algorithm"
                    @change="onAlgorithmChange"
                    required
                  >
                    <option value="">选择算法</option>
                    <option 
                      v-for="algo in availableAlgorithms" 
                      :key="algo.value" 
                      :value="algo.value"
                    >
                      {{ algo.label }}
                    </option>
                  </select>
                </div>
                
                <!-- 特征选择 -->
                <div class="mb-3" v-if="advancedAnalysisForm.algorithm">
                  <label class="form-label">特征变量</label>
                  <div class="mb-2">
                    <button 
                      type="button" 
                      class="btn btn-sm btn-outline-secondary"
                      @click="selectAllFeatures"
                    >
                      全选
                    </button>
                    <button 
                      type="button" 
                      class="btn btn-sm btn-outline-secondary ms-2"
                      @click="unselectAllFeatures"
                    >
                      取消全选
                    </button>
                  </div>
                  <div class="feature-selection-container">
                    <div 
                      v-for="col in columns" 
                      :key="col.name"
                      class="form-check"
                    >
                      <input 
                        class="form-check-input" 
                        type="checkbox" 
                        :id="`feature-adv-${col.name}`"
                        :value="col.name"
                        v-model="advancedAnalysisForm.featureColumns"
                        :disabled="advancedAnalysisForm.analysisType === 'classification' && advancedAnalysisForm.targetColumn === col.name"
                      >
                      <label class="form-check-label" :for="`feature-adv-${col.name}`">
                        {{ col.name }}
                      </label>
                    </div>
                  </div>
                  <div class="form-text" v-if="advancedAnalysisForm.featureColumns.length === 0">
                    请至少选择一个特征
                  </div>
                </div>
                
                <!-- 分类特有 - 目标变量选择 -->
                <div class="mb-3" v-if="advancedAnalysisForm.analysisType === 'classification'">
                  <label class="form-label">目标变量</label>
                  <select 
                    class="form-select" 
                    v-model="advancedAnalysisForm.targetColumn"
                    required
                  >
                    <option value="">选择目标列</option>
                    <option 
                      v-for="col in columns" 
                      :key="col.name" 
                      :value="col.name"
                      :disabled="advancedAnalysisForm.featureColumns.includes(col.name)"
                    >
                      {{ col.name }}
                    </option>
                  </select>
                </div>
                
                <!-- 算法参数配置 -->
                <div v-if="currentAlgorithmParams.length > 0" class="mb-4">
                  <h6 class="mb-3">算法参数配置</h6>
                  
                  <div 
                    v-for="param in currentAlgorithmParams" 
                    :key="param.name"
                    class="mb-3"
                  >
                    <label :for="`param-${param.name}`" class="form-label">{{ param.label }}</label>
                    
                    <!-- 数字类型参数 -->
                    <input 
                      v-if="param.type === 'number'" 
                      type="number" 
                      class="form-control" 
                      :id="`param-${param.name}`"
                      v-model.number="advancedAnalysisForm.algorithmParams[param.name]"
                      :min="param.min"
                      :max="param.max"
                      :step="param.step || 1"
                    >
                    
                    <!-- 选择类型参数 -->
                    <select 
                      v-else-if="param.type === 'select'" 
                      class="form-select" 
                      :id="`param-${param.name}`"
                      v-model="advancedAnalysisForm.algorithmParams[param.name]"
                    >
                      <option 
                        v-for="option in param.options" 
                        :key="option.value" 
                        :value="option.value"
                      >
                        {{ option.label }}
                      </option>
                    </select>
                    
                    <!-- 文本类型参数 -->
                    <input 
                      v-else-if="param.type === 'text'" 
                      type="text" 
                      class="form-control" 
                      :id="`param-${param.name}`"
                      v-model="advancedAnalysisForm.algorithmParams[param.name]"
                    >
                    
                    <!-- 布尔类型参数 -->
                    <div v-else-if="param.type === 'boolean'" class="form-check">
                      <input 
                        class="form-check-input" 
                        type="checkbox" 
                        :id="`param-${param.name}`"
                        v-model="advancedAnalysisForm.algorithmParams[param.name]"
                      >
                      <label class="form-check-label" :for="`param-${param.name}`">
                        启用
                      </label>
                    </div>
                  </div>
                </div>
                
                <div class="d-grid">
                  <button 
                    type="submit" 
                    class="btn btn-primary"
                    :disabled="performingAnalysis || !canPerformAnalysis"
                  >
                    <span v-if="performingAnalysis" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    {{ performingAnalysis ? '执行中...' : '执行分析' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
        
        <div class="col-md-8">
          <div class="card shadow-sm mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">分析结果</h5>
              <div v-if="currentAnalysisResult">
                <span class="badge bg-primary">{{ getAnalysisTypeLabel(currentAnalysisResult.type) }}</span>
                <span class="badge bg-secondary ms-2">{{ getAlgorithmLabel(currentAnalysisResult.algorithm, currentAnalysisResult.type) }}</span>
              </div>
            </div>
            <div class="card-body">
              <div v-if="currentAnalysisResult" class="mb-3">
                <!-- 聚类结果展示 -->
                <div v-if="currentAnalysisResult.type === 'clustering'">
                  <div class="alert alert-success">
                    <h6 class="mb-0">聚类完成</h6>
                  </div>
                  
                  <div class="row mt-4">
                    <div class="col-md-6">
                      <div class="card bg-light">
                        <div class="card-body text-center">
                          <h2 class="text-primary">{{ currentAnalysisResult.result.cluster_count }}</h2>
                          <p class="mb-0">簇的数量</p>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-6">
                      <div class="card bg-light">
                        <div class="card-body text-center">
                          <h2 class="text-primary">{{ currentAnalysisResult.result.total_samples }}</h2>
                          <p class="mb-0">样本总数</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="mt-4">
                    <h6>簇大小分布:</h6>
                    <div class="d-flex align-items-center mb-2" v-for="(size, index) in currentAnalysisResult.result.cluster_sizes" :key="index">
                      <span class="me-2">簇 {{ index }}:</span>
                      <div class="progress flex-grow-1">
                        <div 
                          class="progress-bar" 
                          :style="{width: `${(size / currentAnalysisResult.result.total_samples) * 100}%`}"
                        >
                          {{ size }}
                        </div>
                      </div>
                    </div>
                    
                    <div v-if="currentAnalysisResult.result.outliers_count > 0" class="mt-3">
                      <span class="badge bg-warning">发现 {{ currentAnalysisResult.result.outliers_count }} 个异常点</span>
                    </div>
                  </div>
                </div>
                
                <!-- 分类结果展示 -->
                <div v-else-if="currentAnalysisResult.type === 'classification'">
                  <div class="alert alert-success">
                    <h6 class="mb-0">分类模型训练完成</h6>
                  </div>
                  
                  <div class="row text-center mt-4">
                    <div class="col-md-4">
                      <div class="card bg-light">
                        <div class="card-body">
                          <h2 class="text-primary">{{ (currentAnalysisResult.result.metrics.accuracy * 100).toFixed(2) }}%</h2>
                          <p class="mb-0">准确率 (Accuracy)</p>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-4" v-if="currentAnalysisResult.result.metrics.precision !== undefined">
                      <div class="card bg-light">
                        <div class="card-body">
                          <h2 class="text-primary">{{ (currentAnalysisResult.result.metrics.precision * 100).toFixed(2) }}%</h2>
                          <p class="mb-0">精确率 (Precision)</p>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-4" v-if="currentAnalysisResult.result.metrics.recall !== undefined">
                      <div class="card bg-light">
                        <div class="card-body">
                          <h2 class="text-primary">{{ (currentAnalysisResult.result.metrics.recall * 100).toFixed(2) }}%</h2>
                          <p class="mb-0">召回率 (Recall)</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="mt-4 text-center">
                    <p>在 {{ currentAnalysisResult.result.metrics.samples }} 个测试样本上评估</p>
                  </div>
                </div>
                
                <!-- 降维结果展示 -->
                <div v-else-if="currentAnalysisResult.type === 'dimensionality_reduction'">
                  <div class="alert alert-success">
                    <h6 class="mb-0">降维完成</h6>
                  </div>
                  
                  <div class="row mt-4">
                    <div class="col-md-12 text-center">
                      <p>降维后数据 (前1000个点的2D投影)</p>
                      <!-- 使用echarts展示散点图 -->
                      <div ref="dimensionReductionChart" style="height: 400px; width: 100%; border-radius: 8px;"></div>
                    </div>
                  </div>
                  
                  <div class="mt-4" v-if="currentAnalysisResult.result.explained_variance">
                    <h6>解释方差比例:</h6>
                    <div class="progress mb-2">
                      <div 
                        class="progress-bar" 
                        :style="{width: `${currentAnalysisResult.result.explained_variance[0] * 100}%`}"
                      >
                        {{ (currentAnalysisResult.result.explained_variance[0] * 100).toFixed(2) }}%
                      </div>
                    </div>
                    <p class="small text-muted">第一主成分解释方差比例</p>
                  </div>
                </div>
              </div>
              <div v-else class="py-5 text-center text-muted">
                <i class="bi bi-graph-up display-1 mb-3"></i>
                <p>执行分析后在此处显示结果</p>
              </div>
            </div>
          </div>
          
          <div class="card shadow-sm">
            <div class="card-header">
              <h5 class="mb-0">分析历史</h5>
            </div>
            <div class="card-body">
              <div v-if="analysisHistory.length === 0" class="text-center py-3 text-muted">
                暂无分析历史
              </div>
              
              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>名称</th>
                      <th>分析类型</th>
                      <th>算法</th>
                      <th>时间</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(analysis, index) in analysisHistory" :key="index">
                      <td>{{ analysis.name }}</td>
                      <td>{{ getAnalysisTypeLabel(analysis.type) }}</td>
                      <td>{{ getAlgorithmLabel(analysis.algorithm, analysis.type) }}</td>
                      <td>{{ new Date(analysis.timestamp).toLocaleString() }}</td>
                      <td>
                        <button 
                          class="btn btn-sm btn-outline-primary"
                          @click="currentAnalysisResult = analysis"
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
import axios from 'axios';
import * as echarts from 'echarts';

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
      housePriceForm: {
        name: '',
        testFile: null
      },
      trainingHousePriceModel: false,
      predictingHousePrice: false,
      predictionError: null,
      predictionResultError: null,
      currentPrediction: null,
      predictionResults: null,
      testFile: null,
      predictions: [],
      loadingPredictions: false,
      
      // 高级分析相关
      advancedAnalysisForm: {
        analysisType: '', // 'clustering', 'classification', 'dimensionality_reduction'
        name: '',
        algorithm: '',
        featureColumns: [],
        targetColumn: '', // 仅用于分类
        testSize: 0.2, // 仅用于分类
        algorithmParams: {}, // 动态参数
      },
      performingAnalysis: false,
      analysisError: null,
      currentAnalysisResult: null,
      analysisHistory: [],
      algorithmConfig: {
        // 聚类算法配置
        clustering: {
          algorithms: [
            { value: 'kmeans', label: 'K均值聚类 (K-Means)' },
            { value: 'dbscan', label: '密度聚类 (DBSCAN)' },
            { value: 'hierarchical', label: '层次聚类 (Hierarchical)' }
          ],
          // 各算法的参数配置
          kmeans: [
            { name: 'n_clusters', label: '簇的数量', type: 'number', defaultValue: 3, min: 2, max: 20 },
            { name: 'init', label: '初始化方法', type: 'select', defaultValue: 'k-means++', 
              options: [
                { value: 'k-means++', label: 'k-means++' },
                { value: 'random', label: '随机' }
              ]
            },
            { name: 'n_init', label: '运行次数', type: 'number', defaultValue: 10, min: 1, max: 50 },
            { name: 'max_iter', label: '最大迭代次数', type: 'number', defaultValue: 300, min: 50, max: 1000 }
          ],
          dbscan: [
            { name: 'eps', label: '邻域半径', type: 'number', defaultValue: 0.5, min: 0.01, max: 10, step: 0.01 },
            { name: 'min_samples', label: '核心点最小样本数', type: 'number', defaultValue: 5, min: 2, max: 50 }
          ],
          hierarchical: [
            { name: 'n_clusters', label: '簇的数量', type: 'number', defaultValue: 3, min: 2, max: 20 },
            { name: 'linkage', label: '连接方式', type: 'select', defaultValue: 'ward',
              options: [
                { value: 'ward', label: 'Ward' },
                { value: 'complete', label: '完全连接' },
                { value: 'average', label: '平均连接' },
                { value: 'single', label: '单连接' }
              ]
            }
          ]
        },
        // 分类算法配置
        classification: {
          algorithms: [
            { value: 'logistic_regression', label: '逻辑回归 (Logistic Regression)' },
            { value: 'random_forest', label: '随机森林 (Random Forest)' },
            { value: 'svm', label: '支持向量机 (SVM)' }
          ],
          logistic_regression: [
            { name: 'penalty', label: '正则化', type: 'select', defaultValue: 'l2',
              options: [
                { value: 'l1', label: 'L1正则化' },
                { value: 'l2', label: 'L2正则化' },
                { value: 'none', label: '无正则化' }
              ]
            },
            { name: 'C', label: '正则化强度倒数', type: 'number', defaultValue: 1.0, min: 0.1, max: 10, step: 0.1 },
            { name: 'solver', label: '求解器', type: 'select', defaultValue: 'liblinear',
              options: [
                { value: 'liblinear', label: 'liblinear' },
                { value: 'saga', label: 'saga' },
                { value: 'lbfgs', label: 'lbfgs' }
              ]
            },
            { name: 'max_iter', label: '最大迭代次数', type: 'number', defaultValue: 100, min: 50, max: 1000 }
          ],
          random_forest: [
            { name: 'n_estimators', label: '树的数量', type: 'number', defaultValue: 100, min: 10, max: 500 },
            { name: 'max_depth', label: '最大深度', type: 'number', defaultValue: 10, min: 1, max: 50 },
            { name: 'min_samples_split', label: '内部节点再划分所需最小样本数', type: 'number', defaultValue: 2, min: 2, max: 20 }
          ],
          svm: [
            { name: 'C', label: '惩罚参数', type: 'number', defaultValue: 1.0, min: 0.1, max: 10, step: 0.1 },
            { name: 'kernel', label: '核函数', type: 'select', defaultValue: 'rbf',
              options: [
                { value: 'linear', label: '线性核' },
                { value: 'poly', label: '多项式核' },
                { value: 'rbf', label: 'RBF核' },
                { value: 'sigmoid', label: 'Sigmoid核' }
              ]
            },
            { name: 'gamma', label: 'gamma参数', type: 'select', defaultValue: 'scale',
              options: [
                { value: 'scale', label: '自动缩放' },
                { value: 'auto', label: '自动' }
              ]
            }
          ]
        },
        // 降维算法配置
        dimensionality_reduction: {
          algorithms: [
            { value: 'pca', label: '主成分分析 (PCA)' },
            { value: 'tsne', label: 't-SNE' }
          ],
          pca: [
            { name: 'n_components', label: '主成分数量', type: 'number', defaultValue: 2, min: 1, max: 20 },
            { name: 'svd_solver', label: 'SVD求解器', type: 'select', defaultValue: 'auto',
              options: [
                { value: 'auto', label: '自动' },
                { value: 'full', label: '全SVD' },
                { value: 'arpack', label: 'ARPACK' },
                { value: 'randomized', label: '随机化SVD' }
              ]
            }
          ],
          tsne: [
            { name: 'n_components', label: '输出维度', type: 'number', defaultValue: 2, min: 1, max: 3 },
            { name: 'perplexity', label: '困惑度', type: 'number', defaultValue: 30, min: 5, max: 100 },
            { name: 'n_iter', label: '迭代次数', type: 'number', defaultValue: 1000, min: 250, max: 5000 }
          ]
        }
      }
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
      const { algorithm, target, features } = this.housePriceForm
      return !!algorithm && !!target && features.length > 0
    },
    // 高级分析相关计算属性
    currentAnalysisType() {
      return this.advancedAnalysisForm.analysisType;
    },
    currentAlgorithm() {
      return this.advancedAnalysisForm.algorithm;
    },
    availableAlgorithms() {
      const type = this.currentAnalysisType;
      if (!type || !this.algorithmConfig[type]) return [];
      return this.algorithmConfig[type].algorithms || [];
    },
    currentAlgorithmParams() {
      const type = this.currentAnalysisType;
      const algorithm = this.currentAlgorithm;
      
      if (!type || !algorithm || !this.algorithmConfig[type][algorithm]) {
        return [];
      }
      
      return this.algorithmConfig[type][algorithm];
    },
    canPerformAnalysis() {
      const form = this.advancedAnalysisForm;
      
      if (!form.analysisType || !form.algorithm || form.featureColumns.length === 0) {
        return false;
      }
      
      // 分类需要额外检查目标列
      if (form.analysisType === 'classification' && !form.targetColumn) {
        return false;
      }
      
      return true;
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
    'housePriceForm.target'(newValue) {
      // 当目标变量改变时，移除特征列表中的目标变量
      if (newValue && this.housePriceForm.features.includes(newValue)) {
        this.housePriceForm.features = this.housePriceForm.features.filter(f => f !== newValue)
      }
    },
    // 高级分析相关watcher
    'advancedAnalysisForm.targetColumn'(newValue) {
      // 当分类目标变量改变时，移除特征列表中的目标变量
      if (newValue && this.advancedAnalysisForm.featureColumns.includes(newValue)) {
        this.advancedAnalysisForm.featureColumns = this.advancedAnalysisForm.featureColumns.filter(f => f !== newValue)
      }
    },
    // 监听当前分析结果变化
    currentAnalysisResult: {
      handler(newVal) {
        if (newVal && newVal.type === 'dimensionality_reduction') {
          // 使用nextTick确保DOM已更新
          this.$nextTick(() => {
            this.createDimensionReductionChart();
          });
        }
      },
      deep: true
    }
  },
  created() {
    // 全局错误处理器
    this.errorHandler = (error) => {
      if (error.response && error.response.status === 404) {
        this.handleNotFoundError(error);
        return true; // 表示已处理
      }
      return false; // 未处理，交给默认处理器
    };
    
    // 注册全局错误处理器
    this.$root.$on('error', this.errorHandler);
  },
  beforeUnmount() {
    // 移除全局错误处理器
    this.$root.$off('error', this.errorHandler);
  },
  methods: {
    async fetchDataset() {
      this.loading = true
      
      try {
        const result = await this.$store.dispatch('fetchDataset', this.datasetId)
        
        if (result && result.success) {
          // 确保dataset和columns都存在
          if (this.dataset && this.dataset.columns) {
            try {
              
              this.columns = this.dataset.columns
            } catch (e) {
              console.error('解析列数据失败:', e)
              this.columns = []
            }
          } else {
            console.warn('数据集或列信息不存在')
            this.columns = []
          }
          
          // 如果是预测标签，加载历史预测
          if (this.activeTab === 'prediction') {
            this.fetchPredictions()
          }
        } else {
          console.warn('获取数据集返回错误:', result?.error || '未知错误')
          this.columns = []
        }
      } catch (err) {
        console.error('获取数据集失败', err)
        this.columns = []
        
        // 处理404错误
        if (err.response && err.response.status === 404) {
          alert('数据集不存在或已被删除')
          this.$router.push('/dashboard')
        }
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
          // 处理图像URL
          let imageUrl = result.imageUrl;
          
          // 如果是相对路径，转换成绝对路径
          if (imageUrl && imageUrl.startsWith('/')) {
            // 使用完整的基础URL
            imageUrl = `${window.location.origin}${imageUrl}`;
          }
          
          this.currentVisualization = {
            name: this.visualizationForm.name,
            chartType: this.visualizationForm.chartType,
            imageUrl: imageUrl
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
        
        if (result && result.success) {
          this.predictions = result.predictions || []
          
          // 如果有预测记录，默认选择第一个
          if (this.predictions.length > 0) {
            this.selectPrediction(this.predictions[0])
          }
        } else {
          // 增加错误处理
          console.warn('获取预测记录返回非成功状态:', result)
          this.predictions = []
        }
      } catch (err) {
        console.error('获取预测记录失败', err)
        this.predictions = [] // 确保失败时也设置为空数组
      } finally {
        this.loadingPredictions = false
      }
    },
    
    async trainHousePriceModel() {
      this.trainingHousePriceModel = true;
      this.predictionError = null;
      
      try {
        const response = await axios.post(`/analysis/train_price_model`, {
          dataset_id: this.datasetId,
          model_name: this.housePriceForm.name || '房价预测模型'
        });
        
        if (response.data.success) {
          // 训练成功，重新加载模型列表
          await this.fetchPredictions();
          
          // 选择新训练的模型
          const newPredictionId = response.data.prediction_id;
          const newPrediction = this.predictions.find(p => p.id === newPredictionId);
          if (newPrediction) {
            this.selectPrediction(newPrediction);
          }
          
          // 重置表单
          this.housePriceForm.name = '';
        } else {
          this.predictionError = response.data.error || '训练模型失败';
        }
      } catch (error) {
        console.error('训练房价预测模型失败:', error);
        this.predictionError = error.response?.data?.error || '训练模型失败，请检查网络连接';
      } finally {
        this.trainingHousePriceModel = false;
      }
    },
    
    selectPrediction(prediction) {
      this.currentPrediction = prediction
    },
    
    getAlgorithmLabel(algorithm, type) {
      // 预测模型算法映射
      const algorithmMap = {
        'linear_regression': '线性回归',
        'random_forest': '随机森林'
      };
      
      // 如果没有指定类型或是预测类型，使用简单映射
      if (!type || type === 'prediction') {
        return algorithmMap[algorithm] || algorithm;
      }
      
      // 高级分析算法标签获取
      const algorithmList = this.algorithmConfig[type]?.algorithms || [];
      const found = algorithmList.find(item => item.value === algorithm);
      return found ? found.label : algorithm;
    },
    
    formatNumber(value) {
      if (typeof value !== 'number') return value
      
      // 显示3位小数
      return value.toFixed(3)
    },
    
    handleNotFoundError(error) {
      console.warn('API端点未找到:', error.config.url);
      
      if (error.config.url.includes('/predictions')) {
        // 预测API不存在时的处理
        this.loadingPredictions = false;
        this.predictions = [];
        // 可选：显示友好提示
        this.predictionError = "预测功能暂不可用，请稍后再试";
      }
    },
    
    // 高级分析相关方法
    resetAnalysisParams() {
      this.advancedAnalysisForm.algorithmParams = {};
      
      // 为当前选择的算法设置默认参数
      if (this.currentAlgorithmParams.length > 0) {
        const defaultParams = {};
        this.currentAlgorithmParams.forEach(param => {
          defaultParams[param.name] = param.defaultValue;
        });
        this.advancedAnalysisForm.algorithmParams = defaultParams;
      }
    },
    
    onAnalysisTypeChange() {
      this.advancedAnalysisForm.algorithm = '';
      this.advancedAnalysisForm.algorithmParams = {};
      this.advancedAnalysisForm.featureColumns = [];
      
      if (this.currentAnalysisType === 'classification') {
        this.advancedAnalysisForm.targetColumn = '';
      }
    },
    
    onAlgorithmChange() {
      this.resetAnalysisParams();
    },
    
    async performAdvancedAnalysis() {
      if (!this.canPerformAnalysis) return;
      
      this.performingAnalysis = true;
      this.analysisError = null;
      
      try {
        const analysisType = this.advancedAnalysisForm.analysisType;
        const algorithm = this.advancedAnalysisForm.algorithm;
        const featureColumns = this.advancedAnalysisForm.featureColumns;
        
        // 构建API请求参数
        const apiParams = {
          dataset_id: this.datasetId,
          feature_columns: featureColumns,
          algorithm_config: {
            algorithm: algorithm,
            params: this.advancedAnalysisForm.algorithmParams
          }
        };
        
        // 分类特有参数
        if (analysisType === 'classification') {
          apiParams.target_column = this.advancedAnalysisForm.targetColumn;
          apiParams.test_size = this.advancedAnalysisForm.testSize;
        }
        
        // 根据分析类型选择API端点
        let endpoint;
        if (analysisType === 'clustering') {
          endpoint = '/analysis/perform_clustering';
        } else if (analysisType === 'classification') {
          endpoint = '/analysis/perform_classification';
        } else if (analysisType === 'dimensionality_reduction') {
          endpoint = '/analysis/perform_dimensionality_reduction';
        } else {
          throw new Error('未知的分析类型');
        }
        
        // 使用axios替代this.$http
        const response = await axios.post(endpoint, apiParams);
        
        if (response.data && response.data.success) {
          // 保存结果
          this.currentAnalysisResult = {
            type: analysisType,
            algorithm: algorithm,
            result: response.data,
            timestamp: new Date().toISOString()
          };
          
          // 添加到历史记录
          this.analysisHistory.unshift({
            ...this.currentAnalysisResult,
            name: this.advancedAnalysisForm.name || `${this.getAnalysisTypeLabel(analysisType)} - ${this.getAlgorithmLabel(algorithm, analysisType)}`
          });
          
          // 重置表单名称
          this.advancedAnalysisForm.name = '';
        } else {
          this.analysisError = response.data.error || '分析执行失败';
        }
      } catch (err) {
        console.error('高级分析执行失败', err);
        this.analysisError = err.response?.data?.error || '执行分析时出错';
      } finally {
        this.performingAnalysis = false;
      }
    },
    
    getAnalysisTypeLabel(type) {
      const typeMap = {
        'clustering': '聚类分析',
        'classification': '分类分析',
        'dimensionality_reduction': '降维分析'
      };
      return typeMap[type] || type;
    },
    
    // 创建降维结果可视化图表
    createDimensionReductionChart() {
      if (!this.currentAnalysisResult || 
          this.currentAnalysisResult.type !== 'dimensionality_reduction' || 
          !this.currentAnalysisResult.result.data_2d) {
        return;
      }
      
      // 确保dom元素存在
      if (!this.$refs.dimensionReductionChart) {
        return;
      }
      
      // 初始化图表
      const chartDom = this.$refs.dimensionReductionChart;
      const chart = echarts.init(chartDom);
      
      // 准备数据
      const data = this.currentAnalysisResult.result.data_2d;
      
      // 设置图表选项
      const option = {
        title: {
          text: '降维结果可视化',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            return `点 ${params.dataIndex}`;
          }
        },
        grid: {
          left: '5%',
          right: '5%',
          top: '10%',
          bottom: '10%',
          containLabel: true
        },
        xAxis: {
          name: '维度1',
          type: 'value',
          scale: true
        },
        yAxis: {
          name: '维度2',
          type: 'value',
          scale: true
        },
        series: [
          {
            name: '降维点',
            type: 'scatter',
            data: data,
            symbolSize: 5,
            itemStyle: {
              color: function(params) {
                // 生成随机颜色
                const colorList = [
                  '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
                  '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'
                ];
                
                // 根据数据的第一维度进行简单的分组
                if (data.length > 0) {
                  const firstDimMin = Math.min(...data.map(item => item[0]));
                  const firstDimMax = Math.max(...data.map(item => item[0]));
                  const range = firstDimMax - firstDimMin;
                  
                  if (range > 0) {
                    const value = data[params.dataIndex][0];
                    const index = Math.floor(((value - firstDimMin) / range) * colorList.length);
                    return colorList[Math.min(index, colorList.length - 1)];
                  }
                }
                
                return colorList[0];
              }
            }
          }
        ]
      };
      
      // 设置图表
      chart.setOption(option);
      
      // 响应窗口大小变化
      window.addEventListener('resize', () => {
        chart.resize();
      });
      
      // 保存图表实例供后续使用
      this.dimensionReductionChart = chart;
    },
    
    // 格式化大数字为千分位表示
    formatLargeNumber(value) {
      if (value === null || value === undefined) return '-';
      return new Intl.NumberFormat('en-US').format(Math.round(value));
    },
    
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return '-';
      const date = new Date(dateString);
      return date.toLocaleDateString('zh-CN');
    },
    
    // 使用当前模型进行房价预测
    async predictHousePrice() {
      if (!this.currentPrediction || !this.testFile) {
        this.predictionResultError = '请先选择模型和测试文件';
        return;
      }
      
      this.predictingHousePrice = true;
      this.predictionResultError = null;
      this.predictionResults = null;
      
      try {
        const formData = new FormData();
        formData.append('file', this.testFile);
        formData.append('prediction_id', this.currentPrediction.id);
        
        const response = await axios.post('/analysis/predict_house_price', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        if (response.data.success) {
          this.predictionResults = response.data;
        } else {
          this.predictionResultError = response.data.error || '预测失败';
        }
      } catch (error) {
        console.error('房价预测失败:', error);
        this.predictionResultError = error.response?.data?.error || '预测失败，请检查网络连接';
      } finally {
        this.predictingHousePrice = false;
      }
    },
    
    // 处理测试文件选择
    handleTestFileChange(event) {
      const files = event.target.files;
      if (files && files.length > 0) {
        this.testFile = files[0];
        console.log('已选择测试文件:', this.testFile.name);
      } else {
        this.testFile = null;
      }
    },
    
    // 全选特征
    selectAllFeatures() {
      this.advancedAnalysisForm.featureColumns = this.columns.map(col => col.name);
    },
    
    // 取消全选特征
    unselectAllFeatures() {
      this.advancedAnalysisForm.featureColumns = [];
    },
    
    // 全选热力图的列
    selectAllColumnsForHeatmap() {
      this.visualizationForm.config.columns = this.numericColumns.map(col => col.name);
    },
    
    // 取消全选热力图的列
    unselectAllColumnsForHeatmap() {
      this.visualizationForm.config.columns = [];
    },
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

.feature-selection-container {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
}
</style> 