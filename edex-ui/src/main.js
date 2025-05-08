import App from './components/app.svelte';

// Import global CSS files
import './assets/css/root.css';
import './assets/css/main_shell.css';
import './assets/css/filesystem.css';
import './assets/css/keyboard.css';
import './assets/css/modal.css';
import './assets/css/mod_column.css';
import './assets/css/mod_clock.css';
import './assets/css/mod_sysinfo.css';
import './assets/css/mod_hardwareInspector.css';
import './assets/css/mod_cpuinfo.css';
import './assets/css/mod_netstat.css';
import './assets/css/mod_conninfo.css';
import './assets/css/mod_globe.css';
import './assets/css/mod_ramwatcher.css';
import './assets/css/mod_toplist.css';
import './assets/css/mod_fuzzyFinder.css';
import './assets/css/mod_processlist.css';
import './assets/css/extra_ratios.css';

// Import Leaflet (we'll load it dynamically in the component instead to avoid Electron issues)
// import 'leaflet/dist/leaflet.css';

const app = new App({
  target: document.body
});

export default app; 