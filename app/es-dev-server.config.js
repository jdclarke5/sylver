const proxy = require('koa-proxies');
 
module.exports = {
  port: 9000,  
  watch: true,
  nodeResolve: true,
  appIndex: "index.html",
  middlewares: [
    proxy("/api", {
      target: "http://localhost:5000",
    }),
  ],
  debug: true,
};