import { createBrowserRouter } from 'react-router-dom'
import { lazy, Suspense } from 'react'

const DashboardPage = lazy(() => import('@/pages/dashboard'))
const SearchPage = lazy(() => import('@/pages/search'))
const TrendsPage = lazy(() => import('@/pages/trends'))
const ChatPage = lazy(() => import('@/pages/chat'))

export const router = createBrowserRouter([
  { path: '/', element: <Suspense fallback={null}><DashboardPage /></Suspense> },
  { path: '/search', element: <Suspense fallback={null}><SearchPage /></Suspense> },
  { path: '/trends', element: <Suspense fallback={null}><TrendsPage /></Suspense> },
  { path: '/chat', element: <Suspense fallback={null}><ChatPage /></Suspense> },
])
