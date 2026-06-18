import type { ComponentType } from 'react'
import { lazy, Suspense } from 'react'
import { createBrowserRouter } from 'react-router-dom'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { PageSkeleton } from '@/components/PageSkeleton'

const DashboardPage = lazy(() => import('@/pages/dashboard'))
const SearchPage = lazy(() => import('@/pages/search'))
const TrendsPage = lazy(() => import('@/pages/trends'))
const ChatPage = lazy(() => import('@/pages/chat'))
const RoutesPage = lazy(() => import('@/pages/routes'))

function wrap(Page: ComponentType) {
  return (
    <ErrorBoundary>
      <Suspense fallback={<PageSkeleton />}>
        <Page />
      </Suspense>
    </ErrorBoundary>
  )
}

export const router = createBrowserRouter([
  { path: '/', element: wrap(DashboardPage) },
  { path: '/search', element: wrap(SearchPage) },
  { path: '/trends', element: wrap(TrendsPage) },
  { path: '/chat', element: wrap(ChatPage) },
  { path: '/routes', element: wrap(RoutesPage) },
])
