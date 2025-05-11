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
            <h5>{{ dataset?.file_type?.toUpperCase() || '未知' }}</h5>
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
    
    <!-- 数据预览 -->
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">数据预览</h5>
        <!-- 添加预览完整文件的按钮 -->
        <button 
          class="btn btn-sm btn-outline-primary" 
          @click="viewFullFile"
        >
          查看完整文件
        </button>
      </div>
      <div class="card-body p-0">
        <!-- 显示完整文件内容的模态框 -->
        <div class="modal fade" id="fullFileModal" tabindex="-1" aria-hidden="true">
          <div class="modal-dialog modal-xl modal-dialog-scrollable">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">{{ dataset.name }} - 完整内容</h5>
                <button type="button" class="btn-close" @click="closeModal"></button>
              </div>
              <div class="modal-body">
                <div v-if="loadingFullFile" class="text-center py-3">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">加载中...</span>
                  </div>
                  <p class="mt-2">正在加载完整文件数据，请稍候...</p>
                </div>
                <div v-else>
                  <!-- 显示文件统计信息 -->
                  <div class="alert alert-info mb-3" v-if="fullFileData.length > 0">
                    文件包含 <strong>{{ fullFileData.length }}</strong> 行数据，
                    <strong>{{ columns.length }}</strong> 列
                  </div>
                  
                  <!-- 完整文件内容表格 -->
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
                        <tr v-for="(row, index) in fullFileData" :key="index">
                          <td v-for="col in columns" :key="col.name">
                            {{ row[col.name] !== undefined && row[col.name] !== null ? row[col.name] : '' }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  
                  <!-- 如果数据为空显示提示 -->
                  <div v-if="fullFileData.length === 0" class="text-center py-5 text-muted">
                    <i class="bi bi-file-earmark-x display-4 mb-3"></i>
                    <p>文件内容为空或无法读取</p>
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeModal">关闭</button>
              </div>
            </div>
          </div>
        </div>
        
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
                  {{ row[col.name] || '' }}
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
import { Modal } from 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

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
      loadingFullFile: false,
      fullFileData: [],
      bootstrapModal: null,
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
      this.columns = [] // 先初始化为空数组，避免未定义错误
      
      try {
        // 先检查是否有本地缓存的数据集信息
        if (!this.dataset || !this.dataset.id) {
          console.log('本地无数据集信息，从服务器获取...');
        }
        
        const result = await this.$store.dispatch('fetchDataset', this.datasetId)
        console.log('获取数据集结果:', result);
        
        if (result && result.success) {
          // 确保预览数据存在
          this.preview = result.preview || []
          
          // 确保数据集信息存在
          if (this.dataset) {
            console.log('获取到数据集信息:', this.dataset);
            
            // 安全地解析columns数据
            if (this.dataset.columns) {
              try {
                this.columns = JSON.parse(this.dataset.columns)
                console.log('解析的列信息:', this.columns);
              } catch (e) {
                console.error('解析columns数据失败:', e)
                this.columns = []
              }
            } else {
              console.warn('数据集中没有列信息')
              this.columns = []
            }
          } else {
            console.error('数据集信息不存在')
          }
        } else {
          console.error('获取数据集失败:', result?.error || '未知错误')
        }
      } catch (err) {
        console.error('获取数据集过程中发生错误:', err)
      } finally {
        this.loading = false
      }
    },
    
    async viewFullFile() {
      if (!this.dataset || !this.dataset.id) {
        alert('数据集信息不完整，无法查看完整文件');
        return;
      }
      
      this.loadingFullFile = true;
      this.fullFileData = [];
      
      try {
        // 使用导入的Modal
        const modalEl = document.getElementById('fullFileModal');
        this.bootstrapModal = new Modal(modalEl);
        this.bootstrapModal.show();
        
        console.log(`准备获取数据集 ${this.datasetId} 的完整文件内容`);
        
        // 获取完整文件内容
        const response = await fetch(`/api/data/datasets/${this.datasetId}/full`);
        
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`服务器返回错误(${response.status}): ${errorText}`);
        }
        
        const data = await response.json();
        console.log('获取到完整文件响应:', data);
        
        if (data && data.success) {
          // 设置文件数据
          this.fullFileData = data.data || [];
          
          // 记录统计信息
          const stats = data.stats || {};
          console.log(`成功获取完整文件数据，共 ${stats.row_count || this.fullFileData.length} 行，${stats.column_count || '未知'} 列`);
          
          // 确保有列信息可以显示
          if (this.columns.length === 0 && this.fullFileData.length > 0) {
            // 从第一条记录中提取列信息
            const firstRecord = this.fullFileData[0];
            this.columns = Object.keys(firstRecord).map(key => ({
              name: key,
              type: typeof firstRecord[key] === 'number' ? 'numeric' : 'categorical'
            }));
            console.log('从完整数据中提取的列信息:', this.columns);
          }
        } else {
          throw new Error(data?.error || '获取完整文件失败');
        }
      } catch (err) {
        console.error('获取完整文件时出错:', err);
        alert(`获取完整文件失败: ${err.message || '未知错误'}`);
        this.closeModal();
      } finally {
        this.loadingFullFile = false;
      }
    },
    
    closeModal() {
      if (this.bootstrapModal) {
        this.bootstrapModal.hide();
      }
    }
  },
  beforeUnmount() {
    // 移除事件监听器，避免内存泄漏
    const closeButtons = document.querySelectorAll('[data-bs-dismiss="modal"]');
    closeButtons.forEach(button => {
      button.removeEventListener('click', this.closeModal);
    });
  }
}
</script>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  outline: 0;
  display: none;
}

.modal.show {
  display: block;
}

.modal-dialog {
  position: relative;
  width: auto;
  margin: 0.5rem;
  pointer-events: none;
  max-width: 90%;
  margin: 1.75rem auto;
}

.modal-dialog-scrollable {
  display: flex;
  max-height: calc(100% - 3.5rem);
}

.modal-content {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  pointer-events: auto;
  background-color: #fff;
  background-clip: padding-box;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 0.3rem;
  outline: 0;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1040;
  width: 100vw;
  height: 100vh;
  background-color: #000;
  opacity: 0.5;
}

.modal-body {
  position: relative;
  flex: 1 1 auto;
  padding: 1rem;
}

.modal-header,
.modal-footer {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  border-top-left-radius: calc(0.3rem - 1px);
  border-top-right-radius: calc(0.3rem - 1px);
}

.modal-footer {
  border-top: 1px solid #dee2e6;
  border-bottom: none;
}
</style>