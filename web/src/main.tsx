import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import 'antd/dist/reset.css'

import AppLayout from './components/AppLayout'
import ListPage from './pages/ListPage'
import StarMapPage from './pages/StarMapPage'
import './style.css'

const rootElement = document.getElementById('app') as HTMLElement

ReactDOM.createRoot(rootElement).render(
  // Temporarily disable StrictMode to avoid echarts-for-react ResizeObserver bug in dev
  // <React.StrictMode>
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#177ddc',
          borderRadius: 8,
          fontFamily: `"Inter", "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif`,
        },
      }}
    >
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<StarMapPage />} />
            <Route path="list" element={<ListPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  // </React.StrictMode>,
)
