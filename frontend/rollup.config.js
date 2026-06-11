import { nodeResolve } from '@rollup/plugin-node-resolve'
import commonjs from '@rollup/plugin-commonjs'
import replace from '@rollup/plugin-replace'
import typescript from '@rollup/plugin-typescript'
import postcss from 'rollup-plugin-postcss'

const isDev = process.env.NODE_ENV !== 'production'

export default {
  input: 'src/main.tsx',
  output: {
    dir: 'dist',
    format: 'esm',
    sourcemap: isDev,
    chunkFileNames: '[name]-[hash].js',
  },
  plugins: [
    replace({
      preventAssignment: true,
      'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV ?? 'development'),
    }),
    nodeResolve({ browser: true, extensions: ['.ts', '.tsx', '.js', '.jsx'] }),
    commonjs(),
    typescript({ tsconfig: './tsconfig.json', noEmitOnError: !isDev }),
    postcss({
      config: { path: './postcss.config.js' },
      extract: 'bundle.css',
      minimize: !isDev,
      modules: { generateScopedName: isDev ? '[name]__[local]' : '[hash:base64:6]' },
    }),
  ],
}
