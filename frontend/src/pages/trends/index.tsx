import { useState } from 'react'
import { Layout } from '@/components/Layout'
import { AirportInput } from '@/components/AirportInput'
import { PriceChart } from '@/components/PriceChart'
import { usePriceTrends } from './hooks/usePriceTrends'
import type { PriceStats } from '@/types/flight'

const DAYS_OPTIONS: { value: 30 | 90 | 180; label: string }[] = [
  { value: 30, label: '近30天' },
  { value: 90, label: '近90天' },
  { value: 180, label: '近180天' },
]

const PRICE_LEVEL_CONFIG: Record<
  PriceStats['price_level'],
  { label: string; cls: string }
> = {
  low: { label: '历史低位', cls: 'bg-green-100 text-green-700' },
  below_average: { label: '低于均价', cls: 'bg-green-50 text-green-600' },
  average: { label: '价格正常', cls: 'bg-gray-100 text-gray-600' },
  above_average: { label: '高于均价', cls: 'bg-orange-50 text-orange-600' },
  high: { label: '历史高位', cls: 'bg-red-100 text-red-700' },
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 text-center">
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className="text-lg font-bold text-gray-900">{value}</p>
    </div>
  )
}

export default function TrendsPage() {
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [days, setDays] = useState<30 | 90 | 180>(30)

  const { data, isLoading, isError } = usePriceTrends(origin, destination, days)

  const fmt = (n: number | null) =>
    n != null ? `¥${n.toLocaleString('zh-CN', { maximumFractionDigits: 0 })}` : '—'

  return (
    <Layout>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">价格趋势</h1>

      {/* 航线选择 */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 mb-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          <AirportInput label="出发地" value="" onChange={(iata) => setOrigin(iata)} />
          <AirportInput label="目的地" value="" onChange={(iata) => setDestination(iata)} />
        </div>
        <div className="flex gap-2">
          {DAYS_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setDays(opt.value)}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                days === opt.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* 统计卡片 */}
      {data && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          <StatCard label="历史最低" value={fmt(data.stats.historical_min)} />
          <StatCard label="历史均价" value={fmt(data.stats.historical_avg)} />
          <StatCard label="当前最低" value={fmt(data.stats.current_price)} />
          <div className="bg-white border border-gray-200 rounded-xl p-4 text-center">
            <p className="text-xs text-gray-400 mb-1">价格位置</p>
            {(() => {
              const cfg = PRICE_LEVEL_CONFIG[data.stats.price_level]
              return (
                <span className={`text-sm font-semibold px-2 py-0.5 rounded-full ${cfg.cls}`}>
                  {cfg.label}
                </span>
              )
            })()}
          </div>
        </div>
      )}

      {/* 图表 */}
      <div className="bg-white border border-gray-200 rounded-xl p-6">
        {!origin || !destination ? (
          <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
            请先选择出发地和目的地
          </div>
        ) : isLoading ? (
          <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
            加载中…
          </div>
        ) : isError ? (
          <div className="flex items-center justify-center h-64 text-red-400 text-sm">
            数据加载失败
          </div>
        ) : (
          <PriceChart data={data?.data_points ?? []} />
        )}
      </div>
    </Layout>
  )
}
