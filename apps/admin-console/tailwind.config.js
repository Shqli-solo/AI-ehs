/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // 响应式断点定义
      screens: {
        'mobile': {'max': '639px'},
        'tablet': {'min': '640px', 'max': '1024px'},
        'desktop': {'min': '1025px'},
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
      // 颜色系统（Design Tokens）
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        // 主色
        primary: {
          DEFAULT: "#1890ff",
          foreground: "#ffffff",
          hover: "#40a9ff",
          active: "#096dd9",
        },
        // 成功
        success: {
          DEFAULT: "#52c41a",
          foreground: "#ffffff",
        },
        // 警告
        warning: {
          DEFAULT: "#fa8c16",
          foreground: "#ffffff",
        },
        // 错误
        error: {
          DEFAULT: "#ff4d4f",
          foreground: "#ffffff",
        },
        // 中性色
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      // 字体规范
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          '"Noto Sans"',
          'sans-serif',
        ],
      },
      fontSize: {
        // 大标题
        'title-lg': ['20px', { lineHeight: '1.4', fontWeight: '600' }],
        // 小标题
        'title': ['16px', { lineHeight: '1.5', fontWeight: '600' }],
        // 正文
        'body': ['14px', { lineHeight: '1.5', fontWeight: '400' }],
        // 辅助文字
        'caption': ['13px', { lineHeight: '1.5', fontWeight: '400' }],
      },
      // 间距系统（以 4px 为基准）
      spacing: {
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px',
      },
      // 圆角规范
      borderRadius: {
        'card': '8px',
        'button': '6px',
        'input': '6px',
        'badge': '12px',
        lg: '8px',
        md: '6px',
        full: '9999px',
      },
      // 阴影规范
      boxShadow: {
        card: '0 1px 3px rgba(0,0,0,0.1)',
        'card-hover': '0 4px 12px rgba(24,144,255,0.2)',
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  plugins: [],
};
