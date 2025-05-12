<template>
  <div class="home">
    <div class="jumbotron bg-light p-5 rounded-3 mb-5">
      <div class="container-fluid py-4">
        <h1 class="display-4 fw-bold">房价预测数据分析平台</h1>
        <p class="col-md-8 fs-5">
          简单易用的房价数据分析工具，帮助您分析房地产数据并进行精准预测
        </p>
        <div class="d-grid gap-2 d-md-flex justify-content-md-start">
          <router-link to="/register" class="btn btn-primary btn-lg px-4 me-md-2">开始使用</router-link>
          <router-link to="/login" class="btn btn-outline-secondary btn-lg px-4">登录</router-link>
        </div>
      </div>
    </div>
    
    <h2 class="text-center mb-4">核心功能</h2>
    
    <div class="row g-4 py-4 row-cols-1 row-cols-lg-3">
      <div class="col">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <div class="feature-icon d-inline-flex align-items-center justify-content-center bg-primary bg-gradient text-white fs-2 mb-3 p-2 rounded-circle">
              <i class="bi bi-cloud-upload"></i>
            </div>
            <h3 class="fs-5">数据管理</h3>
            <p>支持CSV/Excel文件上传，数据预览，与MySQL数据库集成</p>
            <ul class="list-unstyled mt-3 text-start">
              <li class="mb-2 text-muted"><i class="bi bi-check-circle-fill text-success me-2"></i>多格式数据导入</li>
              <li class="mb-2 text-muted"><i class="bi bi-check-circle-fill text-success me-2"></i>预览和导出功能</li>
              <li class="text-muted"><i class="bi bi-check-circle-fill text-success me-2"></i>数据库集成</li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="col">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <div class="feature-icon d-inline-flex align-items-center justify-content-center bg-primary bg-gradient text-white fs-2 mb-3 p-2 rounded-circle">
              <i class="bi bi-graph-up"></i>
            </div>
            <h3 class="fs-5">数据可视化</h3>
            <p>动态生成多种图表，支持自定义参数的交互式可视化</p>
            <ul class="list-unstyled mt-3 text-start">
              <li class="mb-2 text-muted"><i class="bi bi-check-circle-fill text-success me-2"></i>柱状图、折线图</li>
              <li class="mb-2 text-muted"><i class="bi bi-check-circle-fill text-success me-2"></i>散点图、热力图</li>
              <li class="text-muted"><i class="bi bi-check-circle-fill text-success me-2"></i>自定义可视化参数</li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="col">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <div class="feature-icon d-inline-flex align-items-center justify-content-center bg-primary bg-gradient text-white fs-2 mb-3 p-2 rounded-circle">
              <i class="bi bi-cpu"></i>
            </div>
            <h3 class="fs-5">房价预测</h3>
            <p>集成多种机器学习算法，实现精准的房价预测分析</p>
            <ul class="list-unstyled mt-3 text-start">
              <li class="mb-2 text-muted"><i class="bi bi-check-circle-fill text-success me-2"></i>线性回归算法</li>
              <li class="mb-2 text-muted"><i class="bi bi-check-circle-fill text-success me-2"></i>随机森林算法</li>
              <li class="text-muted"><i class="bi bi-check-circle-fill text-success me-2"></i>模型效果评估</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.feature-icon {
  width: 3rem;
  height: 3rem;
}
</style> 