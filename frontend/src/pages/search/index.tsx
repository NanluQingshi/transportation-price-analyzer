import { useState } from 'react'
import { Layout } from '@/components/Layout'
import { AirportInput } from '@/components/AirportInput'
import { FlightCard } from '@/components/FlightCard'
import { Spinner } from '@/components/Spinner'
import { useFlightSearch } from './hooks/useFlightSearch'
import type { CabinClass } from '@/types/flight'

const CABIN_OPTIONS: { value: CabinClass; label: string }[] = [
  { value: 'ECONOMY', label: '经济舱' },
  { value: 'BUSINESS', label: '商务舱' },
  { value: 'FIRST', label: '头等舱' },
]

export default function SearchPage() {
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [departureDate, setDepartureDate] = useState('')
  const [returnDate, setReturnDate] = useState('')
  const [adults, setAdults] = useState(1)
  const [cabinClass, setCabinClass] = useState<CabinClass>('ECONOMY')
  const [sortBy, setSortBy] = useState<'price' | 'duration'>('price')

  const { search, results, cached, queryTimeMs, isLoading, error, hasSearched } = useFlightSearch()

  const handleSearch = () => {
    if (!origin || !destination || !departureDate) return
    const params = {
      origin,
      destination,
      departure_date: departureDate,
      adults,
      cabin_class: cabinClass,
      ...(returnDate ? { return_date: returnDate } : {}),
    }
    search(params)
  }

  const sorted = [...results].sort((a, b) =>
    sortBy === 'price' ? a.price - b.price : a.duration_minutes - b.duration_minutes,
  )

  return (
    <Layout>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">搜索机票</h1>

      {/* 搜索表单 */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          <AirportInput
            label="出发地"
            value=""
            onChange={(iata) => setOrigin(iata)}
            placeholder="城市或机场代码"
          />
          <AirportInput
            label="目的地"
            value=""
            onChange={(iata) => setDestination(iata)}
            placeholder="城市或机场代码"
          />
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-gray-700">出发日期</label>
            <input
              type="date"
              value={departureDate}
              onChange={(e) => setDepartureDate(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-gray-700">返程日期（可选）</label>
            <input
              type="date"
              value={returnDate}
              onChange={(e) => setReturnDate(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-gray-700">乘客人数</label>
            <input
              type="number"
              min={1}
              max={9}
              value={adults}
              onChange={(e) => setAdults(Number(e.target.value))}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-gray-700">舱位</label>
            <select
              value={cabinClass}
              onChange={(e) => setCabinClass(e.target.value as CabinClass)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {CABIN_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
        </div>
        <button
          onClick={handleSearch}
          disabled={isLoading || !origin || !destination || !departureDate}
          className="w-full sm:w-auto px-8 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {isLoading && <Spinner size="sm" className="border-white border-t-blue-200" />}
          {isLoading ? '搜索中…' : '搜索'}
        </button>
      </div>

      {/* 结果区 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm mb-4">
          {error}
        </div>
      )}

      {hasSearched && !error && (
        <>
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm text-gray-500">
              找到 {results.length} 个航班
              {cached ? '（缓存）' : `（${queryTimeMs}ms）`}
            </p>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">排序：</span>
              {(['price', 'duration'] as const).map((key) => (
                <button
                  key={key}
                  onClick={() => setSortBy(key)}
                  className={`text-sm px-3 py-1 rounded-lg transition-colors ${
                    sortBy === key
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  {key === 'price' ? '价格' : '时长'}
                </button>
              ))}
            </div>
          </div>
          <div className="flex flex-col gap-3">
            {sorted.map((offer) => (
              <FlightCard key={`${offer.flight_number}-${offer.departure_time}`} offer={offer} />
            ))}
            {sorted.length === 0 && (
              <div className="bg-white rounded-xl border border-gray-200 py-16 text-center text-gray-400 text-sm">
                未找到符合条件的航班
              </div>
            )}
          </div>
        </>
      )}
    </Layout>
  )
}
