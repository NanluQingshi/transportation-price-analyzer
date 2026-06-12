import { useEffect, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { searchAirports } from '@/services/searchApi'

export interface AirportInputProps {
  /** 输入框标签文字 */
  label: string
  value: string
  onChange: (iata: string, label: string) => void
  placeholder?: string
}

/** 机场搜索输入框，支持 IATA 代码和城市名自动补全 */
export function AirportInput({ label, value, onChange, placeholder }: AirportInputProps) {
  const [inputText, setInputText] = useState(value)
  const [open, setOpen] = useState(false)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const [query, setQuery] = useState('')
  const wrapperRef = useRef<HTMLDivElement>(null)

  const { data, isFetching } = useQuery({
    queryKey: ['airports', query],
    queryFn: () => searchAirports(query),
    enabled: query.length >= 2,
    staleTime: 1000 * 60 * 10,
  })

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const handleInput = (text: string) => {
    setInputText(text)
    setOpen(true)
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => setQuery(text), 300)
  }

  const handleSelect = (iata: string, city: string, name: string) => {
    const display = `${city} (${iata})`
    setInputText(display)
    setOpen(false)
    onChange(iata, display)
  }

  return (
    <div ref={wrapperRef} className="relative flex flex-col gap-1">
      <label className="text-sm font-medium text-gray-700">{label}</label>
      <input
        type="text"
        value={inputText}
        onChange={(e) => handleInput(e.target.value)}
        onFocus={() => query.length >= 2 && setOpen(true)}
        placeholder={placeholder ?? '城市或机场代码'}
        className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
      {open && (
        <ul className="absolute z-20 top-full mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-56 overflow-auto">
          {isFetching && (
            <li className="px-3 py-2 text-sm text-gray-400">搜索中…</li>
          )}
          {!isFetching && data?.length === 0 && (
            <li className="px-3 py-2 text-sm text-gray-400">未找到机场</li>
          )}
          {data?.map((airport) => (
            <li
              key={airport.iata}
              onMouseDown={() => handleSelect(airport.iata, airport.city, airport.name)}
              className="px-3 py-2 text-sm cursor-pointer hover:bg-blue-50 flex justify-between items-center"
            >
              <span>
                <span className="font-medium">{airport.city}</span>
                <span className="text-gray-400 ml-1">{airport.name}</span>
              </span>
              <span className="text-blue-600 font-mono text-xs">{airport.iata}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
