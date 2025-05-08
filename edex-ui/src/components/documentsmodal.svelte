<script>
  import { onMount } from 'svelte';
  
  // Document knowledge graph data
  let documents = [
    { id: 1, name: "User Guide", type: "manual" },
    { id: 2, name: "API Reference", type: "reference" },
    { id: 3, name: "System Documentation", type: "manual" },
    { id: 4, name: "Troubleshooting", type: "guide" },
    { id: 5, name: "Quick Start", type: "guide" }
  ];
  
  // Location data
  let originLocation = "Hampton Roads, VA";
  let impactLocation = "Global";
  
  // Map data
  let map;
  let mapInitialized = false;
  
  // Define the Hampton Roads cities/localities
  const hamptonRoadsCities = [
    "NORFOLK", "VIRGINIA BEACH", "CHESAPEAKE", "PORTSMOUTH", 
    "SUFFOLK", "HAMPTON", "NEWPORT NEWS", "WILLIAMSBURG",
    "JAMES CITY", "GLOUCESTER", "YORK", "POQUOSON",
    "ISLE OF WIGHT", "SURRY", "SOUTHAMPTON", "SMITHFIELD"
  ];

  // Define the Seven Cities specifically
  const sevenCities = [
    "CHESAPEAKE", "HAMPTON", "NEWPORT NEWS", "NORFOLK", 
    "PORTSMOUTH", "SUFFOLK", "VIRGINIA BEACH"
  ];

  // Colors for city polygons
  const cityColor = '#2b3b80'; // Navy blue for regular localities
  const sevenCitiesColor = '#d32f2f'; // Red for the Seven Cities
  const cityOutline = '#ffffff'; // White outline
  const cityOpacity = 0.05; // Very light fill for better map visibility
  const sevenCitiesOpacity = 0.15; // Slightly higher opacity for Seven Cities
  const cityWeight = 2; // Slightly thicker border
  
  // Function to fetch GeoJSON data for Hampton Roads localities
  async function fetchHamptonRoadsData() {
    const baseUrl = 'https://vginmaps.vdem.virginia.gov/arcgis/rest/services/VA_Base_Layers/VA_Admin_Boundaries/FeatureServer/1/query';
    
    // Build query parameters
    const params = new URLSearchParams({
      where: `NAME IN ('${hamptonRoadsCities.join("','")}') AND NAME <> 'FRANKLIN COUNTY'`,
      outFields: 'NAME,JURISTYPE',
      returnGeometry: true,
      f: 'geojson'
    }).toString();
    
    try {
      const response = await fetch(`${baseUrl}?${params}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching GeoJSON data:', error);
      return null;
    }
  }

  // Function to style the GeoJSON features
  function styleFeature(feature) {
    // Check if the feature is one of the Seven Cities
    const isSevenCity = feature.properties && 
                      feature.properties.NAME && 
                      sevenCities.includes(feature.properties.NAME);
    
    return {
      fillColor: isSevenCity ? sevenCitiesColor : cityColor,
      fillOpacity: isSevenCity ? sevenCitiesOpacity : cityOpacity,
      color: cityOutline,
      weight: cityWeight,
      dashArray: '5,5', // Dashed border pattern
      lineCap: 'round',
      lineJoin: 'round'
    };
  }

  // Function to create popups for each feature
  function onEachFeature(feature, layer) {
    if (feature.properties && feature.properties.NAME) {
      const name = feature.properties.NAME;
      const type = feature.properties.JURISTYPE === 'CI' ? 'City' : 'County';
      const isSevenCity = sevenCities.includes(name);
      
      layer.bindPopup(`
        <div class="popup-content">
          <h3>${name}</h3>
          <p class="jurisdiction-type">${type}</p>
          ${isSevenCity ? '<p class="seven-cities-badge">Seven Cities</p>' : ''}
        </div>
      `);

      // Add hover effect
      layer.on({
        mouseover: function(e) {
          const layer = e.target;
          const isSevenCity = feature.properties && 
                             feature.properties.NAME && 
                             sevenCities.includes(feature.properties.NAME);
          
          layer.setStyle({
            fillOpacity: isSevenCity ? 0.4 : 0.2,
            weight: 3,
            dashArray: ''
          });
          layer.bringToFront();
        },
        mouseout: function(e) {
          const layer = e.target;
          const isSevenCity = feature.properties && 
                             feature.properties.NAME && 
                             sevenCities.includes(feature.properties.NAME);
          
          layer.setStyle({
            fillOpacity: isSevenCity ? sevenCitiesOpacity : cityOpacity,
            weight: cityWeight,
            dashArray: '5,5'
          });
        }
      });
    }
  }
  
  // Key player data
  let keyPlayers = [
    { name: "User", role: "End User" },
    { name: "Administrator", role: "System Admin" },
    { name: "Developer", role: "API Developer" }
  ];
  
  function selectDocument(id) {
    console.log(`Document ${id} selected`);
    // In a real implementation, this would load the document content
  }

  // Initialize the map and load data
  async function initMap(mapContainer) {
    if (!window.L) {
      console.error('Leaflet library not loaded');
      return;
    }

    // Initialize the map centered on Hampton Roads region
    map = L.map(mapContainer, {
      center: [36.9095, -76.2046],
      zoom: 10,
      minZoom: 9,
      maxZoom: 18,
      maxBoundsViscosity: 1.0,
      attributionControl: false,
      zoomControl: true,
      dragging: true,
      scrollWheelZoom: true,
      bounceAtZoomLimits: false,
      zoomSnap: 0.5,
      zoomDelta: 0.5
    });

    // Add a base tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Fetch the GeoJSON data for Hampton Roads localities
    const geoJsonData = await fetchHamptonRoadsData();
    
    if (geoJsonData) {
      // Create and add the GeoJSON layer for boundaries
      const geoJsonLayer = L.geoJSON(geoJsonData, {
        style: styleFeature,
        onEachFeature: onEachFeature
      }).addTo(map);

      // Fit the map to the boundaries
      const bounds = geoJsonLayer.getBounds();
      map.fitBounds(bounds);
      map.setMaxBounds(bounds);
    } else {
      console.error('Failed to load GeoJSON data');
    }

    mapInitialized = true;
  }
  
  onMount(() => {
    // Load Leaflet CSS dynamically
    const leafletCss = document.createElement('link');
    leafletCss.rel = 'stylesheet';
    leafletCss.href = 'node_modules/leaflet/dist/leaflet.css';
    document.head.appendChild(leafletCss);

    // Load Leaflet script dynamically
    const leafletScript = document.createElement('script');
    leafletScript.src = 'node_modules/leaflet/dist/leaflet.js';
    leafletScript.onload = () => {
      // Initialize map once Leaflet is loaded
      const mapContainer = document.getElementById('leaflet-map');
      if (mapContainer) {
        initMap(mapContainer);
      }
    };
    document.head.appendChild(leafletScript);

    return () => {
      // Cleanup on component destroy
      if (map) {
        map.remove();
      }
    };
  });
</script>

<section id="modal" class="documents-modal">
  <div class="modal_header">
    <h1>Document Knowledge System</h1>
  </div>
  
  <div class="modal_body">
    <div class="modal_section">
      <h2>Location of Origin</h2>
      <p class="location-info">{originLocation}</p>
    </div>
    
    <div class="modal_section">
      <h2>Location of Impact</h2>
      <p class="location-info">{impactLocation}</p>
    </div>
    
    <div class="modal_section map-section">
      <h2>Geographic Map</h2>
      <div id="leaflet-map" class="map-container" class:initialized={mapInitialized}></div>
    </div>
    
    <div class="modal_section">
      <h2>Document Selection</h2>
      <div class="document-tabs">
        {#each documents as doc}
          <div 
            class="document-tab" 
            on:click={() => selectDocument(doc.id)}
          >
            <span class="doc-type">{doc.type}</span>
            <span class="doc-name">{doc.name}</span>
          </div>
        {/each}
      </div>
    </div>
    
    <div class="modal_section">
      <h2>Knowledge Graph</h2>
      <div class="knowledge-graph">
        <div class="graph-visualization">
          <!-- Knowledge graph visualization representation -->
          <div class="node central">Documents</div>
          {#each documents as doc, i}
            <div 
              class="node satellite" 
              style="transform: rotate({i * 72}deg) translateX(80px);"
            >
              {doc.name}
            </div>
          {/each}
        </div>
      </div>
    </div>
    
    <div class="modal_section">
      <h2>Key Role Players</h2>
      <div class="key-players">
        {#each keyPlayers as player}
          <div class="player-item">
            <div class="player-name">{player.name}</div>
            <div class="player-role">{player.role}</div>
          </div>
        {/each}
      </div>
    </div>
  </div>
</section>

<style>
  /* Custom styles not covered by the imported modal.css */
  .documents-modal {
    height: auto;
    max-height: 40vh;
    overflow-y: auto;
  }
  
  .location-info {
    color: rgb(var(--color_r), var(--color_g), var(--color_b));
    font-size: 14px;
  }
  
  .map-section {
    height: 250px; /* Increased height for better map visibility */
  }
  
  .map-container {
    height: 200px; /* Increased height for better map visibility */
    background-color: var(--color_light_black);
    border-radius: 3px;
    position: relative;
    overflow: hidden;
    z-index: 1; /* Ensure map appears above other elements */
  }
  
  /* Leaflet specific overrides to match theme */
  :global(.leaflet-container) {
    background-color: var(--color_light_black) !important;
    height: 100%;
    width: 100%;
  }
  
  :global(.leaflet-popup-content-wrapper) {
    background-color: var(--color_light_black);
    color: rgb(var(--color_r), var(--color_g), var(--color_b));
    border: 1px solid rgba(var(--color_r), var(--color_g), var(--color_b), 0.5);
  }
  
  :global(.leaflet-popup-tip) {
    background-color: var(--color_light_black);
    border: 1px solid rgba(var(--color_r), var(--color_g), var(--color_b), 0.5);
  }
  
  :global(.popup-content h3) {
    margin: 0;
    color: rgb(var(--color_r), var(--color_g), var(--color_b));
  }
  
  :global(.jurisdiction-type) {
    margin: 5px 0;
    font-size: 12px;
  }
  
  :global(.seven-cities-badge) {
    background-color: #d32f2f;
    color: white;
    padding: 2px 5px;
    border-radius: 3px;
    display: inline-block;
    font-size: 10px;
    margin-top: 5px;
  }
  
  .document-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
  }
  
  .document-tab {
    background-color: var(--color_light_black);
    padding: 5px;
    border-radius: 3px;
    font-size: 12px;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    border: 1px solid rgba(var(--color_r), var(--color_g), var(--color_b), 0.3);
  }
  
  .document-tab:hover {
    background-color: rgba(var(--color_r), var(--color_g), var(--color_b), 0.1);
  }
  
  .doc-type {
    font-size: 9px;
    color: rgba(var(--color_r), var(--color_g), var(--color_b), 1);
    text-transform: uppercase;
  }
  
  .knowledge-graph {
    height: 120px;
    position: relative;
  }
  
  .graph-visualization {
    height: 100%;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .node {
    position: absolute;
    background-color: var(--color_light_black);
    padding: 5px;
    border-radius: 10px;
    font-size: 10px;
    white-space: nowrap;
    border: 1px solid rgba(var(--color_r), var(--color_g), var(--color_b), 0.3);
  }
  
  .node.central {
    background-color: rgba(var(--color_r), var(--color_g), var(--color_b), 0.2);
    color: rgb(var(--color_r), var(--color_g), var(--color_b));
    z-index: 2;
    padding: 10px;
  }
  
  .node.satellite {
    background-color: rgba(var(--color_r), var(--color_g), var(--color_b), 0.1);
    color: rgb(var(--color_r), var(--color_g), var(--color_b));
  }
  
  .key-players {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .player-item {
    background-color: var(--color_light_black);
    padding: 5px;
    border-radius: 3px;
    width: calc(33% - 10px);
    border: 1px solid rgba(var(--color_r), var(--color_g), var(--color_b), 0.3);
  }
  
  .player-name {
    font-weight: bold;
    color: rgb(var(--color_r), var(--color_g), var(--color_b));
  }
  
  .player-role {
    font-size: 10px;
    color: #888;
  }
</style>
