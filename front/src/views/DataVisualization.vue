<template>
  <div class="data-visualization">
    <div class="container-fluid py-4">
      <div class="card mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h3>数据可视化 - {{ datasetName }}</h3>
          <div v-if="loading" class="spinner-border text-primary" role="status">
            <span class="visually-hidden">加载中...</span>
          </div>
        </div>
        <div class="card-body">
          <div class="alert alert-info" v-if="!hasData">
            正在加载数据，请稍候...
          </div>
          <div class="alert alert-danger" v-if="error">
            {{ error }}
          </div>
          
          <!-- 图表按钮区域 -->
          <div class="row mb-4" v-if="hasData">
            <div class="col-md-12">
              <div class="btn-group mb-3">
                <button class="btn btn-primary" @click="generatePriceDistribution">
                  <i class="bi bi-bar-chart-line me-1"></i>房屋价格分布
                </button>
                <button class="btn btn-primary" @click="generateNeighborhoodVsPrice">
                  <i class="bi bi-box-seam me-1"></i>社区与房价对比
                </button>
                <button class="btn btn-primary" @click="generateQualityVsPrice">
                  <i class="bi bi-bar-chart-steps me-1"></i>质量与房价关系
                </button>
                <button class="btn btn-primary" @click="generateCategoryDistributions">
                  <i class="bi bi-pie-chart me-1"></i>类别特征分布
                </button>
              </div>
            </div>
          </div>
          
          <!-- 图表渲染区域 -->
          <div class="row" v-if="hasData && !showMultipleCharts">
            <div class="col-md-12">
              <div ref="chartContainer" style="width: 100%; height: 500px;"></div>
            </div>
          </div>
          
          <!-- 多图表展示区域 -->
          <div class="row mt-2" v-if="showMultipleCharts">
            <div class="col-md-4" v-for="(chart, index) in multipleCharts" :key="index">
              <div class="card mb-3 category-chart-card">
                <div class="card-header py-2">{{ chart.title }}</div>
                <div class="card-body p-2">
                  <div :id="`subChart${index}`" :ref="`subChart${index}`" style="width: 100%; height: 250px;"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts';
import 'bootstrap-icons/font/bootstrap-icons.css';

export default {
  name: 'DataVisualization',
  data() {
    return {
      loading: false,
      error: null,
      datasetId: '',
      dataset: null,
      datasetName: '',
      fullData: [],
      columns: [],
      chart: null,
      showMultipleCharts: false,
      multipleCharts: [],
      multipleChartsInstances: []
    };
  },
  computed: {
    hasData() {
      return this.fullData && this.fullData.length > 0;
    }
  },
  methods: {
    async fetchDataset() {
      this.loading = true;
      this.error = null;
      
      try {
        // 获取数据集基本信息
        this.datasetId = this.$route.params.id;
        const basicInfoResponse = await axios.get(`/data/datasets/${this.datasetId}`);
        
        if (basicInfoResponse.data && basicInfoResponse.data.dataset) {
          this.dataset = basicInfoResponse.data.dataset;
          this.datasetName = this.dataset.name;
          
          // 解析列信息
          if (this.dataset.columns && typeof this.dataset.columns === 'string') {
            this.columns = JSON.parse(this.dataset.columns);
          } else if (Array.isArray(this.dataset.columns)) {
            this.columns = this.dataset.columns;
          }
          
          // 获取完整数据集
          const fullDataResponse = await axios.get(`/data/datasets/${this.datasetId}/full`);
          
          if (fullDataResponse.data && fullDataResponse.data.success && fullDataResponse.data.data) {
            this.fullData = fullDataResponse.data.data;
            console.log(`加载了 ${this.fullData.length} 行数据`);
          } else {

            this.error = fullDataResponse.data.error || '无法加载完整数据集';
          }
        } else {
          this.error = basicInfoResponse.data.error || '无法加载数据集信息';
        }
      } catch (error) {
        console.error('获取数据集失败:', error);
        this.error = error.response?.data?.error || '获取数据集失败，请检查网络连接';
      } finally {
        this.loading = false;
      }
    },
    
    // 初始化图表实例
    initChart() {
      if (this.chart) {
        this.chart.dispose();
      }
      
      this.chart = echarts.init(this.$refs.chartContainer);
      
      // 自适应大小
      window.addEventListener('resize', () => {
        this.chart.resize();
      });
      
      return this.chart;
    },
    
    // 生成房价分布图 (直方图)
    generatePriceDistribution() {
      this.showMultipleCharts = false;
      
      // 确保在下一个DOM更新周期执行图表初始化
      this.$nextTick(() => {
        const chart = this.initChart();
        
        // 提取价格数据
        const priceData = this.fullData
          .filter(item => item.SalePrice !== undefined && item.SalePrice !== null)
          .map(item => item.SalePrice);
        
        if (priceData.length === 0) {
          this.error = '找不到SalePrice数据';
          return;
        }
        
        // 计算价格区间
        const min = Math.min(...priceData);
        const max = Math.max(...priceData);
        const range = max - min;
        const binWidth = range / 30; // 30个bin
        
        // 创建价格区间
        const bins = Array.from({ length: 30 }, (_, i) => ({
          min: min + i * binWidth,
          max: min + (i + 1) * binWidth
        }));
        
        // 统计每个区间的频数
        const counts = bins.map(bin => {
          return priceData.filter(price => price >= bin.min && price < bin.max).length;
        });
        
        // 设置x轴标签
        const labels = bins.map(bin => `${Math.round(bin.min / 1000)}k`);
        
        // 配置图表选项
        const option = {
          title: {
            text: '房屋价格分布',
            left: 'center'
          },
          tooltip: {
            trigger: 'axis',
            formatter: function (params) {
              const bin = bins[params[0].dataIndex];
              return `价格区间: ${Math.round(bin.min)}-${Math.round(bin.max)}<br/>数量: ${params[0].value}`;
            }
          },
          xAxis: {
            type: 'category',
            data: labels,
            name: '价格 (千美元)',
            axisLabel: {
              rotate: 45
            }
          },
          yAxis: {
            type: 'value',
            name: '房屋数量'
          },
          series: [
            {
              name: '房屋数量',
              type: 'bar',
              data: counts,
              itemStyle: {
                color: '#5470c6'
              }
            }
          ],
          dataZoom: [
            {
              type: 'slider',
              show: true,
              xAxisIndex: [0],
              start: 0,
              end: 100
            }
          ]
        };
        
        chart.setOption(option);
      });
    },
    
    // 生成社区与房价对比图 (箱形图)
    generateNeighborhoodVsPrice() {
      this.showMultipleCharts = false;
      this.error = null;
      
      // 确保在DOM更新后初始化图表
      this.$nextTick(() => {
        try {
          console.log("开始生成社区与房价对比图");
          const chart = this.initChart();
          
          // 打印原始数据的一部分，以便检查
          console.log("fullData部分示例:", this.fullData.slice(0, 3));
          
          // 检查Neighborhood字段
          const hasNeighborhoodField = this.fullData.some(item => item.Neighborhood !== undefined);
          console.log("是否包含Neighborhood字段:", hasNeighborhoodField);
          
          if (!hasNeighborhoodField) {
            this.error = "数据中找不到'Neighborhood'字段，请确认字段名称是否正确";
            console.error(this.error);
            return;
          }

          // 检查SalePrice字段
          const hasSalePriceField = this.fullData.some(item => item.SalePrice !== undefined);
          console.log("是否包含SalePrice字段:", hasSalePriceField);
          
          if (!hasSalePriceField) {
            this.error = "数据中找不到'SalePrice'字段，请确认字段名称是否正确";
            console.error(this.error);
            return;
          }
          
          // 按社区分组
          const neighborhoods = [...new Set(this.fullData
            .filter(item => item.Neighborhood)
            .map(item => item.Neighborhood))];
          
          console.log("找到的社区数量:", neighborhoods.length);
          console.log("社区列表:", neighborhoods);
          
          if (neighborhoods.length === 0) {
            this.error = "找不到有效的社区数据";
            console.error(this.error);
            return;
          }
          
          // 准备每个社区的价格数据
          const boxData = [];
          let errorMessage = "";
          
          for (const neighborhood of neighborhoods) {
            try {
              const prices = this.fullData
                .filter(item => item.Neighborhood === neighborhood && item.SalePrice !== undefined && item.SalePrice !== null)
                .map(item => item.SalePrice);
              
              console.log(`社区 ${neighborhood} 的价格数量:`, prices.length);
              
              if (prices.length === 0) {
                console.warn(`社区 ${neighborhood} 没有有效价格数据，跳过`);
                continue;
              }
              
              boxData.push({
                name: neighborhood,
                prices,
                // 计算统计值
                min: Math.min(...prices),
                q1: this.percentile(prices, 25),
                median: this.percentile(prices, 50),
                q3: this.percentile(prices, 75),
                max: Math.max(...prices),
                // 计算均值，用于排序
                mean: prices.reduce((a, b) => a + b, 0) / prices.length
              });
            } catch (err) {
              console.error(`处理社区 ${neighborhood} 数据时出错:`, err);
              errorMessage = `处理社区数据时出错: ${err.message}`;
            }
          }
          
          if (boxData.length === 0) {
            this.error = errorMessage || "无法生成有效的箱线图数据";
            console.error(this.error);
            return;
          }
          
          console.log("生成的箱线图数据:", boxData);
          
          // 按均价排序
          boxData.sort((a, b) => b.mean - a.mean);
          
          // 限制展示前15个社区，避免图表太拥挤
          const topNeighborhoods = boxData.slice(0, 15);
          
          // 配置选项
          const option = {
            title: {
              text: '社区与房价对比 (箱形图)',
              left: 'center'
            },
            tooltip: {
              trigger: 'item',
              formatter: function (params) {
                const data = params.data;
                return `${params.name}<br/>
                        最小值: $${Math.round(data[1])}<br/>
                        下四分位: $${Math.round(data[2])}<br/>
                        中位数: $${Math.round(data[3])}<br/>
                        上四分位: $${Math.round(data[4])}<br/>
                        最大值: $${Math.round(data[5])}`;
              }
            },
            grid: {
              left: '10%',
              right: '10%',
              bottom: '15%'
            },
            xAxis: {
              type: 'category',
              data: topNeighborhoods.map(item => item.name),
              axisLabel: {
                interval: 0,
                rotate: 45
              },
              name: '社区'
            },
            yAxis: {
              type: 'value',
              name: '售价 (美元)',
              scale: true
            },
            series: [
              {
                name: '房价',
                type: 'boxplot',
                data: topNeighborhoods.map(item => {
                  // 注意顺序：[最小值, 下四分位数, 中位数, 上四分位数, 最大值]
                  return [
                    item.min,
                    item.q1,
                    item.median,
                    item.q3,
                    item.max
                  ];
                }),
                tooltip: {show: true}
              }
            ]
          };
          
          console.log("设置ECharts选项");
          chart.setOption(option);
          console.log("社区与房价对比图生成完成");
        } catch (error) {
          console.error("生成社区与房价对比图时出错:", error);
          this.error = `生成图表错误: ${error.message}`;
        }
      });
    },
    
    // 生成房屋质量与房价关系图 (箱形图)
    generateQualityVsPrice() {
      this.showMultipleCharts = false;
      
      // 确保在DOM更新后初始化图表
      this.$nextTick(() => {
        const chart = this.initChart();
        
        // 获取所有可能的质量等级
        const qualityLevels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].filter(level => 
          this.fullData.some(item => item.OverallQual === level)
        );
        
        // 按质量等级分组价格数据
        const boxData = qualityLevels.map(level => {
          const prices = this.fullData
            .filter(item => item.OverallQual === level && item.SalePrice !== undefined)
            .map(item => item.SalePrice);
            
          return {
            level,
            prices,
            // 计算统计值
            min: Math.min(...prices),
            q1: this.percentile(prices, 25),
            median: this.percentile(prices, 50),
            q3: this.percentile(prices, 75),
            max: Math.max(...prices)
          };
        });
        
        // 按质量等级排序
        boxData.sort((a, b) => a.level - b.level);
        
        // 配置选项
        const option = {
          title: {
            text: '房屋质量与价格关系 (箱形图)',
            left: 'center'
          },
          tooltip: {
            trigger: 'item',
            formatter: function (params) {
              const data = params.data;
              return `质量等级: ${params.name}<br/>
                      最小值: $${Math.round(data[1])}<br/>
                      下四分位: $${Math.round(data[2])}<br/>
                      中位数: $${Math.round(data[3])}<br/>
                      上四分位: $${Math.round(data[4])}<br/>
                      最大值: $${Math.round(data[5])}`;
            }
          },
          xAxis: {
            type: 'category',
            data: boxData.map(item => item.level),
            name: '整体质量 (1-10)'
          },
          yAxis: {
            type: 'value',
            name: '售价 (美元)',
            scale: true
          },
          series: [
            {
              name: '房价',
              type: 'boxplot',
              data: boxData.map(item => [
                item.level,
                item.min,
                item.q1,
                item.median,
                item.q3,
                item.max
              ]),
              tooltip: {show: true}
            }
          ]
        };
        
        chart.setOption(option);
      });
    },
    
    // 生成多个类别特征分布图
    generateCategoryDistributions() {
      try {
        console.log("开始生成类别特征分布图");
        this.error = null;
        
        // 设置多图表模式
        this.showMultipleCharts = true;
        
        // 清除主图表
        if (this.chart) {
          this.chart.dispose();
          this.chart = null;
        }
        
        // 清除旧的多图表实例
        this.multipleChartsInstances.forEach(chart => {
          if (chart) chart.dispose();
        });
        this.multipleChartsInstances = [];
        
        // 定义要展示的类别特征
        const features = ['MSZoning', 'LotShape', 'HouseStyle'];
        
        // 检查数据中是否包含这些字段
        const missingFeatures = [];
        for (const feature of features) {
          const hasFeature = this.fullData.some(item => item[feature] !== undefined);
          console.log(`是否包含 ${feature} 字段:`, hasFeature);
          if (!hasFeature) {
            missingFeatures.push(feature);
          }
        }
        
        if (missingFeatures.length > 0) {
          this.error = `数据中找不到以下字段: ${missingFeatures.join(', ')}`;
          console.error(this.error);
          return;
        }
        
        this.multipleCharts = features.map(feature => ({ 
          title: this.getFeatureName(feature), 
          feature 
        }));
        
        console.log("将要生成的图表:", this.multipleCharts);
        
        // 使用setTimeout确保DOM已完全更新
        setTimeout(() => {
          this.initCategoryCharts(features);
        }, 300);
        
        console.log("类别特征分布图生成完成");
      } catch (error) {
        console.error("生成类别特征分布图时出错:", error);
        this.error = `生成图表错误: ${error.message}`;
      }
    },
    
    // 初始化类别图表（分离为单独的方法）
    initCategoryCharts(features) {
      console.log("开始初始化类别图表");
      
      features.forEach((feature, index) => {
        try {
          console.log(`初始化 ${feature} 图表`);
          
          // 通过ID选择DOM元素，而不是ref
          const chartDom = document.getElementById(`subChart${index}`);
          
          if (!chartDom) {
            console.error(`找不到ID为subChart${index}的DOM元素`);
            return;
          }
          
          console.log(`获取到DOM元素:`, chartDom);
          
          // 确保DOM元素尺寸
          if (chartDom.clientWidth === 0 || chartDom.clientHeight === 0) {
            console.error(`图表容器尺寸为0: width=${chartDom.clientWidth}, height=${chartDom.clientHeight}`);
            chartDom.style.width = '100%';
            chartDom.style.height = '250px';
          }
          
          const chart = echarts.init(chartDom);
          this.multipleChartsInstances.push(chart);
          
          // 计算特征分布
          const distribution = this.calculateCategoryDistribution(feature);
          console.log(`${feature} 分布数据:`, distribution);
          
          if (distribution.length === 0) {
            console.error(`${feature} 没有有效的分布数据`);
            return;
          }
          
          // 配置图表
          const option = {
            title: {
              text: this.getFeatureName(feature),
              left: 'center',
              textStyle: {
                fontSize: 14
              }
            },
            tooltip: {
              trigger: 'item',
              formatter: '{b}: {c} ({d}%)'
            },
            series: [
              {
                name: feature,
                type: 'pie',
                radius: '70%',
                data: distribution.map(item => ({
                  name: item.category,
                  value: item.count
                })),
                emphasis: {
                  itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                  }
                }
              }
            ]
          };
          
          chart.setOption(option);
          console.log(`${feature} 图表已设置`);
          
          // 自适应大小
          window.addEventListener('resize', () => {
            chart.resize();
          });
        } catch (err) {
          console.error(`初始化 ${feature} 图表时出错:`, err);
          this.error = `生成 ${this.getFeatureName(feature)} 图表错误: ${err.message}`;
        }
      });
    },
    
    // 计算类别特征的分布
    calculateCategoryDistribution(feature) {
      // 获取有效数据
      const validData = this.fullData.filter(item => item[feature] !== undefined && item[feature] !== null);
      
      // 统计每个类别的数量
      const counts = {};
      validData.forEach(item => {
        const category = item[feature];
        counts[category] = (counts[category] || 0) + 1;
      });
      
      // 转换为数组格式
      const distribution = Object.entries(counts).map(([category, count]) => ({
        category,
        count
      }));
      
      // 按数量排序（从大到小）
      distribution.sort((a, b) => b.count - a.count);
      
      return distribution;
    },
    
    // 获取特征的中文名称
    getFeatureName(feature) {
      const nameMap = {
        'MSZoning': '区域用途分类',
        'LotShape': '地块形状',
        'HouseStyle': '房屋风格',
        'OverallQual': '整体质量',
        'SalePrice': '销售价格',
        'Neighborhood': '社区'
      };
      
      return nameMap[feature] || feature;
    },
    
    // 计算百分位数
    percentile(data, p) {
      if (data.length === 0) return 0;
      
      // 排序数据
      const sorted = [...data].sort((a, b) => a - b);
      
      // 计算位置
      const position = (sorted.length - 1) * p / 100;
      const base = Math.floor(position);
      const rest = position - base;
      
      // 插值
      if (sorted[base + 1] !== undefined) {
        return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
      } else {
        return sorted[base];
      }
    }
  },
  created() {
    this.fetchDataset();
  }
};
</script>

<style scoped>
.data-visualization {
  padding: 0;
}

.btn-group .btn {
  margin-right: 8px;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: none;
  margin-bottom: 20px;
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
  padding: 0.75rem 1.25rem;
}

.card-body {
  padding: 1.25rem;
}

.category-chart-card {
  margin-bottom: 10px;
}

.category-chart-card .card-body {
  padding: 0.5rem;
}
</style> 