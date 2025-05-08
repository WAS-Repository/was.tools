<script>
  import Statusbar from './Statusbar.svelte';
  import FileExplorer from './FileExplorer.svelte';
  import DocumentsModal from './documentsmodal.svelte';
  import { onMount } from 'svelte';
  
  // Import global CSS
  import './main.css';
  
  let tabs = [
    { id: 1, name: "fish", active: true },
    { id: 2, name: "htop", active: false },
    { id: 3, name: "EMPTY", active: false },
    { id: 4, name: "EMPTY", active: false }
  ];
  
  let activeDocument = "fish";
  let time = { hours: "18", minutes: "21", seconds: "37" };
  
  // Update the time every second
  onMount(() => {
    const interval = setInterval(() => {
      const now = new Date();
      time = {
        hours: now.getHours().toString().padStart(2, '0'),
        minutes: now.getMinutes().toString().padStart(2, '0'),
        seconds: now.getSeconds().toString().padStart(2, '0')
      };
    }, 1000);
    
    return () => clearInterval(interval);
  });
  
  function setActiveTab(id) {
    tabs = tabs.map(tab => ({
      ...tab,
      active: tab.id === id
    }));
    activeDocument = tabs.find(tab => tab.id === id).name;
  }
</script>

<div id="container">
  <div id="main">
    <!-- Terminal/Shell Section -->
    <section id="main_shell" data-augmented-ui="tl-clip tr-clip br-clip bl-clip border">
      <h3 class="title">
        <p id="main_shell_title">MAIN - {activeDocument}</p>
        <p id="main_shell_sysinfo"></p>
      </h3>
      
      <!-- Shell Tabs -->
      <ul id="main_shell_tabs">
        {#each tabs as tab}
          <li class={tab.active ? "active" : ""} on:click={() => setActiveTab(tab.id)}>
            <p>#{tab.id} - {tab.name}</p>
          </li>
        {/each}
      </ul>
      
      <div id="main_shell_innercontainer">
        <!-- Terminal View -->
        <div class="terminal-container terminal">
          <div class="terminal-overlay">DOCUMENT VIEW</div>
        </div>
      </div>
    </section>
    
    <!-- Left Side Modules -->
    <div id="mod_column_left">
      <!-- Clock Module -->
      <section id="mod_clock">
        <h3 class="title">Current time in user time zone</h3>
        <div id="mod_clock_text">
          <span id="mod_clock_hour">{time.hours}</span>
          <span>:</span>
          <span id="mod_clock_minute">{time.minutes}</span>
          <span>:</span>
          <span id="mod_clock_second">{time.seconds}</span>
        </div>
      </section>
      
      <!-- System Info -->
      <section id="mod_sysinfo">
        <div class="metadata-row">
          <span>2019</span>
          <span>UPTIME</span>
          <span>TYPE</span>
          <span>POWER</span>
        </div>
        <div class="metadata-row">
          <span>APR 30</span>
          <span>2:07:45</span>
          <span>linux</span>
          <span>WIRED</span>
        </div>
      </section>
      
      <!-- CPU Module -->
      <section id="mod_cpuinfo">
        <h3 class="title">CPU USAGE</h3>
        <div class="graph-container">
          <!-- CPU Graph representation -->
        </div>
      </section>
      
      <!-- RAM Module -->
      <section id="mod_ramwatcher">
        <h3 class="title">MEMORY</h3>
        <div class="heatmap-container">
          <!-- Memory heatmap representation -->
        </div>
      </section>
      
      <!-- Process List -->
      <section id="mod_toplist">
        <h3 class="title">TOP PROCESSES</h3>
        <div class="process-list">
          <!-- Process list -->
        </div>
      </section>
    </div>
    
    <!-- Right Side Modules -->
    <div id="mod_column_right">
      <!-- Network Status -->
      <section id="mod_conninfo">
        <h3 class="title">NETWORK STATUS</h3>
        <div class="status-details">
          <div class="status-row">
            <span class="label">Interface:</span>
            <span class="value">ens5s01</span>
          </div>
          <div class="status-row">
            <span class="label">Status:</span>
            <span class="value online">ONLINE</span>
          </div>
        </div>
      </section>
      
      <!-- Globe/Map View -->
      <section id="mod_globe">
        <h3 class="title">WORLD VIEW</h3>
        <div class="map-container">
          <!-- Map representation -->
        </div>
      </section>
      
      <!-- Documents Modal Component -->
      <DocumentsModal />
    </div>
  </div>
  
  <!-- File Explorer Component -->
  <FileExplorer />
  
  <!-- Status Bar Component -->
  <Statusbar />
</div>

<style>
  /* Override any component specific styles here */
  #container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 100vw;
    background-color: #000;
  }
  
  #main {
    display: flex;
    height: calc(100vh - 30vh);
  }
  
  .terminal-overlay {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 48px;
    color: rgba(255, 0, 255, 0.5);
    text-transform: uppercase;
    letter-spacing: 3px;
    z-index: 100;
  }
</style>
