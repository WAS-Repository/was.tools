# eDEX-UI Svelte Implementation

This is a Svelte implementation of the eDEX-UI interface, a sci-fi inspired desktop environment reminiscent of DECTerm and the TRON legacy movie effects.

## Features

- Futuristic UI with terminal integration
- File explorer
- System information displays
- Virtual keyboard
- Document modal system
- Network monitoring
- Responsive design that works on desktop and mobile

## Setup and Building

### Prerequisites

- Node.js (v14 or later recommended)
- npm

### Installation

1. Clone the repository:
```bash
git clone https://github.com/GitSquared/edex-ui.git
cd edex-ui
```

2. Install dependencies:
```bash
npm install
cd src
npm install
cd ..
```

### Running the Application

#### Development Mode

To run the application in development mode with Svelte hot reloading:

```bash
npm run dev
```

#### Production Build

To build the application for production:

```bash
npm run build
```

### Using the Svelte Version

The Svelte implementation uses the same CSS and assets as the original eDEX-UI but replaces the HTML/JS implementation with Svelte components.

To switch between the original version and the Svelte version, you can:

1. Use the original entry point: `src/ui.html`
2. Use the Svelte entry point: `src/ui_svelte.html`

## Implementation Details

The Svelte application is structured with the following components:

- **app.svelte**: Main application container
- **Statusbar.svelte**: System information and keyboard
- **FileExplorer.svelte**: File browsing interface
- **documentsmodal.svelte**: Document selection and knowledge graph

## Contributors

This Svelte implementation was developed as an alternative frontend to the original eDEX-UI created by Gabriel 'Squared' SAILLARD. 