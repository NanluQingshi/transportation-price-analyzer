import { useQuery } from '@tanstack/react-query'
import { fetchTrends } from '@/services/trendsApi'

export function usePriceTrends(
  origin: string,
  destination: string,
  days: 30 | 90 | 180,
) {
  return useQuery({
    queryKey: ['trends', origin, destination, days],
    queryFn: () => fetchTrends(origin, destination, days),
    enabled: origin.length === 3 && destination.length === 3,
    staleTime: 1000 * 60 * 10,
  })
}
