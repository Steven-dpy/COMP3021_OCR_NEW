const { createProxyMiddleware } = require('http-proxy-middleware')

module.exports = function (app) {
  // 代理1：指向用户服务API
  app.use(
    '/api/', // 前端请求前缀
    createProxyMiddleware({
      target: 'http://localhost:8000/api/', // 后端服务1地址
      changeOrigin: true, // 解决跨域问题（重要）
      // 可选：重写路径（如果后端接口没有/users前缀）
      // pathRewrite: { '^/api/users': '/users' }
    })
  )
}
