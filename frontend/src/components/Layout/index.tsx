import { useState } from 'react'
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
  { to: '/routes', label: '关注航线' },
]

function NavItem({ to, label, onClick }: { to: string; label: string; onClick?: () => void }) {
  return (
    <NavLink
      to={to}
      end={to === '/'}
      onClick={onClick}
      className={({ isActive }) =>
        `block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
          isActive
            ? 'bg-blue-50 text-blue-600'
            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
        }`
      }
    >
      {label}
    </NavLink>
  )
}

/** 全局页面布局，包含顶部导航栏（桌面横排 / 移动端汉堡菜单） */
export function Layout({ children }: LayoutProps) {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 relative z-10">
        <div className="max-w-6xl mx-auto px-4 flex items-center justify-between h-14">
          <span className="font-semibold text-blue-600 text-lg">机票分析</span>

          {/* 桌面导航 */}
          <div className="hidden sm:flex gap-1">
            {navItems.map(({ to, label }) => (
              <NavItem key={to} to={to} label={label} />
            ))}
          </div>

          {/* 移动端汉堡按钮 */}
          <button
            className="sm:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
            onClick={() => setMenuOpen((v) => !v)}
            aria-label={menuOpen ? '关闭菜单' : '打开菜单'}
          >
            {menuOpen ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>

        {/* 移动端下拉菜单 */}
        {menuOpen && (
          <div className="sm:hidden border-t border-gray-100 px-4 py-2 flex flex-col gap-1 bg-white shadow-lg">
            {navItems.map(({ to, label }) => (
              <NavItem key={to} to={to} label={label} onClick={() => setMenuOpen(false)} />
            ))}
          </div>
        )}
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-6 sm:py-8">{children}</main>
    </div>
  )
}
