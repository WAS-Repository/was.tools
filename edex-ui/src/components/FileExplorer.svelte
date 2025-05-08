<script>
  // File system data
  let currentPath = '/home/squared';
  let diskUsage = 71; // Percentage used
  
  // Sample file system structure
  let files = [
    { name: 'LICENSE.rtf', type: 'file', icon: 'license' },
    { name: 'README.md', type: 'file', icon: 'markdown' },
    { name: '.git', type: 'directory', icon: 'folder' },
    { name: 'src', type: 'directory', icon: 'folder' },
    { name: 'public_html', type: 'directory', icon: 'folder' },
    { name: 'cgi-bin', type: 'directory', icon: 'folder' },
    { name: '.well-known', type: 'directory', icon: 'folder' }
  ];
  
  // Toggle between file explorer and terminal on mobile
  let showDisks = false;
  let listView = false;
  let hideDotfiles = true;
  
  function toggleDisks() {
    showDisks = !showDisks;
  }
  
  function toggleView() {
    listView = !listView;
  }
  
  function toggleDotfiles() {
    hideDotfiles = !hideDotfiles;
  }
  
  function navigateToDirectory(dirName) {
    if (!showDisks) {
      currentPath = currentPath === '/' 
        ? '/' + dirName
        : currentPath + '/' + dirName;
    }
  }
  
  function goUp() {
    if (!showDisks && currentPath !== '/') {
      const parts = currentPath.split('/');
      parts.pop();
      currentPath = parts.join('/') || '/';
    }
  }
</script>

<section id="filesystem" class:hideDotfiles class:list-view={listView}>
  <h3 class="title">
    <p id="fs_disp_title_dir">FILE SYSTEM: {currentPath}</p>
  </h3>
  
  <div id="fs_disp_container" class:disks={showDisks}>
    {#if !showDisks}
      <div class="fs_disp_up" on:click={goUp}>
        <svg viewBox="0 0 24 24">
          <path d="M19,15H15V19H19M19,3H15V7H19M11,15H7V19H11M11,3H7V7H11M19,11H15V15H19M11,11H7V15H11Z" />
        </svg>
        <h3>Go up</h3>
      </div>
      <div class="fs_disp_showDisks" on:click={toggleDisks}>
        <svg viewBox="0 0 24 24">
          <path d="M6,2H18A2,2 0 0,1 20,4V20A2,2 0 0,1 18,22H6A2,2 0 0,1 4,20V4A2,2 0 0,1 6,2M12,4A6,6 0 0,0 6,10C6,13.31 8.69,16 12.1,16L11.22,13.77C10.95,13.29 11.11,12.68 11.59,12.4L12.45,11.9C12.93,11.63 13.54,11.79 13.82,12.27L15.74,14.69C17.12,13.59 18,11.9 18,10A6,6 0 0,0 12,4M12,9A1,1 0 0,1 13,10A1,1 0 0,1 12,11A1,1 0 0,1 11,10A1,1 0 0,1 12,9Z" />
        </svg>
        <h3>Disks</h3>
      </div>
      
      {#each files as file}
        <div 
          class={file.type === 'directory' ? 'fs_disp_dir' : 'fs_disp_file'} 
          class:hidden={file.name.startsWith('.')}
          on:click={() => file.type === 'directory' ? navigateToDirectory(file.name) : null}
        >
          <svg viewBox="0 0 24 24">
            {#if file.type === 'directory'}
              <path d="M10,4H4C2.89,4 2,4.89 2,6V18A2,2 0 0,0 4,20H20A2,2 0 0,0 22,18V8C22,6.89 21.1,6 20,6H12L10,4Z" />
            {:else if file.name.endsWith('.md')}
              <path d="M19,3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3M19,5V19H5V5H19M7,7V9H17V7H7M7,11V13H17V11H7M7,15V17H14V15H7Z" />
            {:else}
              <path d="M13,9H18.5L13,3.5V9M6,2H14L20,8V20A2,2 0 0,1 18,22H6C4.89,22 4,21.1 4,20V4C4,2.89 4.89,2 6,2M6,20H15V18H6V20M6,17H15V15H6V17M6,14H15V12H6V14M6,11H15V9H6V11Z" />
            {/if}
          </svg>
          <h3>{file.name}</h3>
          {#if listView}
            <h4>File</h4>
            <h4>10K</h4>
            <h4>Today 14:30</h4>
          {/if}
        </div>
      {/each}
    {:else}
      <div class="fs_disp_disk">
        <h3>System (C:)</h3>
        <h4>64 GB</h4>
        <div class="disk-usage">
          <div class="usage-bar" style="width: {71}%"></div>
        </div>
      </div>
      <div class="fs_disp_disk">
        <h3>Data (D:)</h3>
        <h4>256 GB</h4>
        <div class="disk-usage">
          <div class="usage-bar" style="width: {45}%"></div>
        </div>
      </div>
    {/if}
  </div>
  
  <div id="fs_space_bar">
    <h1 on:click={toggleDisks}>Exit Disk Selection</h1>
    <h3>{currentPath}</h3>
    <progress value={diskUsage} max="100"></progress>
  </div>
  
  <div class="view-options">
    <button on:click={toggleView}>Toggle View</button>
    <button on:click={toggleDotfiles}>Toggle Hidden Files</button>
  </div>
</section>

<style>
  /* Additional styles not covered by the imported css */
  .view-options {
    position: absolute;
    right: 0.5vw;
    top: 0.5vh;
  }
  
  .view-options button {
    background: rgba(var(--color_r), var(--color_g), var(--color_b), 0.2);
    border: 1px solid rgba(var(--color_r), var(--color_g), var(--color_b), 0.5);
    color: rgb(var(--color_r), var(--color_g), var(--color_b));
    padding: 0.2vh 0.5vw;
    font-size: 1.2vh;
    cursor: pointer;
  }
  
  .fs_disp_disk {
    border: 1px solid rgba(var(--color_r), var(--color_g), var(--color_b), 0.5);
    border-radius: 0.3vh;
    padding: 1vh;
    margin: 1vh;
    width: 20vw;
  }
  
  .disk-usage {
    height: 0.5vh;
    background: rgba(var(--color_r), var(--color_g), var(--color_b), 0.2);
    margin-top: 0.5vh;
  }
  
  .usage-bar {
    height: 100%;
    background: rgb(var(--color_r), var(--color_g), var(--color_b));
  }
</style>
