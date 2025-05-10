<template>
  <div v-if="loading" class="text-center py-5">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">加载中...</span>
    </div>
  </div>
  
  <div v-else-if="dataset" class="dataset-detail">
    <div class="d-flex justify-content-between align-items-start mb-4">
      <div>
        <h2>{{ dataset.name }}</h2>
        <p class="text-muted">{{ dataset.description || '没有描述' }}</p>
      </div>
      <div>
        <router-link 
          :to="`/analysis/${dataset.id}`" 
          class="btn btn-primary me-2"
        >
          分析与预测
        </router-link>
        <button 
          v-if="!dataset.cleaned"
          class="btn btn-outline-success"
          @click="showCleanOptions = true"
        >
          数据清洗
        </button>
      </div>
    </div>
    
    <div class="row mb-4">
      <div class="col-md-3 mb-3">
        <div class="card">
          <div class="card-body text-center">
            <h5>{{ dataset.row_count }}</h5>
            <p class="card-text text-muted">行数</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card">
          <div class="card-body text-center">
            <h5>{{ columns.length }}</h5>
            <p class="card-text text-muted">列数</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card">
          <div class="card-body text-center">
            <h5>{{ dataset.file_type.toUpperCase() }}</h5>
            <p class="card-text text-muted">文件类型</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card">
          <div class="card-body text-center">
            <h5>{{ dataset.cleaned ? '已清洗' : '未清洗' }}</h5>
            <p class="card-text text-muted">状态</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 数据清洗选项 -->
    <div v-if="showCleanOptions" class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">数据清洗选项</h5>
        <button 
          type="button" 
          class="btn-close" 
          @click="showCleanOptions = false"
        ></button>
      </div>
      <div class="card-body">
        <div v-if="cleaningError" class="alert alert-danger">
          {{ cleaningError }}
        </div>
        
        <!-- 添加自动清洗建议按钮 -->
        <div class="mb-3 d-grid">
          <button 
            class="btn btn-outline-info mb-3" 
            @click="getCleaningSuggestions"
            :disabled="gettingSuggestions"
          >
            {{ gettingSuggestions ? '正在分析数据...' : '自动分析并提供清洗建议' }}
          </button>
        </div>
        
        <!-- 清洗建议列表 -->
        <div v-if="cleaningSuggestions.length > 0" class="mb-4">
          <h6 class="mb-3">清洗建议</h6>
          <div class="list-group">
            <div 
              v-for="(suggestion, index) in cleaningSuggestions" 
              :key="index"
              class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
            >
              <div>
                <div class="d-flex align-items-center">
                  <span 
                    class="badge rounded-pill me-2"
                    :class="{
                      'bg-danger': suggestion.priority === 'high',
                      'bg-warning': suggestion.priority === 'medium',
                      'bg-info': suggestion.priority === 'low'
                    }"
                  >
                    {{ getPriorityLabel(suggestion.priority) }}
                  </span>
                  <span>{{ getOperationLabel(suggestion) }}</span>
                </div>
                <small class="text-muted d-block mt-1">{{ suggestion.reason }}</small>
              </div>
              <button 
                class="btn btn-sm btn-outline-primary"
                @click="applyCleaningSuggestion(suggestion)"
              >
                应用
              </button>
            </div>
          </div>
          
          <div class="d-grid mt-3">
            <button 
              class="btn btn-success btn-sm"
              @click="applyAllSuggestions"
            >
              一键应用所有建议
            </button>
          </div>
        </div>
        
        <div class="mb-3">
          <h6>清洗操作</h6>
          <div class="mb-2" v-for="(op, index) in cleaningOperations" :key="index">
            <div class="card">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <span>{{ getOperationLabel(op) }}</span>
                  </div>
                  <button 
                    class="btn btn-sm btn-outline-danger"
                    @click="removeOperation(index)"
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="cleaningOperations.length === 0" class="text-center py-3">
            <p class="text-muted">未添加清洗操作</p>
          </div>
        </div>
        
        <hr>
        
        <div>
          <h6>添加清洗操作</h6>
          <div class="row mb-3">
            <div class="col-md-4">
              <select class="form-select" v-model="newOperation.type">
                <option value="">选择操作类型</option>
                <option value="drop_column">删除列</option>
                <option value="fill_na">填充缺失值</option>
                <option value="drop_na">删除含缺失值的行</option>
                <option value="remove_outliers">移除异常值</option>
                <option value="categorical_encoding">类别编码</option>
              </select>
            </div>
            
            <div class="col-md-4" v-if="newOperation.type">
              <select class="form-select" v-model="newOperation.column">
                <option value="">选择列</option>
                <option 
                  v-for="col in columns" 
                  :key="col.name" 
                  :value="col.name"
                >
                  {{ col.name }} ({{ col.type }})
                </option>
              </select>
            </div>
            
            <div class="col-md-4" v-if="newOperation.type === 'fill_na'">
              <select class="form-select" v-model="newOperation.method">
                <option value="mean">均值填充</option>
                <option value="median">中位数填充</option>
                <option value="mode">众数填充</option>
                <option value="value">指定值填充</option>
              </select>
            </div>
            
            <div class="col-md-4" v-if="newOperation.type === 'fill_na' && newOperation.method === 'value'">
              <input 
                type="text" 
                class="form-control" 
                placeholder="填充值" 
                v-model="newOperation.value"
              >
            </div>
            
            <div class="col-md-4" v-if="newOperation.type === 'categorical_encoding'">
              <select class="form-select" v-model="newOperation.method">
                <option value="one_hot">独热编码</option>
                <option value="label">标签编码</option>
              </select>
            </div>
          </div>
          
          <div class="d-grid">
            <button 
              class="btn btn-sm btn-outline-primary" 
              @click="addOperation"
              :disabled="!canAddOperation"
            >
              添加操作
            </button>
          </div>
        </div>
        
        <div class="d-flex justify-content-end mt-4">
          <button 
            class="btn btn-primary" 
            @click="cleanData"
            :disabled="cleaning || cleaningOperations.length === 0"
          >
            {{ cleaning ? '清洗中...' : '开始清洗' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 数据预览 -->
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">数据预览</h5>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-striped table-sm">
            <thead>
              <tr>
                <th v-for="col in columns" :key="col.name">
                  {{ col.name }}
                  <span class="badge bg-secondary ms-1">{{ col.type }}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in preview" :key="index">
                <td v-for="col in columns" :key="col.name">
                  {{ row[col.name] }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- 在数据清洗后添加结果统计面板 -->
    <div v-if="cleaningResult" class="card mb-4">
      <div class="card-header">
        <h5 class="mb-0">数据清洗结果</h5>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-4">
            <div class="card">
              <div class="card-body text-center">
                <h5>{{ cleaningResult.original_count }}</h5>
                <p class="card-text text-muted">原始行数</p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card">
              <div class="card-body text-center">
                <h5>{{ cleaningResult.cleaned_count }}</h5>
                <p class="card-text text-muted">清洗后行数</p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card">
              <div class="card-body text-center">
                <h5>{{ cleaningResult.removed_count }}</h5>
                <p class="card-text text-muted">移除的行数</p>
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
  name: 'DatasetDetail',
  data() {
    return {
      loading: true,
      preview: [],
      columns: [],
      showCleanOptions: false,
      cleaningOperations: [],
      newOperation: {
        type: '',
        column: '',
        method: '',
        value: ''
      },
      cleaning: false,
      cleaningError: null,
      cleaningSuggestions: [],
      gettingSuggestions: false,
      cleaningResult: null,
    }
  },
  computed: {
    dataset() {
      return this.$store.getters.currentDataset
    },
    datasetId() {
      return Number(this.$route.params.id)
    },
    canAddOperation() {
      const { type, column } = this.newOperation
      
      if (!type || !column) {
        return false
      }
      
      if (type === 'fill_na') {
        if (this.newOperation.method === 'value' && !this.newOperation.value) {
          return false
        }
        return !!this.newOperation.method
      }
      
      if (type === 'categorical_encoding') {
        return !!this.newOperation.method
      }
      
      return true
    }
  },
  mounted() {
    this.fetchDataset()
  },
  methods: {
    async fetchDataset() {
      this.loading = true
      
      try {
        const result = await this.$store.dispatch('fetchDataset', this.datasetId)
        
        if (result.success) {
          this.preview = result.preview
          this.columns = JSON.parse(this.dataset.columns)
        }
      } catch (err) {
        console.error('获取数据集失败', err)
      } finally {
        this.loading = false
      }
    },
    
    getOperationLabel(op) {
      switch (op.type) {
        case 'drop_column':
          return `删除列 "${op.column}"`
        case 'fill_na':
          if (op.method === 'value') {
            return `填充列 "${op.column}" 的缺失值为 "${op.value}"`
          }
          const methodMap = {
            mean: '均值',
            median: '中位数',
            mode: '众数'
          }
          return `用${methodMap[op.method]}填充列 "${op.column}" 的缺失值`
        case 'drop_na':
          return `删除列 "${op.column}" 中含缺失值的行`
        case 'remove_outliers':
          return `移除列 "${op.column}" 中的异常值`
        case 'categorical_encoding':
          const encodeMap = {
            one_hot: '独热编码',
            label: '标签编码'
          }
          return `对列 "${op.column}" 进行${encodeMap[op.method]}`
        default:
          return '未知操作'
      }
    },
    
    addOperation() {
      if (!this.canAddOperation) {
        return
      }
      
      this.cleaningOperations.push({ ...this.newOperation })
      
      // 重置新操作
      this.newOperation = {
        type: '',
        column: '',
        method: '',
        value: ''
      }
    },
    
    removeOperation(index) {
      this.cleaningOperations.splice(index, 1)
    },
    
    async cleanData() {
      if (this.cleaningOperations.length === 0) {
        return
      }
      
      this.cleaning = true
      this.cleaningError = null
      
      try {
        const result = await this.$store.dispatch('cleanDataset', {
          datasetId: this.datasetId,
          operations: this.cleaningOperations
        })
        
        if (result.success) {
          // 更新预览数据
          this.preview = result.preview
          
          // 保存清洗结果
          this.cleaningResult = {
            original_count: result.original_count,
            cleaned_count: result.cleaned_count,
            removed_count: result.removed_count
          }
          
          // 隐藏清洗选项
          this.showCleanOptions = false
          
          // 重新获取数据集信息
          await this.fetchDataset()
        } else {
          this.cleaningError = result.error
        }
      } catch (err) {
        this.cleaningError = '数据清洗失败'
        console.error(err)
      } finally {
        this.cleaning = false
      }
    },
    
    async getCleaningSuggestions() {
      this.gettingSuggestions = true
      this.cleaningSuggestions = []
      
      try {
        const response = await fetch(`/api/data/datasets/${this.datasetId}/suggest`)
        const data = await response.json()
        
        if (data.success) {
          this.cleaningSuggestions = data.suggestions
        } else {
          this.cleaningError = data.error || '获取清洗建议失败'
        }
      } catch (err) {
        console.error('获取清洗建议时出错', err)
        this.cleaningError = '获取清洗建议失败'
      } finally {
        this.gettingSuggestions = false
      }
    },
    
    getPriorityLabel(priority) {
      switch(priority) {
        case 'high': return '高优先级'
        case 'medium': return '中优先级'
        case 'low': return '低优先级'
        default: return '建议'
      }
    },
    
    applyCleaningSuggestion(suggestion) {
      // 将建议添加到清洗操作列表
      this.cleaningOperations.push({ ...suggestion })
    },
    
    applyAllSuggestions() {
      // 按优先级排序建议
      const sortedSuggestions = [...this.cleaningSuggestions].sort((a, b) => {
        const priorityOrder = { high: 0, medium: 1, low: 2 };
        return priorityOrder[a.priority] - priorityOrder[b.priority];
      });
      
      // 添加所有建议到操作列表
      sortedSuggestions.forEach(suggestion => {
        this.cleaningOperations.push({ ...suggestion });
      });
      
      // 通知用户
      alert(`已添加 ${sortedSuggestions.length} 个清洗操作！您可以检查并修改这些操作，然后点击"开始清洗"按钮执行。`);
    },
  }
}
</script> 