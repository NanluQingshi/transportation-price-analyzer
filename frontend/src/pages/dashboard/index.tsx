import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Layout } from '@/components/Layout'
import { Spinner } from '@/components/Spinner'
import { fetchDashboard } from '@/services/searchApi'
import type { RouteSummary } from '@/types/flight'

function TrendBadge({ trend }: { trend: RouteSummary['trend'] }) {
  const config = {
    up: { label: '↑ 涨', cls: 'bg-red-50 text-red-600' },
    down: { label: '↓ 跌', cls: 'bg-green-50 text-green-600' },
    stable: { label: '— 平', cls: 'bg-gray-100 text-gray-500' },
  }[trend]
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${config.cls}`}>
      {config.label}
    </span>
  )
}

function RouteRow({ route }: { route: RouteSummary }) {
  return (
    <div className="flex items-center justify-between py-4 border-b border-gray-100 last:border-0">
      <div>
        <p className="font-medium text-gray-900 text-sm sm:text-base">
          {route.origin_city || route.origin} → {route.destination_city || route.destination}
        </p>
        <p className="text-xs text-gray-400 mt-0.5">
          {route.origin} / {route.destination}
        </p>
      </div>
      <div className="flex items-center gap-3 sm:gap-4">
        <TrendBadge trend={route.trend} />
        <div className="text-right">
          <p className="text-base sm:text-lg font-bold text-gray-900">
            ¥{route.min_price.toLocaleString('zh-CN', { maximumFractionDigits: 0 })}
          </p>
          <p
            className={`text-xs mt-0.5 ${
              route.price_change > 0
                ? 'text-red-500'
                : route.price_change < 0
                  ? 'text-green-500'
                  : 'text-gray-400'
            }`}
          >
            {route.price_change > 0 ? '+' : ''}
            {route.price_change.toFixed(0)} ({route.price_change_pct > 0 ? '+' : ''}
            {route.price_change_pct.toFixed(1)}%)
          </p>
        </div>
      </div>
    </div>
  )
}

function EmptyGuide() {
  return (
    <div className="py-16 flex flex-col items-center gap-4 text-center">
      <div className="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center text-2xl">
        ✈️
      </div>
      <div>
        <p className="text-gray-700 font-medium">还没有价格数据</p>
        <p className="text-sm text-gray-400 mt-1">
          先添加关注航线，定时任务每天 01:00 自动抓取价格快照
        </p>
      </div>
      <div className="flex gap-3">
        <Link
          to="/routes"
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
        >
          添加关注航线
        </Link>
        <Link
          to="/search"
          className="px-4 py-2 border border-gray-200 text-gray-600 text-sm rounded-lg hover:bg-gray-50 transition-colors"
        >
          直接搜索
        </Link>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['dashboard'],
    queryFn: fetchDashboard,
    staleTime: 1000 * 60 * 5,
  })

  return (
    <Layout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">每日价格汇总</h1>
        {data && <p className="text-sm text-gray-400">{data.date}</p>}
      </div>

      <div className="bg-white rounded-xl border border-gray-200 px-6">
        {isLoading && (
          <div className="py-16 flex justify-center">
            <Spinner size="lg" />
          </div>
        )}
        {isError && (
          <div className="py-16 text-center text-red-400 text-sm">数据加载失败，请稍后重试</div>
        )}
        {!isLoading && !isError && data?.routes.length === 0 && <EmptyGuide />}
        {data?.routes.map((route) => (
          <RouteRow key={`${route.origin}-${route.destination}`} route={route} />
        ))}
      </div>
    </Layout>
  )
}
