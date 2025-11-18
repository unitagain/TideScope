interface LogoProps {
  height?: number
  className?: string
}

const Logo = ({ height = 36, className = '' }: LogoProps) => {
  return (
    <svg
      width={height * 3.75}
      height={height}
      viewBox="0 0 300 80"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        {/* 主渐变：蓝紫粉 */}
        <linearGradient id="tideScopeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style={{ stopColor: '#3b82f6', stopOpacity: 1 }} />
          <stop offset="50%" style={{ stopColor: '#8b5cf6', stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: '#ec4899', stopOpacity: 1 }} />
        </linearGradient>
        
        {/* 发光效果 */}
        <filter id="logoGlow">
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      {/* TideScope 文字 */}
      <text
        x="150"
        y="50"
        fontFamily="'Inter', 'SF Pro Display', -apple-system, system-ui, sans-serif"
        fontSize="42"
        fontWeight="700"
        textAnchor="middle"
        fill="url(#tideScopeGradient)"
        filter="url(#logoGlow)"
        letterSpacing="-0.02em"
      >
        TideScope
      </text>
      
      {/* 装饰点 (动画) */}
      <circle cx="290" cy="45" r="3" fill="#3b82f6" opacity="0.8">
        <animate
          attributeName="opacity"
          values="0.4;1;0.4"
          dur="2s"
          repeatCount="indefinite"
        />
      </circle>
    </svg>
  )
}

export default Logo
