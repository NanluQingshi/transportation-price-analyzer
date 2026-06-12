import { useMutation } from '@tanstack/react-query'
import { searchFlights } from '@/services/searchApi'
import type { SearchParams, SearchResponse } from '@/types/flight'

export function useFlightSearch() {
  const mutation = useMutation<SearchResponse, Error, SearchParams>({
    mutationFn: searchFlights,
  })

  return {
    search: mutation.mutate,
    results: mutation.data?.results ?? [],
    cached: mutation.data?.cached ?? false,
    queryTimeMs: mutation.data?.query_time_ms ?? 0,
    isLoading: mutation.isPending,
    error: mutation.error?.message ?? null,
    hasSearched: mutation.isSuccess || mutation.isError,
  }
}
