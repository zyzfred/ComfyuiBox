export default {
  define: {
    __API_URL__: JSON.stringify(process.env.VITE_API_URL || 'http://localhost:8686')
  }
}