<template>
  <div>
    <nav-bar />
    <div class="container mt-4">
      <router-view />
    </div>
    <footer class="footer mt-5 py-3 bg-light">
      <div class="container text-center">
        <span class="text-muted">房价预测分析系统 &copy; {{ new Date().getFullYear() }}</span>
      </div>
    </footer>
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue'

export default {
  name: 'App',
  components: {
    NavBar
  },
  created() {
    // 检查认证状态
    this.$store.dispatch('checkAuth')
  }
}
</script>

<style>
body {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
}

.footer {
  margin-top: auto;
}

#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
