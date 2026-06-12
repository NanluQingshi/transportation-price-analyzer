import type { FlightOffer } from '@/types/flight'

export interface FlightCardProps {
  offer: FlightOffer
}

function formatDuration(minutes: number): string {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h${m > 0 ? ` ${m}m` : ''}` : `${m}m`
}

/** 单个航班报价卡片 */
export function FlightCard({ offer }: FlightCardProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 flex items-center justify-between hover:shadow-md transition-shadow">
      <div className="flex items-center gap-6">
        <div className="text-center w-12">
          <p className="text-xs text-gray-400">{offer.airline_code}</p>
          <p className="text-sm font-medium text-gray-700">{offer.flight_number}</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-center">
            <p className="text-xl font-bold text-gray-900">{offer.departure_time}</p>
            <p className="text-xs text-gray-400">{offer.origin}</p>
          </div>
          <div className="flex flex-col items-center gap-0.5 px-2">
            <p className="text-xs text-gray-400">{formatDuration(offer.duration_minutes)}</p>
            <div className="w-20 h-px bg-gray-300 relative">
              <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-gray-400 rounded-full" />
            </div>
            <p className="text-xs text-gray-400">{offer.cabin_class}</p>
          </div>
          <div className="text-center">
            <p className="text-xl font-bold text-gray-900">{offer.arrival_time}</p>
            <p className="text-xs text-gray-400">{offer.destination}</p>
          </div>
        </div>
      </div>
      <div className="text-right">
        <p className="text-2xl font-bold text-blue-600">
          ¥{offer.price.toLocaleString('zh-CN', { maximumFractionDigits: 0 })}
        </p>
        <p className="text-xs text-gray-400 mt-0.5">{offer.source}</p>
      </div>
    </div>
  )
}
