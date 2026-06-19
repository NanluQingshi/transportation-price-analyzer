import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Layout } from './index'

function renderLayout(children = <div>内容</div>) {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <Layout>{children}</Layout>
    </MemoryRouter>,
  )
}

describe('Layout', () => {
  it('renders logo', () => {
    renderLayout()
    expect(screen.getByText('机票分析')).toBeInTheDocument()
  })

  it('renders all nav items', () => {
    renderLayout()
    const navLabels = ['每日汇总', '搜索机票', '价格趋势', '智能分析', '关注航线', '价格提醒']
    navLabels.forEach((label) => {
      expect(screen.getAllByText(label).length).toBeGreaterThan(0)
    })
  })

  it('renders children content', () => {
    renderLayout(<p>测试内容</p>)
    expect(screen.getByText('测试内容')).toBeInTheDocument()
  })

  it('shows mobile hamburger button', () => {
    renderLayout()
    const btn = screen.getByRole('button', { name: /打开菜单|关闭菜单/ })
    expect(btn).toBeInTheDocument()
  })

  it('toggles mobile menu on hamburger click', () => {
    renderLayout()
    // 初始时桌面导航存在
    const hamburger = screen.getByRole('button', { name: '打开菜单' })

    // 点击后菜单展开，按钮文案变为"关闭菜单"
    fireEvent.click(hamburger)
    expect(screen.getByRole('button', { name: '关闭菜单' })).toBeInTheDocument()

    // 再次点击关闭
    fireEvent.click(screen.getByRole('button', { name: '关闭菜单' }))
    expect(screen.getByRole('button', { name: '打开菜单' })).toBeInTheDocument()
  })
})
