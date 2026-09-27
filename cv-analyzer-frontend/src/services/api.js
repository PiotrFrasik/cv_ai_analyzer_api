import axios from 'axios'
// base prefix
const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api'
})

// Add token JWT for request if exists
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

export default api


