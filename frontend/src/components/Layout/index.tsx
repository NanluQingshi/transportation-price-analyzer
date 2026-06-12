import { NavLink } from 'react-router-dom'
import type { ReactNode } from 'react'

export interface LayoutProps {
  children: ReactNode
}

const navItems = [
  { to: '/', label: '每日汇总' },
  { to: '/search', label: '搜索机票' },
  { to: '/trends', label: '价格趋势' },
  { to: '/chat', label: '智能分析' },
]

/** 全局页面布局，包含顶部导航栏 */
export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 flex items-center h-14 gap-6">
          <span className="font-semibold text-blue-600 text-lg shrink-0">机票分析</span>
          <div className="flex gap-1">
            {navItems.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
          </div>
        </div>
      </nav>
      <main className="max-w-6xl mx-auto px-4 py-8">{children}</main>
    </div>
  )
}
