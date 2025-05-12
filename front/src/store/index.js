import { createStore } from 'vuex'
import axios from 'axios'

export default createStore({
  state: {
    user: null,
    datasets: [],
    currentDataset: null
  },
  mutations: {
    setUser(state, user) {
      state.user = user
    },
    setDatasets(state, datasets) {
      state.datasets = datasets
    },
    setCurrentDataset(state, dataset) {
      state.currentDataset = dataset
    },
    addDataset(state, dataset) {
      state.datasets.push(dataset)
    }
  },
  actions: {
    // 用户认证
    async login({ commit }, credentials) {
      try {
        const response = await axios.post('/auth/login', credentials)
        const user = response.data.user
        localStorage.setItem('user', JSON.stringify(user))
        commit('setUser', user)
        return { success: true }
      } catch (error) {
        return { success: false, error: error.response?.data?.error || '登录失败' }
      }
    },
    
    async register(_, userData) {
      try {
        await axios.post('/auth/register', userData)
        return { success: true }
      } catch (error) {
        return { success: false, error: error.response?.data?.error || '注册失败' }
      }
    },
    
    async logout({ commit }) {
      try {
        // 即使后端请求失败，也要确保本地登出
        try {
          // 完整URL，确保正确性
          await axios.post('/auth/logout')
        } catch (error) {
          console.error('服务器退出请求失败:', error.message)
          // 忽略后端错误继续执行
        }
        
        // 无论后端成功与否，都执行前端登出
        localStorage.removeItem('user')
        commit('setUser', null)
        return { success: true }
      } catch (error) {
        console.error('前端登出操作失败:', error)
        return { success: false, error: '登出失败' }
      }
    },
    
    checkAuth({ commit }) {
      try {
        const userStr = localStorage.getItem('user')
        if (userStr) {
          const user = JSON.parse(userStr)
          commit('setUser', user)
        } else {
          commit('setUser', null)
        }
      } catch (error) {
        // 处理JSON解析错误
        console.error('Error parsing user data from localStorage:', error)
        localStorage.removeItem('user') // 清除无效数据
        commit('setUser', null)
      }
    },
    
    // 数据集管理
    async fetchDatasets({ commit, state }) {
      try {
        // 从状态中获取用户ID
        const userId = state.user ? state.user.id : null;
        
        // 在请求中包含用户ID
        const response = await axios.get('/data/datasets', {
          params: { user_id: userId },
          headers: { 'X-User-ID': userId }
        });
        
        const datasets = response.data.datasets || [];
        commit('setDatasets', datasets);
        return { success: true, datasets };
      } catch (error) {
        console.error('获取数据集错误:', error);
        commit('setDatasets', []);
        return { success: false, error: '获取数据集失败' };
      }
    },
    
    async fetchDataset({ commit }, datasetId) {
      try {
        const response = await axios.get(`/data/datasets/${datasetId}`);
        const data = response.data;
        
        if (data && data.dataset) {
          commit('setCurrentDataset', data.dataset);
          return {
            success: true,
            dataset: data.dataset,
            preview: data.preview || []
          };
        }
        
        return { 
          success: false, 
          error: '服务器返回的数据格式不正确' 
        };
      } catch (error) {
        console.error('获取数据集详情失败:', error);
        return { 
          success: false, 
          error: error.response?.data?.error || '获取数据集详情失败' 
        };
      }
    },
    async uploadDataset({ commit, state }, { file, description }) {
      try {
        console.log('开始上传文件:', file.name);
        
        // 获取用户ID（如果有）
        const userId = state.user ? state.user.id : null;
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('description', description || '');
        if (userId) {
          formData.append('user_id', userId);
        }
        
        console.log('FormData准备完成，即将上传');
        
        // 设置更多调试信息
        const response = await axios.post('/data/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'X-User-ID': userId
          },
          withCredentials: true,
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            console.log(`上传进度: ${percentCompleted}%`);
          }
        });
        
        console.log('上传响应:', response.data);
        
        if (response.data) {
          let dataset = response.data.dataset || {};
          
          if (!dataset.id && response.data.id) {
            dataset = response.data;
          }
          
          if (dataset.id) {
            commit('addDataset', dataset);
            return {
              success: true,
              dataset: dataset,
              preview: response.data.preview || []
            };
          }
        }
        
        return { 
          success: true,
          message: '文件已上传，但返回数据格式不符合预期'
        };
      } catch (error) {
        console.error('上传错误详情:', error.response?.data || error.message);
        return {
          success: false,
          error: error.response?.data?.error || '上传失败'
        };
      }
    },
    
    // 数据清洗
    async cleanDataset(_, { datasetId, operations }) {
      try {
        const response = await axios.post(`/data/datasets/${datasetId}/clean`, { operations });
        
        if (response.data) {
          return { 
            success: true, 
            preview: response.data.preview || [],
            original_count: response.data.original_count,
            cleaned_count: response.data.cleaned_count,
            removed_count: response.data.removed_count,
            column_count: response.data.column_count,
            added_column_count: response.data.added_column_count,
            columns: response.data.columns
          };
        }
        return { success: false, error: '服务器返回数据格式不正确' };
      } catch (error) {
        console.error('数据清洗错误:', error.response?.data || error.message);
        return { 
          success: false, 
          error: error.response?.data?.error || '数据清洗失败' 
        };
      }
    },
    
    // 数据可视化
    async createVisualization(_, { datasetId, chartType, config, name }) {
      try {
        const response = await axios.post(`/analysis/visualize/${datasetId}`, {
          chart_type: chartType,
          config,
          name
        });
        
        if (response.data && response.data.visualization_id) {
          return { 
            success: true, 
            visualizationId: response.data.visualization_id,
            imageUrl: response.data.image_url || ''
          };
        }
        return { success: false, error: '服务器返回数据格式不正确' };
      } catch (error) {
        console.error('可视化创建错误:', error.response?.data || error.message);
        return { 
          success: false, 
          error: error.response?.data?.error || '创建可视化失败' 
        };
      }
    },
    
    // 房价预测
    async trainModel(_, { datasetId, algorithm, features, target, name }) {
      try {
        const response = await axios.post(`/analysis/predict/${datasetId}`, {
          algorithm,
          features,
          target,
          name
        });
        
        if (response.data && response.data.prediction_id) {
          return { 
            success: true, 
            predictionId: response.data.prediction_id,
            metrics: response.data.metrics || {}
          };
        }
        return { success: false, error: '服务器返回数据格式不正确' };
      } catch (error) {
        console.error('模型训练错误:', error.response?.data || error.message);
        return { 
          success: false, 
          error: error.response?.data?.error || '模型训练失败' 
        };
      }
    },
    
    async getPredictions(_, datasetId) {
      try {
        const response = await axios.get(`/analysis/predictions/${datasetId}`);
        
        if (response.data && response.data.predictions) {
          return { 
            success: true, 
            predictions: response.data.predictions 
          };
        }
        return { success: false, error: '服务器返回数据格式不正确' };
      } catch (error) {
        console.error('获取预测错误:', error.response?.data || error.message);
        return { 
          success: false, 
          error: error.response?.data?.error || '获取预测模型失败' 
        };
      }
    }
  },
  getters: {
    isAuthenticated(state) {
      return !!state.user
    },
    currentUser(state) {
      return state.user || {}
    },
    datasets(state) {
      return state.datasets || []
    },
    currentDataset(state){
      return state.currentDataset || {}
    }
  }
})