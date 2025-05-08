<script>
  import { onMount } from 'svelte';
  
  // Keyboard status and system information
  let batteryPercentage = "94.7%";
  let runningStatus = "Running on A/C";
  let hostname = "batcore-home";
  let loadAverage = [3.39, 3.92, 3.99];
  let uptimeInfo = "2 days, 07:45:44";
  let tasks = { total: 149, running: 3 };
  
  // Keyboard settings
  let currentKeyboard = "en-US";
  let capsLockEnabled = false;
  let altPressed = false;
  let ctrlPressed = false;
  let shiftPressed = false;
  
  // Function keys and their actions
  const functionKeys = [
    { key: "Help", action: "F1" },
    { key: "Setup", action: "F2" },
    { key: "Search", action: "F3" },
    { key: "Filter", action: "F4" },
    { key: "Sort", action: "F5" },
    { key: "Paging", action: "F6" },
    { key: "Nice-", action: "F7" },
    { key: "Nice+", action: "F8" },
    { key: "Kill", action: "F9" },
    { key: "Quit", action: "F10" }
  ];
  
  // Toggle caps lock for demo purposes
  function toggleCapsLock() {
    capsLockEnabled = !capsLockEnabled;
  }
  
  // Handle key press for demo purposes
  function handleKeyPress(key) {
    if (key === 'ctrl') ctrlPressed = !ctrlPressed;
    if (key === 'alt') altPressed = !altPressed;
    if (key === 'shift') shiftPressed = !shiftPressed;
  }
</script>

<section id="keyboard" class:fullscreen={false}>
  <div id="keyboard_info">
    <div id="keyboard_layout">
      {currentKeyboard}
    </div>
    
    <div id="sysinfo">
      <div>
        <span>Hostname:</span> 
        <span class="value">{hostname}</span>
      </div>
      <div>
        <span>Tasks:</span> 
        <span class="value">{tasks.total}, {tasks.running} running</span>
      </div>
      <div>
        <span>Load average:</span> 
        <span class="value">{loadAverage[0]} {loadAverage[1]} {loadAverage[2]}</span>
      </div>
      <div>
        <span>Uptime:</span> 
        <span class="value">{uptimeInfo}</span>
      </div>
      <div>
        <span>Battery:</span> 
        <span class="value">{batteryPercentage} ({runningStatus})</span>
      </div>
    </div>
    
    <div id="actionbar">
      {#each functionKeys as fKey}
        <div class="action">
          <div class="keycap">{fKey.action}</div>
          <div class="text">{fKey.key}</div>
        </div>
      {/each}
    </div>
  </div>
  
  <div id="keyboard_horizontal">
    <div class="keyboard_row">
      <div class="keyboard_key" id="keyboard_key_esc">ESC</div>
      <div class="keyboard_key" id="keyboard_key_1">1</div>
      <div class="keyboard_key" id="keyboard_key_2">2</div>
      <div class="keyboard_key" id="keyboard_key_3">3</div>
      <div class="keyboard_key" id="keyboard_key_4">4</div>
      <div class="keyboard_key" id="keyboard_key_5">5</div>
      <div class="keyboard_key" id="keyboard_key_6">6</div>
      <div class="keyboard_key" id="keyboard_key_7">7</div>
      <div class="keyboard_key" id="keyboard_key_8">8</div>
      <div class="keyboard_key" id="keyboard_key_9">9</div>
      <div class="keyboard_key" id="keyboard_key_0">0</div>
      <div class="keyboard_key" id="keyboard_key_minus">-</div>
      <div class="keyboard_key" id="keyboard_key_equal">=</div>
      <div class="keyboard_key" id="keyboard_key_backspace">BACK</div>
    </div>
    <div class="keyboard_row">
      <div class="keyboard_key" id="keyboard_key_tab">TAB</div>
      <div class="keyboard_key" id="keyboard_key_q">Q</div>
      <div class="keyboard_key" id="keyboard_key_w">W</div>
      <div class="keyboard_key" id="keyboard_key_e">E</div>
      <div class="keyboard_key" id="keyboard_key_r">R</div>
      <div class="keyboard_key" id="keyboard_key_t">T</div>
      <div class="keyboard_key" id="keyboard_key_y">Y</div>
      <div class="keyboard_key" id="keyboard_key_u">U</div>
      <div class="keyboard_key" id="keyboard_key_i">I</div>
      <div class="keyboard_key" id="keyboard_key_o">O</div>
      <div class="keyboard_key" id="keyboard_key_p">P</div>
      <div class="keyboard_key" id="keyboard_key_bracket_left">[</div>
      <div class="keyboard_key" id="keyboard_key_bracket_right">]</div>
      <div class="keyboard_key" id="keyboard_key_enter">ENTER</div>
    </div>
    <div class="keyboard_row">
      <div 
        class="keyboard_key {capsLockEnabled ? 'active' : ''}" 
        id="keyboard_key_caps" 
        on:click={toggleCapsLock}
      >
        CAPS
      </div>
      <div class="keyboard_key" id="keyboard_key_a">A</div>
      <div class="keyboard_key" id="keyboard_key_s">S</div>
      <div class="keyboard_key" id="keyboard_key_d">D</div>
      <div class="keyboard_key" id="keyboard_key_f">F</div>
      <div class="keyboard_key" id="keyboard_key_g">G</div>
      <div class="keyboard_key" id="keyboard_key_h">H</div>
      <div class="keyboard_key" id="keyboard_key_j">J</div>
      <div class="keyboard_key" id="keyboard_key_k">K</div>
      <div class="keyboard_key" id="keyboard_key_l">L</div>
      <div class="keyboard_key" id="keyboard_key_semicolon">;</div>
      <div class="keyboard_key" id="keyboard_key_quote">'</div>
      <div class="keyboard_key" id="keyboard_key_backslash">\</div>
    </div>
    <div class="keyboard_row">
      <div 
        class="keyboard_key {shiftPressed ? 'active' : ''}" 
        id="keyboard_key_shift_left" 
        on:click={() => handleKeyPress('shift')}
      >
        SHIFT
      </div>
      <div class="keyboard_key" id="keyboard_key_lt">&lt;</div>
      <div class="keyboard_key" id="keyboard_key_z">Z</div>
      <div class="keyboard_key" id="keyboard_key_x">X</div>
      <div class="keyboard_key" id="keyboard_key_c">C</div>
      <div class="keyboard_key" id="keyboard_key_v">V</div>
      <div class="keyboard_key" id="keyboard_key_b">B</div>
      <div class="keyboard_key" id="keyboard_key_n">N</div>
      <div class="keyboard_key" id="keyboard_key_m">M</div>
      <div class="keyboard_key" id="keyboard_key_comma">,</div>
      <div class="keyboard_key" id="keyboard_key_period">.</div>
      <div class="keyboard_key" id="keyboard_key_slash">/</div>
      <div 
        class="keyboard_key {shiftPressed ? 'active' : ''}" 
        id="keyboard_key_shift_right" 
        on:click={() => handleKeyPress('shift')}
      >
        SHIFT
      </div>
    </div>
    <div class="keyboard_row">
      <div 
        class="keyboard_key {ctrlPressed ? 'active' : ''}" 
        id="keyboard_key_ctrl_left" 
        on:click={() => handleKeyPress('ctrl')}
      >
        CTRL
      </div>
      <div class="keyboard_key" id="keyboard_key_super">FN</div>
      <div 
        class="keyboard_key {altPressed ? 'active' : ''}" 
        id="keyboard_key_alt_left" 
        on:click={() => handleKeyPress('alt')}
      >
        ALT
      </div>
      <div class="keyboard_key" id="keyboard_key_space">SPACE</div>
      <div 
        class="keyboard_key {altPressed ? 'active' : ''}" 
        id="keyboard_key_alt_right" 
        on:click={() => handleKeyPress('alt')}
      >
        ALT GR
      </div>
      <div class="keyboard_key" id="keyboard_key_left">←</div>
      <div class="keyboard_key" id="keyboard_key_up">↑</div>
      <div class="keyboard_key" id="keyboard_key_down">↓</div>
      <div class="keyboard_key" id="keyboard_key_right">→</div>
    </div>
  </div>
</section>

<style>
  /* Custom styles not covered by the imported keyboard.css */
  #sysinfo {
    display: flex;
    justify-content: space-between;
    padding: 0.5vh;
    font-size: 1.2vh;
    flex-wrap: wrap;
  }
  
  #sysinfo > div {
    margin-right: 1vw;
  }
  
  #sysinfo span.value {
    color: rgb(var(--color_r), var(--color_g), var(--color_b));
  }
  
  #actionbar {
    display: flex;
    padding: 0.3vh;
    background-color: var(--color_light_black);
    border-top: 0.1vh solid rgba(var(--color_r), var(--color_g), var(--color_b), 0.3);
  }
  
  .action {
    display: flex;
    align-items: center;
    margin-right: 1vw;
  }
  
  .action .keycap {
    background-color: rgba(var(--color_r), var(--color_g), var(--color_b), 0.2);
    border: 0.1vh solid rgba(var(--color_r), var(--color_g), var(--color_b), 0.4);
    padding: 0.2vh 0.4vw;
    margin-right: 0.3vw;
    font-size: 1.2vh;
    border-radius: 0.2vh;
  }
  
  .action .text {
    color: rgb(var(--color_r), var(--color_g), var(--color_b));
    font-size: 1.2vh;
  }
</style>
