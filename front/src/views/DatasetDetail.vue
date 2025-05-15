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
          :to="`/analysis/${datasetId}`" 
          class="btn btn-primary me-2"
        >
          分析与预测
        </router-link>
        <router-link 
          :to="`/data-visualization/${datasetId}`"  
          class="btn btn-info me-2"
        >
          数据可视化
        </router-link>
        <button 
          v-if="!cleaned"
          class="btn btn-outline-success"
          @click="showCleanOptions = true"
        >
          数据清洗
        </button>
      </div>
    </div>
    
    <!-- 数据清洗面板 -->
    <div v-if="showCleanOptions" class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">数据清洗</h5>
        <button class="btn-close" @click="showCleanOptions = false"></button>
      </div>
      <div class="card-body">
        <div v-if="cleaning" class="text-center py-3">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">清洗中...</span>
          </div>
          <p class="mt-2">正在进行数据清洗，请稍候...</p>
        </div>
        
        <div v-else-if="gettingSuggestions" class="text-center py-3">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">分析中...</span>
          </div>
          <p class="mt-2">正在分析数据并生成清洗建议，请稍候...</p>
        </div>
        
        <div v-else>
          <!-- 清洗操作选择 -->
          <div class="mb-4">
            <h6>添加清洗操作</h6>
            <div class="row g-3">
              <div class="col-md-3">
                <select v-model="newOperation.type" class="form-select" aria-label="选择操作类型">
                  <option value="">选择操作类型</option>
                  <option value="fill_na">处理缺失值</option>
                  <option value="drop_duplicates">删除重复行</option>
                  <option value="handle_outliers">处理异常值</option>
                </select>
              </div>
              
              <!-- 根据操作类型显示不同的选项 -->
              <template v-if="newOperation.type === 'fill_na'">
                <div class="col-md-3">
                  <select v-model="newOperation.column" class="form-select" aria-label="选择列">
                    <option value="">选择列</option>
                    <option v-for="col in columns" :key="col.name" :value="col.name">
                      {{ col.name }} (缺失值: {{ col.missing_count }})
                    </option>
                  </select>
                </div>
                <div class="col-md-3">
                  <select v-model="newOperation.method" class="form-select" aria-label="选择填充方法">
                    <option value="">选择方法</option>
                    <option value="drop">删除含缺失值的行</option>
                    <option value="mean" v-if="getColumnType(newOperation.column) === 'numeric'">均值填充</option>
                    <option value="median" v-if="getColumnType(newOperation.column) === 'numeric'">中位数填充</option>
                    <option value="mode">众数填充</option>
                    <option value="value">固定值填充</option>
                  </select>
                </div>
                <div class="col-md-3" v-if="newOperation.method === 'value'">
                  <input type="text" v-model="newOperation.value" class="form-control" placeholder="输入填充值">
                </div>
              </template>
              
              <template v-else-if="newOperation.type === 'drop_duplicates'">
                <div class="col-md-3">
                  <select v-model="newOperation.columns" class="form-select" multiple aria-label="选择用于判断重复的列">
                    <option v-for="col in columns" :key="col.name" :value="col.name">
                      {{ col.name }}
                    </option>
                  </select>
                  <small class="form-text text-muted">按住Ctrl可多选</small>
                </div>
                <div class="col-md-3">
                  <select v-model="newOperation.keep" class="form-select" aria-label="保留哪一条">
                    <option value="first">保留第一条</option>
                    <option value="last">保留最后一条</option>
                  </select>
                </div>
              </template>
              
              <template v-else-if="newOperation.type === 'handle_outliers'">
                <div class="col-md-3">
                  <select v-model="newOperation.column" class="form-select" aria-label="选择列">
                    <option value="">选择列</option>
                    <option v-for="col in numericColumns" :key="col.name" :value="col.name">
                      {{ col.name }}
                    </option>
                  </select>
                </div>
                <div class="col-md-3">
                  <select v-model="newOperation.method" class="form-select" aria-label="选择处理方法">
                    <option value="">选择方法</option>
                    <option value="drop">删除异常值</option>
                    <option value="cap">截断异常值</option>
                  </select>
                </div>
                <div class="col-md-3" v-if="newOperation.method === 'cap'">
                  <input type="number" v-model.number="newOperation.threshold" class="form-control" placeholder="设置阈值(默认1.5)">
                </div>
              </template>
              
              <div class="col-12 text-end">
                <button 
                  class="btn btn-primary" 
                  @click="addOperation" 
                  :disabled="!canAddOperation"
                >
                  添加操作
                </button>
              </div>
            </div>
          </div>
          
          <!-- 当前操作列表 -->
          <div v-if="cleaningOperations.length > 0" class="mb-4">
            <h6>清洗操作列表</h6>
            <div class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>操作类型</th>
                    <th>目标列</th>
                    <th>方法</th>
                    <th>参数</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(op, index) in cleaningOperations" :key="index">
                    <td>{{ getOperationTypeName(op.type) }}</td>
                    <td>{{ op.column || (op.columns ? op.columns.join(', ') : '全部') }}</td>
                    <td>{{ getMethodName(op) }}</td>
                    <td>
                      <span v-if="op.value">{{ op.value }}</span>
                      <span v-else-if="op.threshold">阈值: {{ op.threshold }}</span>
                      <span v-else-if="op.keep">{{ op.keep === 'first' ? '保留第一条' : '保留最后一条' }}</span>
                    </td>
                    <td>
                      <button class="btn btn-sm btn-outline-danger" @click="removeOperation(index)">
                        删除
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div class="d-flex justify-content-end mt-3">
              <button class="btn btn-success" @click="executeCleanData">
                执行清洗
              </button>
            </div>
          </div>
          
          <!-- 清洗结果 -->
          <div v-if="cleaningResult" class="alert" :class="cleaningError ? 'alert-danger' : 'alert-success'">
            <h6>{{ cleaningError ? '清洗失败' : '清洗成功' }}</h6>
            <p v-if="cleaningError">{{ cleaningError }}</p>
            <div v-else>
              <p>
                <strong>行数变化：</strong><br>
                原始数据: {{ cleaningResult.original_count }} 行<br>
                清洗后: {{ cleaningResult.cleaned_count }} 行<br>
                移除: {{ cleaningResult.removed_count }} 行 
              </p>
              <p v-if="cleaningResult.added_column_count !== undefined">
                <strong>列数变化：</strong><br>
                原始列数: {{ cleaningResult.column_count - cleaningResult.added_column_count }} 列<br>
                清洗后: {{ cleaningResult.column_count }} 列<br>
                {{ cleaningResult.added_column_count > 0 ? '新增' : '减少' }}: {{ Math.abs(cleaningResult.added_column_count) }} 列
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="row mb-4">
      <div class="col-md-3 mb-3">
        <div class="card">
          <div class="card-body text-center">
            <h5>{{ row_count }}</h5>
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
            <h5>{{ file_type?.toUpperCase() || '未知' }}</h5>
            <p class="card-text text-muted">文件类型</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card">
          <div class="card-body text-center">
            <h5>{{ cleaned ? '已清洗' : '未清洗' }}</h5>
            <p class="card-text text-muted">状态</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 数据预览 -->
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
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
              <tr v-for="(row, index) in (preview || [])" :key="index">
                <td v-for="col in columns" :key="col.name">
                  {{ row[col.name] !== undefined && row[col.name] !== null ? row[col.name] : '' }}
                </td>
              </tr>
              <!-- 如果没有预览数据显示提示 -->
              <tr v-if="!preview || preview.length === 0">
                <td :colspan="columns.length" class="text-center py-3">
                  暂无预览数据
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import 'bootstrap/dist/css/bootstrap.min.css';

export default {
  name: 'DatasetDetail',
  data() {
    return {
      loading: true,
      row_count: 0,
      file_type: '',
      cleaned: false,
      preview: [],
      columns: [],
      showCleanOptions: false,
      cleaningOperations: [],
      newOperation: {
        type: '',
        column: '',
        method: '',
        value: '',
        columns: [],
        keep: 'first',
        threshold: 1.5
      },
      cleaning: false,
      cleaningError: null,
      cleaningResult: null,
    }
  },
  computed: {
    dataset() {
      return this.$store.getters.currentDataset || {}
    },
    datasetId() {
      return Number(this.$route.params.id)
    },
    canAddOperation() {
      const { type, column, method, columns } = this.newOperation
      
      if (!type) {
        return false
      }
      
      if (type === 'fill_na') {
        if (!column) return false
        if (!method) return false
        if (method === 'value' && !this.newOperation.value) {
          return false
        }
        return true
      }
      
      if (type === 'drop_duplicates') {
        return columns && columns.length > 0
      }
      
      if (type === 'handle_outliers') {
        if (!column) return false
        if (!method) return false
        return true
      }
      
      if (type === 'categorical_encoding') {
        return !!column && !!method
      }
      
      return false
    },
    // 过滤出数值型列
    numericColumns() {
      return this.columns.filter(col => this.getColumnType(col.name) === 'numeric')
    }
  },
  mounted() {
    this.fetchDataset()
  },
  methods: {
    async fetchDataset() {
      this.loading = true
      
      try {
        // 先检查是否有本地缓存的数据集信息
        if (!this.dataset || !this.dataset.id) {
          console.log('本地无数据集信息，从服务器获取...');
        }
        
        // 清除缓存，确保获取最新数据
        await this.$store.commit('setCurrentDataset', null)
        
        const result = await this.$store.dispatch('fetchDataset', this.datasetId)
        console.log('获取数据集结果:', result);
        
        if (result && result.success) {
          // 更新预览数据
          if (result.preview && Array.isArray(result.preview)) {
            this.preview = result.preview
          } else {
            this.preview = []
          }
          
          // 使用 Vuex store 更新数据集信息
          if (result.dataset) {
            await this.$store.commit('setCurrentDataset', result.dataset)
            console.log('已更新数据集信息到 store')
            
            this.file_type = result.dataset.file_type || ''
            this.cleaned = result.dataset.cleaned || false
            this.row_count = result.dataset.row_count || 0
            
            // 处理列信息
            if (result.dataset.columns) {
              try {
                // 尝试解析列信息
                let parsedColumns
                
                if (typeof result.dataset.columns === 'string') {
                  parsedColumns = JSON.parse(result.dataset.columns)
                } else if (Array.isArray(result.dataset.columns)) {
                  parsedColumns = result.dataset.columns
                } else {
                  console.warn('列信息格式不正确:', result.dataset.columns)
                  parsedColumns = null
                }
                
                // 检查解析后的列信息是否是标准格式
                if (parsedColumns && Array.isArray(parsedColumns)) {
                  if (parsedColumns.length > 0 && 'name' in parsedColumns[0] && 'type' in parsedColumns[0]) {
                    // 标准格式，直接使用
                    this.columns = parsedColumns
                    console.log('使用数据集标准列信息:', this.columns)
                  } else {
                    // 非标准格式，尝试转换
                    this.columns = Array.isArray(parsedColumns) ? 
                      parsedColumns.map(col => typeof col === 'string' ? 
                      {
                        name: col,
                        type: 'unknown',
                        missing_count: 0,
                        unique_count: 0
                      } : col) : []
                    console.log('转换后的列信息:', this.columns)
                  }
                } else {
                  // 解析失败或结果不是数组，尝试从预览数据提取
                  this.extractColumnsFromPreview(this.preview)
                }
                
              } catch (e) {
                console.error('处理columns数据失败:', e)
                // 尝试从预览数据提取列信息
                this.extractColumnsFromPreview(this.preview)
              }
            } else if (this.preview && this.preview.length > 0) {
              // 如果数据集中没有列信息，但有预览数据，从预览数据中提取列信息
              this.extractColumnsFromPreview(this.preview)
            } else {
              console.warn('数据集中没有列信息')
              this.columns = []
            }
          } else {
            console.error('数据集信息不存在')
            this.columns = []
          }
        } else {
          console.error('获取数据集失败:', result?.error || '未知错误')
          this.columns = []
        }
      } catch (err) {
        console.error('获取数据集过程中发生错误:', err)
        this.columns = []
      } finally {
        this.loading = false
      }
    },
    
    // 数据清洗相关方法
    
    // 获取列类型
    getColumnType(columnName) {
      if (!columnName) return null
      const column = this.columns.find(col => col.name === columnName)
      return column ? column.type : null
    },
    
    // 获取操作类型名称
    getOperationTypeName(type) {
      const typeNames = {
        'fill_na': '处理缺失值',
        'drop_duplicates': '删除重复行',
        'handle_outliers': '处理异常值',
        'categorical_encoding': '分类编码'
      }
      return typeNames[type] || type
    },
    
    // 获取操作方法名称
    getMethodName(operation) {
      if (!operation.method) return ''
      
      if (operation.type === 'fill_na') {
        const methodNames = {
          'drop': '删除行',
          'mean': '均值填充',
          'median': '中位数填充',
          'mode': '众数填充',
          'value': '固定值填充'
        }
        return methodNames[operation.method] || operation.method
      }
      
      if (operation.type === 'handle_outliers') {
        const methodNames = {
          'drop': '删除异常值',
          'cap': '截断异常值'
        }
        return methodNames[operation.method] || operation.method
      }
      
      return operation.method
    },
    
    // 添加清洗操作
    addOperation() {
      if (!this.canAddOperation) return
      
      const operation = { type: this.newOperation.type }
      
      // 根据操作类型添加不同的属性
      if (this.newOperation.type === 'fill_na') {
        operation.column = this.newOperation.column
        operation.method = this.newOperation.method
        if (operation.method === 'value') {
          operation.value = this.newOperation.value
        }
      } else if (this.newOperation.type === 'drop_duplicates') {
        operation.columns = [...this.newOperation.columns]
        operation.keep = this.newOperation.keep
      } else if (this.newOperation.type === 'handle_outliers') {
        operation.column = this.newOperation.column
        operation.method = this.newOperation.method
        if (operation.method === 'cap') {
          operation.threshold = this.newOperation.threshold || 1.5
        }
      }
      
      // 添加到操作列表
      this.cleaningOperations.push(operation)
      
      // 重置新操作表单
      this.resetNewOperation()
    },
    
    // 重置新操作表单
    resetNewOperation() {
      this.newOperation = {
        type: '',
        column: '',
        method: '',
        value: '',
        columns: [],
        keep: 'first',
        threshold: 1.5
      }
    },
    
    // 移除清洗操作
    removeOperation(index) {
      this.cleaningOperations.splice(index, 1)
    },
    
    // 执行数据清洗
    async executeCleanData() {
      if (this.cleaningOperations.length === 0) {
        this.cleaningError = '请至少添加一个清洗操作'
        return
      }
      
      this.cleaning = true
      this.cleaningError = null
      this.cleaningResult = null
      
      try {
        const result = await this.$store.dispatch('cleanDataset', {
          datasetId: this.datasetId,
          operations: this.cleaningOperations
        })
        
        if (result && result.success) {
          // 更新清洗结果信息
          this.cleaningResult = {
            original_count: result.original_count,
            cleaned_count: result.cleaned_count,
            removed_count: result.removed_count,
            column_count: result.column_count || this.columns.length,
            added_column_count: result.added_column_count || 0,
            columns: result.columns || []
          }
          
          // 更新预览数据
          if (result.preview && Array.isArray(result.preview)) {
            this.preview = result.preview
          }
          
          // 更新行数
          this.row_count = result.cleaned_count
          
          // 直接使用后端返回的列信息（标准格式）
          if (result.columns && Array.isArray(result.columns)) {
            // 检查是否是标准列格式（带有name和type属性）
            if (result.columns.length > 0 && 'name' in result.columns[0] && 'type' in result.columns[0]) {
              this.columns = result.columns
              console.log('使用清洗后返回的标准列信息:', this.columns)
            } else {
              // 如果不是标准格式，尝试从预览数据提取
              this.extractColumnsFromPreview(result.preview)
            }
          } else {
            // 列信息缺失，尝试从预览数据提取
            this.extractColumnsFromPreview(result.preview)
          }
          
          // 更新数据集状态
          this.cleaned = true
          
          // 刷新数据集信息
          await this.fetchDataset()
        } else {
          this.cleaningError = result?.error || '清洗失败'
        }
      } catch (error) {
        console.error('执行数据清洗时出错:', error)
        this.cleaningError = '执行清洗时发生错误: ' + (error.message || '未知错误')
      } finally {
        this.cleaning = false
      }
    },
    
    // 从预览数据中提取列信息
    extractColumnsFromPreview(preview) {
      if (preview && Array.isArray(preview) && preview.length > 0) {
        const previewData = preview[0]
        const columnNames = Object.keys(previewData)
        
        // 转换为标准列格式
        this.columns = columnNames.map(colName => {
          const value = previewData[colName]
          return {
            name: colName,
            type: typeof value === 'number' ? 'numeric' : 'categorical',
            missing_count: 0,
            unique_count: 1
          }
        })
        console.log('从预览数据提取的列信息:', this.columns)
      }
    },
  }
}
</script>

<style scoped>
</style>