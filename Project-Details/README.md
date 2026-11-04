<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ECE 350: Embedded Systems & Hardware Interface Project</title>
  <style>
    :root {
      --bg-color: #0d1117;
      --card-bg: #161b22;
      --border-color: #30363d;
      --text-main: #c9d1d9;
      --text-muted: #8b949e;
      --heading-color: #58a6ff;
      --accent: #238636;
      --code-bg: #1f242c;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      background-color: var(--bg-color);
      color: var(--text-main);
      line-height: 1.6;
      padding: 40px 20px;
      margin: 0;
    }

    .container {
      max-width: 900px;
      margin: 0 auto;
      background-color: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 32px;
    }

    h1, h2, h3 {
      color: var(--heading-color);
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 8px;
    }

    h1 {
      margin-top: 0;
      font-size: 2rem;
    }

    h2 {
      margin-top: 32px;
      font-size: 1.4rem;
    }

    p, ul {
      margin-bottom: 16px;
    }

    ul {
      padding-left: 24px;
    }

    li {
      margin-bottom: 6px;
    }

    hr {
      border: 0;
      border-top: 1px solid var(--border-color);
      margin: 32px 0;
    }

    pre {
      background-color: var(--code-bg);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 16px;
      overflow-x: auto;
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
      font-size: 0.9rem;
      color: #e6edf3;
    }

    code {
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
      background-color: rgba(110, 118, 129, 0.2);
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.85em;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 16px;
      margin-bottom: 24px;
    }

    th, td {
      border: 1px solid var(--border-color);
      padding: 10px 14px;
      text-align: left;
    }

    th {
      background-color: #21262d;
      color: #f0f6fc;
    }

    ol {
      padding-left: 20px;
    }

    ol li {
      margin-bottom: 8px;
    }
  </style>
</head>
<body>

  <div class="container">
    <h1>ECE 350: Embedded Systems & Hardware Interface Project</h1>

    <h2>1. Executive Summary & Value Proposition</h2>
    <ul>
      <li><strong>Problem Statement:</strong> Current commercial automated monitoring solutions are often rigid, cost-prohibitive, and lack low-latency, deterministic hardware control for rapid threshold responses.</li>
      <li><strong>Proposed Solution:</strong> A modular embedded interface bridging real-time sensor data acquisition with automated actuator control and low-power hardware triggers.</li>
      <li><strong>Core Value & Impact:</strong>
        <ul>
          <li>Eliminates software polling overhead via direct interrupt-driven peripheral control.</li>
          <li>Reduces baseline system idle power consumption.</li>
          <li>Provides a reproducible, cost-effective baseline architecture for scalable IoT/sensor network deployments.</li>
        </ul>
      </li>
    </ul>

    <hr>

    <h2>2. System Architecture</h2>
    <pre>
+--------------------+       I2C / SPI / GPIO       +----------------------+
|                    | ---------------------------> |                      |
| Analog & Digital   |                              |  Microcontroller /   |
| Sensor Inputs      | &lt;--------------------------- |  Development Board   |
| (PIR / Temp / ADC) |       Hardware Interrupts    |  (ARM Cortex / AVR)  |
+--------------------+                              +----------------------+
                                                               |
                                            PWM / GPIO Control | UART Telemetry
                                                               v
                                                    +----------------------+
                                                    | Actuators & Outputs  |
                                                    | (RGB LEDs, Relays,   |
                                                    | Serial Data Stream)  |
                                                    +----------------------+
    </pre>

    <hr>

    <h2>3. Hardware Requirements & Pinout Configuration</h2>
    <table>
      <thead>
        <tr>
          <th>Component</th>
          <th>Interface / Protocol</th>
          <th>Pin / Port Mapping</th>
          <th>Purpose</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Microcontroller Board</strong></td>
          <td>System Controller</td>
          <td><code>Core MCU</code></td>
          <td>Central processing & logic</td>
        </tr>
        <tr>
          <td><strong>Primary Sensor (e.g., PIR / Temp)</strong></td>
          <td>GPIO / External Interrupt</td>
          <td><code>Pin EXTI_0</code></td>
          <td>Low-latency threshold detection</td>
        </tr>
        <tr>
          <td><strong>Actuator / Indicator (e.g., RGB LED)</strong></td>
          <td>Hardware Timer (PWM)</td>
          <td><code>Pins PWM_R, PWM_G, PWM_B</code></td>
          <td>Real-time visual status signaling</td>
        </tr>
        <tr>
          <td><strong>Auxiliary Peripheral / Display</strong></td>
          <td>I2C / SPI</td>
          <td><code>SCL, SDA / MOSI, SCK</code></td>
          <td>Telemetry logging or local readout</td>
        </tr>
      </tbody>
    </table>

    <hr>

    <h2>4. Software Architecture & Implementation</h2>
    <ul>
      <li><strong>Interrupt Service Routine (ISR):</strong> Triggered immediately upon peripheral threshold crossing to eliminate CPU-intensive blocking delays.</li>
      <li><strong>State Machine:</strong> Deterministic finite-state machine (FSM) cycling across <code>IDLE</code>, <code>SAMPLING</code>, <code>PROCESSING</code>, and <code>ALERT/ACTUATE</code> states.</li>
      <li><strong>Hardware Timers & PWM:</strong> Microcontroller hardware timers generate pulse-width modulation signals independently of main loop execution.</li>
      <li><strong>Low-Power Idle:</strong> Core enters sleep mode between events to minimize continuous current draw.</li>
    </ul>

    <hr>

    <h2>5. Repository Directory Layout</h2>
    <pre>
├── docs/
│   ├── ProjectDescription_FA26.pdf
│   ├── ECE350_Project_Proposal.pdf
│   └── Value_Creation_ECE350.pdf
├── firmware/
│   ├── src/                 # Peripheral drivers, ISRs, and core state machine
│   └── include/             # Hardware register definitions & header files
├── hardware/
│   └── schematics/          # Wiring diagrams, pinout charts, and circuit layouts
├── scripts/                 # Data logging and telemetry parsing utilities
└── README.md
    </pre>

    <hr>

    <h2>6. Build, Flashing & Execution Setup</h2>

    <h3>Prerequisites</h3>
    <ul>
      <li>Toolchain: <code>arm-none-eabi-gcc</code> or platform-specific compiler</li>
      <li>Build System: <code>make</code> or PlatformIO</li>
      <li>Flash Utility: <code>OpenOCD</code>, <code>avrdude</code>, or vendor-specific programmer</li>
    </ul>

    <h3>Compilation & Deployment Steps</h3>
    <pre>
# Clone the repository
git clone https://github.com/Xiao-XC/ECE350-embeddedSystems-HardwareInterface-Project.git
cd ECE350-embeddedSystems-HardwareInterface-Project

# Build firmware
make all

# Flash to target board via serial/SWD interface
make flash
    </pre>

    <hr>

    <h2>Immediate Next Steps</h2>
    <ol>
      <li>Save this file as <code>index.html</code> to view it locally in your browser.</li>
      <li>If embedding directly into GitHub markdown, use standard Markdown rather than raw HTML wrapper tags (<code>&lt;html&gt;</code>, <code>&lt;body&gt;</code>).</li>
    </ol>
  </div>

</body>
</html>
