/** 页面级加载骨架屏，用于 Suspense fallback */
export function PageSkeleton() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* 导航栏骨架 */}
      <div className="bg-white border-b border-gray-200 h-14" />
      <div className="max-w-6xl mx-auto px-4 py-8 space-y-4">
        {/* 标题骨架 */}
        <div className="h-7 w-48 bg-gray-200 rounded-lg animate-pulse" />
        {/* 内容卡片骨架 */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
              <div className="h-4 bg-gray-200 rounded animate-pulse" style={{ width: `${30 + i * 10}%` }} />
              <div className="h-6 w-20 bg-gray-200 rounded animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
