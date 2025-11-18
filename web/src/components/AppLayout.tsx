import { Link, Outlet, useLocation } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import type { MenuProps } from 'antd'
import Logo from './Logo'

const { Header, Content, Footer } = Layout

const menuItems: MenuProps['items'] = [
  { key: '/', label: <Link to="/">Star Map</Link> },
  { key: '/list', label: <Link to="/list">Task List</Link> },
]

function resolveSelectedKey(pathname: string): string {
  if (pathname.startsWith('/list')) {
    return '/list'
  }
  return '/'
}

const AppLayout = () => {
  const location = useLocation()
  const selectedKey = resolveSelectedKey(location.pathname)

  return (
    <Layout className="app-shell">
      <Header className="app-header">
        <Link to="/" className="brand" aria-label="TideScope navigation">
          <Logo height={32} />
        </Link>
        <Menu
          mode="horizontal"
          selectedKeys={[selectedKey]}
          items={menuItems}
          className="app-menu"
        />
      </Header>
      <Content className="app-content">
        <Outlet />
      </Content>
      <Footer className="app-footer">Project Task StarMap · Stage 3 Demo</Footer>
    </Layout>
  )
}

export default AppLayout
