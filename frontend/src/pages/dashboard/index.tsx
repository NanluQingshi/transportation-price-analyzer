import { useQuery } from '@tanstack/react-query'
import { Layout } from '@/components/Layout'
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
      <div className="flex items-center gap-3">
        <div>
          <p className="font-medium text-gray-900">
            {route.origin_city || route.origin} → {route.destination_city || route.destination}
          </p>
          <p className="text-xs text-gray-400 mt-0.5">
            {route.origin} / {route.destination}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <TrendBadge trend={route.trend} />
        <div className="text-right">
          <p className="text-lg font-bold text-gray-900">
            ¥{route.min_price.toLocaleString('zh-CN', { maximumFractionDigits: 0 })}
          </p>
          <p className={`text-xs mt-0.5 ${route.price_change > 0 ? 'text-red-500' : route.price_change < 0 ? 'text-green-500' : 'text-gray-400'}`}>
            {route.price_change > 0 ? '+' : ''}{route.price_change.toFixed(0)} ({route.price_change_pct > 0 ? '+' : ''}{route.price_change_pct.toFixed(1)}%)
          </p>
        </div>
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
        {data && (
          <p className="text-sm text-gray-400">{data.date}</p>
        )}
      </div>

      <div className="bg-white rounded-xl border border-gray-200 px-6">
        {isLoading && (
          <div className="py-16 text-center text-gray-400 text-sm">加载中…</div>
        )}
        {isError && (
          <div className="py-16 text-center text-red-400 text-sm">数据加载失败，请稍后重试</div>
        )}
        {data?.routes.length === 0 && (
          <div className="py-16 text-center text-gray-400 text-sm">
            暂无价格数据，等待定时任务抓取…
          </div>
        )}
        {data?.routes.map((route) => (
          <RouteRow key={`${route.origin}-${route.destination}`} route={route} />
        ))}
      </div>
    </Layout>
  )
}
