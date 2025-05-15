<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow">
          <div class="card-body p-5">
            <h2 class="text-center mb-4">登录</h2>
            
            <div v-if="error" class="alert alert-danger">
              {{ error }}
            </div>
            
            <form @submit.prevent="login">
              <div class="mb-3">
                <label for="username" class="form-label">用户名或邮箱</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="username" 
                  v-model="loginForm.username"
                  required
                >
              </div>
              
              <div class="mb-3">
                <label for="password" class="form-label">密码</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="password" 
                  v-model="loginForm.password"
                  required
                >
              </div>
              
              <div class="d-grid gap-2">
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  {{ loading ? '登录中...' : '登录' }}
                </button>
              </div>
            </form>
            
            <div class="text-center mt-4">
              <p>还没有账号？ <router-link to="/register">立即注册</router-link></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      loading: false,
      error: null
    }
  },
  methods: {
    async login() {
      this.loading = true;
      this.error = null;
      
      try {
        const result = await this.$store.dispatch('login', this.loginForm);
        
        if (result.success) {
          // 登录成功，重定向到仪表盘
          this.$router.push('/dashboard');
        } else {
          this.error = result.error || '登录失败';
        }
      } catch (err) {
        console.error('登录出错:', err);
        this.error = '登录过程中发生错误';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script> 