<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
      <router-link class="navbar-brand" to="/">房价预测系统</router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav">
          <li class="nav-item" v-if="isAuthenticated">
            <router-link class="nav-link" to="/dashboard">我的数据集</router-link>
          </li>
        </ul>
        <ul class="navbar-nav ms-auto">
          <template v-if="isAuthenticated">
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                {{ currentUser.username }}
              </a>
              <ul class="dropdown-menu dropdown-menu-end">
                <li><a class="dropdown-item" href="#" @click.prevent="logout">退出登录</a></li>
              </ul>
            </li>
          </template>
          <template v-else>
            <li class="nav-item">
              <router-link class="nav-link" to="/login">登录</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/register">注册</router-link>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavBar',
  computed: {
    isAuthenticated() {
      return this.$store.getters.isAuthenticated
    },
    currentUser() {
      return this.$store.getters.currentUser
    }
  },
  methods: {
    async logout() {
      // 直接清除localStorage，不等待后端响应
      localStorage.removeItem('user')
      this.$store.commit('setUser', null)
      // 然后跳转到登录页
      this.$router.push('/login')
      
      // 在页面已跳转后，异步通知后端
      try {
        await this.$store.dispatch('logout')
      } catch (error) {
        console.error('通知后端登出失败:', error)
      }
    }
  }
}
</script> 