import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Layout } from '@/components/Layout'
import { AirportInput } from '@/components/AirportInput'
import { Spinner } from '@/components/Spinner'
import { createRoute, deleteRoute, fetchRoutes } from '@/services/routesApi'
import type { RouteResponse } from '@/types/routes'

function RouteRow({
  route,
  onDelete,
  isDeleting,
}: {
  route: RouteResponse
  onDelete: (id: number) => void
  isDeleting: boolean
}) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
      <div className="flex items-center gap-3">
        <span
          className={`w-2 h-2 rounded-full shrink-0 ${route.is_active ? 'bg-green-400' : 'bg-gray-300'}`}
        />
        <span className="font-mono text-sm font-medium text-gray-800">
          {route.origin} → {route.destination}
        </span>
        {!route.is_active && (
          <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
            已停用
          </span>
        )}
      </div>
      <button
        onClick={() => onDelete(route.id)}
        disabled={isDeleting || !route.is_active}
        className="text-sm text-red-400 hover:text-red-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors px-2 py-1"
      >
        删除
      </button>
    </div>
  )
}

export default function RoutesPage() {
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [originLabel, setOriginLabel] = useState('')
  const [destinationLabel, setDestinationLabel] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data: routes = [], isLoading } = useQuery({
    queryKey: ['routes'],
    queryFn: fetchRoutes,
  })

  const createMutation = useMutation({
    mutationFn: () => createRoute(origin, destination),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['routes'] })
      void queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      setOrigin('')
      setDestination('')
      setOriginLabel('')
      setDestinationLabel('')
      setFormError(null)
    },
    onError: (err: Error) => setFormError(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteRoute(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['routes'] })
      void queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })

  const handleAdd = () => {
    if (!origin || !destination) {
      setFormError('请选择出发地和目的地')
      return
    }
    if (origin === destination) {
      setFormError('出发地和目的地不能相同')
      return
    }
    setFormError(null)
    createMutation.mutate()
  }

  const activeCount = routes.filter((r) => r.is_active).length

  return (
    <Layout>
      <div className="max-w-2xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">关注航线管理</h1>
            <p className="text-sm text-gray-400 mt-1">
              定时任务每天 01:00 自动抓取关注航线的价格快照
            </p>
          </div>
          <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
            {activeCount} 条启用中
          </span>
        </div>

        {/* 新增表单 */}
        <div className="bg-white border border-gray-200 rounded-xl p-5 mb-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">添加航线</h2>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <AirportInput
              label="出发地"
              value={originLabel}
              onChange={(iata, label) => { setOrigin(iata); setOriginLabel(label) }}
              placeholder="城市或机场代码"
            />
            <AirportInput
              label="目的地"
              value={destinationLabel}
              onChange={(iata, label) => { setDestination(iata); setDestinationLabel(label) }}
              placeholder="城市或机场代码"
            />
          </div>
          {formError && (
            <p className="text-sm text-red-500 mb-3">{formError}</p>
          )}
          <button
            onClick={handleAdd}
            disabled={createMutation.isPending || !origin || !destination}
            className="w-full py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {createMutation.isPending ? '添加中…' : '添加航线'}
          </button>
        </div>

        {/* 航线列表 */}
        <div className="bg-white border border-gray-200 rounded-xl px-5">
          {isLoading && (
            <div className="py-12 flex justify-center">
              <Spinner />
            </div>
          )}
          {!isLoading && routes.length === 0 && (
            <div className="py-12 text-center text-gray-400 text-sm">
              还没有关注任何航线，添加一条开始吧
            </div>
          )}
          {routes.map((route) => (
            <RouteRow
              key={route.id}
              route={route}
              onDelete={(id) => deleteMutation.mutate(id)}
              isDeleting={deleteMutation.isPending}
            />
          ))}
        </div>
      </div>
    </Layout>
  )
}
