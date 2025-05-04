/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      keyframes: {
        spin: {
          '0%': {transform: 'rotate(0deg)'},
          '100%': {transform: 'rotate(360deg)'}
        }
      },
      height: {
        'navbar': '4.5rem'
      },
      width: {
        'sidebar': '6rem',
        'sidebar-expanded': '16rem'
      },
      fontSize: {
        'xxs': '0.60rem'
      },
      backgroundPosition: {
        '0': '0% 0%',
        '100': '100% 100%'
      },
      colors: {
        'navbar': {
          DEFAULT: '#000000',
          dark: '#000000',
          hover: '#a1a1aa',
          'hover-dark': '#a1a1aa',
          text: '#d4d4d8',
          'text-dark': '#d4d4d8'
        },
        'app': {
          DEFAULT: '#e5e7eb',
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          dark: '#09090b',
          'dark-50': '#18181b',
          'dark-100': '#27272a',
          'dark-200': '#3f3f46',
          'dark-300': '#52525b',
          'dark-400': '#71717a',
          'dark-500': '#a1a1aa',
          hover: '#d4d4d8',
          'hover-dark': '#27272a',
          text: '#09090b',
          'text-dark': '#fafafa',
          'text-secondary': '#6b7280',
          'text-secondary-dark': '#a1a1aa'
        },
        'primary': {
          DEFAULT: '#8B5CF6',
          50: '#F5F3FF',
          100: '#EDE9FE',
          200: '#DDD6FE',
          300: '#C4B5FD',
          400: '#A78BFA',
          500: '#8B5CF6',
          600: '#7C3AED',
          700: '#6D28D9',
          800: '#5B21B6',
          900: '#4C1D95'
        },
        'secondary': '#5CF68B'
      }
    }
  },
  plugins: [],
}