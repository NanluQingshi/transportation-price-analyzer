import axios from 'axios'

export const apiClient = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

apiClient.interceptors.response.use(
  (res) => res,
  (err: unknown) => {
    if (axios.isAxiosError(err)) {
      const msg = (err.response?.data as { detail?: string } | undefined)?.detail ?? err.message
      return Promise.reject(new Error(msg))
    }
    return Promise.reject(err)
  },
)
