# eDEX-UI Web Version

This is a modified version of the eDEX-UI project that has been converted to run as a web application without Electron dependencies.

## Prerequisites

- Node.js (v14 or later recommended)
- npm (comes with Node.js)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/WAS-Repository/was.tools.git
   cd was.tools
   ```

2. Install dependencies:
   ```
   cd edex-ui
   npm run install-deps
   ```

3. Build the Svelte components:
   ```
   npm run svelte-build
   ```

4. Start the application:
   ```
   npm run start
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

## Development

For development with live reloading:
```
npm run svelte-dev
```

## Features

- Sci-fi inspired terminal interface
- File explorer
- System information displays
- Customizable themes

## License

GPL-3.0 