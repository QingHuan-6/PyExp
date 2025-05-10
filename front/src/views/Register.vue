<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow">
          <div class="card-body p-5">
            <h2 class="text-center mb-4">注册</h2>
            
            <div v-if="error" class="alert alert-danger">
              {{ error }}
            </div>
            
            <div v-if="success" class="alert alert-success">
              {{ success }}
            </div>
            
            <form @submit.prevent="register" v-if="!success">
              <div class="mb-3">
                <label for="username" class="form-label">用户名</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="username" 
                  v-model="registerForm.username"
                  required
                >
              </div>
              
              <div class="mb-3">
                <label for="email" class="form-label">邮箱</label>
                <input 
                  type="email" 
                  class="form-control" 
                  id="email" 
                  v-model="registerForm.email"
                  required
                >
              </div>
              
              <div class="mb-3">
                <label for="password" class="form-label">密码</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="password" 
                  v-model="registerForm.password"
                  required
                  minlength="6"
                >
                <div class="form-text">密码长度至少6个字符</div>
              </div>
              
              <div class="mb-3">
                <label for="confirmPassword" class="form-label">确认密码</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="confirmPassword" 
                  v-model="registerForm.confirmPassword"
                  required
                >
              </div>
              
              <div class="d-grid gap-2">
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="loading || !isFormValid"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  {{ loading ? '注册中...' : '注册' }}
                </button>
              </div>
            </form>
            
            <div class="text-center mt-4">
              <p>已有账号？ <router-link to="/login">立即登录</router-link></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Register',
  data() {
    return {
      registerForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      loading: false,
      error: null,
      success: null
    }
  },
  computed: {
    isFormValid() {
      return (
        this.registerForm.username && 
        this.registerForm.email && 
        this.registerForm.password && 
        this.registerForm.password.length >= 6 &&
        this.registerForm.password === this.registerForm.confirmPassword
      );
    }
  },
  methods: {
    async register() {
      if (!this.isFormValid) {
        if (this.registerForm.password !== this.registerForm.confirmPassword) {
          this.error = '两次输入的密码不一致';
        } else if (this.registerForm.password.length < 6) {
          this.error = '密码长度至少6个字符';
        } else {
          this.error = '请完成所有必填字段';
        }
        return;
      }
      
      this.loading = true;
      this.error = null;
      this.success = null;
      
      try {
        const userData = {
          username: this.registerForm.username,
          email: this.registerForm.email,
          password: this.registerForm.password
        };
        
        const result = await this.$store.dispatch('register', userData);
        
        if (result.success) {
          this.success = '注册成功！请前往登录页面登录';
          this.registerForm = {
            username: '',
            email: '',
            password: '',
            confirmPassword: ''
          };
        } else {
          this.error = result.error || '注册失败';
        }
      } catch (err) {
        console.error('注册出错:', err);
        this.error = '注册过程中发生错误';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script> 