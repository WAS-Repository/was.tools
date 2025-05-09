import svelte from 'rollup-plugin-svelte';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import css from 'rollup-plugin-css-only';
import { terser } from 'rollup-plugin-terser';
import livereload from 'rollup-plugin-livereload';

const production = !process.env.ROLLUP_WATCH;

function serve() {
  let server;

  function toExit() {
    if (server) server.kill(0);
  }

  return {
    writeBundle() {
      if (server) return;
      server = require('child_process').spawn('npm', ['run', 'start'], {
        stdio: ['ignore', 'inherit', 'inherit'],
        shell: true
      });

      process.on('SIGTERM', toExit);
      process.on('exit', toExit);
    }
  };
}

export default {
  input: 'src/main.js',
  output: {
    sourcemap: !production,
    format: 'iife',
    name: 'app',
    file: 'src/build/bundle.js'
  },
  plugins: [
    svelte({
      compilerOptions: {
        // Enable run-time checks when not in production
        dev: !production
      }
    }),
    // Extract component CSS into a separate file
    css({ output: 'bundle.css' }),

    // If you have external dependencies installed from
    // npm, you'll most likely need these plugins.
    resolve({
      browser: true,
      dedupe: ['svelte']
    }),
    commonjs(),

    // In dev mode, call `npm run start` once
    // the bundle has been generated
    !production && serve(),

    // Watch the `src` directory and refresh the
    // browser on changes when not in production
    !production && livereload('src'),

    // Minify for production
    production && terser()
  ],
  watch: {
    clearScreen: false
  }
}; 