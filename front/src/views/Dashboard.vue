<template>
  <div class="dashboard">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>我的数据集</h2>
      <button 
        class="btn btn-primary" 
        data-bs-toggle="modal" 
        data-bs-target="#uploadModal"
      >
        <i class="bi bi-cloud-upload me-2"></i> 上传数据集
      </button>
    </div>
    
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
      <p class="mt-2 text-muted">加载数据集...</p>
    </div>
    
    <div v-else-if="datasets.length === 0" class="text-center py-5 bg-light rounded">
      <div class="py-5">
        <i class="bi bi-folder2-open display-1 text-muted mb-3"></i>
        <h4>暂无数据集</h4>
        <p class="text-muted mb-4">您还没有上传任何数据集</p>
        <button 
          class="btn btn-primary" 
          data-bs-toggle="modal" 
          data-bs-target="#uploadModal"
        >
          <i class="bi bi-cloud-upload me-2"></i> 上传第一个数据集
        </button>
      </div>
    </div>
    
    <div v-else class="row g-4">
      <div 
        v-for="dataset in datasets" 
        :key="dataset.id" 
        class="col-md-6 col-lg-4"
      >
        <div class="card h-100 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <i class="bi bi-table me-2 fs-4 text-primary"></i>
              <h5 class="card-title mb-0 text-truncate">{{ dataset.name }}</h5>
            </div>
            
            <p class="card-text text-muted small mb-3" style="height: 40px; overflow: hidden;">
              {{ dataset.description || '没有描述' }}
            </p>
            
            <div class="d-flex flex-wrap gap-2 mb-3">
              <span class="badge bg-secondary">{{ dataset.file_type }}</span>
              <span class="badge bg-info">{{ dataset.row_count }} 行</span>
              <span 
                class="badge"
                :class="dataset.cleaned ? 'bg-success' : 'bg-warning'"
              >
                {{ dataset.cleaned ? '已清洗' : '未清洗' }}
              </span>
            </div>
            
            <p class="card-text">
              <small class="text-muted">上传时间: {{ formatDate(dataset.created_at) }}</small>
            </p>
          </div>
          <div class="card-footer bg-transparent border-top-0">
            <router-link 
              :to="`/dataset/${dataset.id}`" 
              class="btn btn-sm btn-outline-primary w-100"
              v-if="dataset && dataset.id"
            >
              查看详情
            </router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 上传数据集模态框 -->
    <div class="modal fade" id="uploadModal" tabindex="-1" aria-labelledby="uploadModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="uploadModalLabel">上传数据集</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="uploadError" class="alert alert-danger">
              {{ uploadError }}
            </div>
            
            <form @submit.prevent="uploadDataset">
              <div class="mb-3">
                <label for="file" class="form-label">选择文件</label>
                <input 
                  type="file" 
                  class="form-control" 
                  id="file"
                  ref="fileInput"
                  @change="handleFileChange"
                  accept=".csv,.xlsx,.xls"
                  required
                >
                <div class="form-text">支持 CSV, Excel (xlsx, xls) 格式文件</div>
              </div>
              
              <div class="mb-3">
                <label for="description" class="form-label">描述 (可选)</label>
                <textarea 
                  class="form-control" 
                  id="description" 
                  rows="3"
                  v-model="uploadForm.description"
                  placeholder="添加数据集的简要描述"
                ></textarea>
              </div>
              
              <div class="d-grid">
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="uploading || !uploadForm.file"
                >
                  <span v-if="uploading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  {{ uploading ? '上传中...' : '上传' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data() {
    return {
      loading: true,
      uploading: false,
      uploadError: null,
      uploadForm: {
        file: null,
        description: ''
      }
    }
  },
  computed: {
    datasets() {
      return this.$store.getters.datasets || []
    }
  },
  mounted() {
    this.fetchDatasets()
  },
  methods: {
    async fetchDatasets() {
      this.loading = true
      
      try {
        console.log('开始获取数据集...当前用户:', this.$store.getters.currentUser)
        
        // 直接使用store的方法，不再单独调用axios
        const result = await this.$store.dispatch('fetchDatasets')
        console.log('获取数据集结果:', result)
      } catch (err) {
        console.error('获取数据集失败', err)
      } finally {
        this.loading = false
      }
    },
    
    handleFileChange(event) {
      this.uploadForm.file = event.target.files[0]
    },
    
    async uploadDataset() {
      this.uploading = true;
      this.uploadError = null;
      
      try {
        const result = await this.$store.dispatch('uploadDataset', {
          file: this.uploadForm.file,
          description: this.uploadForm.description
        });
        
        console.log('上传结果:', result);
        
        if (result && result.success) {
          // 无论是否有dataset对象，都刷新数据集列表
          await this.fetchDatasets();
          
          // 重置表单
          this.uploadForm.file = null;
          this.uploadForm.description = '';
          
          // 关闭模态窗口 - 使用 jQuery 方式关闭，不依赖 bootstrap 变量
          const modalEl = document.getElementById('uploadModal');
          if (modalEl) {
            // 使用 jQuery 方式关闭模态窗口
            modalEl.classList.remove('show');
            modalEl.style.display = 'none';
            document.body.classList.remove('modal-open');
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
              backdrop.remove();
            }
          }
          
          // 显示成功消息
          alert('文件上传成功!');
        } else {
          this.uploadError = result?.error || '上传失败';
        }
      } catch (error) {
        console.error('上传出错:', error);
        this.uploadError = '上传过程中发生错误';
      } finally {
        this.uploading = false;
      }
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString()
    }
  }
}
</script> 