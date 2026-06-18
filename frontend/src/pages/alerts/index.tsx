import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Layout } from '@/components/Layout'
import { AirportInput } from '@/components/AirportInput'
import { Spinner } from '@/components/Spinner'
import { createAlert, deleteAlert, fetchAlerts } from '@/services/alertsApi'
import type { AlertResponse } from '@/types/alerts'

function AlertRow({
  alert,
  onDelete,
  isDeleting,
}: {
  alert: AlertResponse
  onDelete: (id: number) => void
  isDeleting: boolean
}) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
      <div className="flex items-center gap-3">
        <span
          className={`w-2 h-2 rounded-full shrink-0 ${alert.is_active ? 'bg-green-400' : 'bg-gray-300'}`}
        />
        <div>
          <p className="text-sm font-medium text-gray-800">
            <span className="font-mono">{alert.origin} → {alert.destination}</span>
            <span className="ml-2 text-blue-600 font-semibold">
              ≤ ¥{alert.target_price.toLocaleString('zh-CN', { maximumFractionDigits: 0 })}
            </span>
          </p>
          <p className="text-xs text-gray-400 mt-0.5 truncate max-w-xs">
            webhook: {alert.notify_target}
          </p>
          {alert.last_triggered_at && (
            <p className="text-xs text-green-500 mt-0.5">
              上次触发：{new Date(alert.last_triggered_at).toLocaleString('zh-CN')}
            </p>
          )}
        </div>
      </div>
      <button
        onClick={() => onDelete(alert.id)}
        disabled={isDeleting || !alert.is_active}
        className="text-sm text-red-400 hover:text-red-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors px-2 py-1 shrink-0"
      >
        删除
      </button>
    </div>
  )
}

export default function AlertsPage() {
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [targetPrice, setTargetPrice] = useState('')
  const [webhookUrl, setWebhookUrl] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data: alerts = [], isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: fetchAlerts,
  })

  const createMutation = useMutation({
    mutationFn: () =>
      createAlert({
        origin,
        destination,
        target_price: Number(targetPrice),
        notify_channel: 'webhook',
        notify_target: webhookUrl,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['alerts'] })
      setOrigin('')
      setDestination('')
      setTargetPrice('')
      setWebhookUrl('')
      setFormError(null)
    },
    onError: (err: Error) => setFormError(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteAlert(id),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  })

  const handleAdd = () => {
    if (!origin || !destination) { setFormError('请选择出发地和目的地'); return }
    if (!targetPrice || Number(targetPrice) <= 0) { setFormError('请输入有效的目标价格'); return }
    if (!webhookUrl.startsWith('http')) { setFormError('请输入有效的 Webhook URL'); return }
    setFormError(null)
    createMutation.mutate()
  }

  const activeCount = alerts.filter((a) => a.is_active).length

  return (
    <Layout>
      <div className="max-w-2xl">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-2xl font-bold text-gray-900">价格提醒</h1>
          <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
            {activeCount} 条启用中
          </span>
        </div>
        <p className="text-sm text-gray-400 mb-6">
          当关注航线最低价低于目标价时，自动推送 Webhook 通知（支持飞书/企微/Slack）
        </p>

        {/* 新增表单 */}
        <div className="bg-white border border-gray-200 rounded-xl p-5 mb-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">添加提醒</h2>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <AirportInput
              label="出发地"
              value=""
              onChange={(iata) => setOrigin(iata)}
            />
            <AirportInput
              label="目的地"
              value=""
              onChange={(iata) => setDestination(iata)}
            />
          </div>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium text-gray-700">目标价格（¥）</label>
              <input
                type="number"
                min={1}
                value={targetPrice}
                onChange={(e) => setTargetPrice(e.target.value)}
                placeholder="例如 500"
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium text-gray-700">Webhook URL</label>
              <input
                type="url"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                placeholder="https://..."
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          {formError && <p className="text-sm text-red-500 mb-3">{formError}</p>}
          <button
            onClick={handleAdd}
            disabled={createMutation.isPending}
            className="w-full py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {createMutation.isPending && <Spinner size="sm" className="border-white border-t-blue-200" />}
            {createMutation.isPending ? '添加中…' : '添加提醒'}
          </button>
        </div>

        {/* 提醒列表 */}
        <div className="bg-white border border-gray-200 rounded-xl px-5">
          {isLoading && (
            <div className="py-12 flex justify-center"><Spinner /></div>
          )}
          {!isLoading && alerts.length === 0 && (
            <div className="py-12 text-center text-gray-400 text-sm">
              还没有价格提醒，添加一条开始吧
            </div>
          )}
          {alerts.map((alert) => (
            <AlertRow
              key={alert.id}
              alert={alert}
              onDelete={(id) => deleteMutation.mutate(id)}
              isDeleting={deleteMutation.isPending}
            />
          ))}
        </div>

        {/* Webhook 说明 */}
        <div className="mt-4 p-4 bg-blue-50 rounded-xl text-xs text-blue-700 space-y-1">
          <p className="font-medium">Webhook 推送格式（POST JSON）</p>
          <p className="font-mono text-blue-500 break-all">
            {`{ "type": "price_alert", "origin": "PEK", "destination": "SHA", "target_price": 500, "current_price": 480, "message": "..." }`}
          </p>
          <p className="text-blue-500">飞书/企微机器人 Webhook 可直接填入，24 小时内同一提醒只推送一次。</p>
        </div>
      </div>
    </Layout>
  )
}
