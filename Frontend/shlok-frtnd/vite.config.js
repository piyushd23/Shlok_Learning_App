import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from 'vite-plugin-tailwindcss'

// https://vite.dev/config/
export default defineConfig({
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
    theme: {
      extend: {},
    },
    plugins: [tailwindcss(),react()],
})
