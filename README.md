# Automatic Security System — ECE 350 Fall 2026

**Team Name:** Mvidia (Tom Chen, Jake Yurasko)  
**Course:** ECE-350 Interactive Embedded Systems Design Project  

---

## 1. Executive Summary & Value Proposition

> **Value Statement:** *"Our security system helps property owners by providing an automatic security device so they can have increased safety."*

### Project Summary
The **Automatic Security System** is an interactive, Raspberry Pi-based property security prototype designed to detect unauthorized entry into restricted areas and deter intrusions. Using a pyroelectric infrared (PIR) motion sensor, the system continuously monitors a designated perimeter. When motion is detected within range, the system transitions from an armed standby state (**Green LED**) to a grace-period warning state (**Yellow LED**), displaying a live countdown timer on an **LCD screen** so authorized individuals have time to disarm the system. If the countdown reaches zero without being disarmed, the system triggers an active alarm state—flashing a **Red LED** and sounding a **passive buzzer** to alert nearby residents and security personnel.

### Stakeholders & Value Creation
Aligned with the ECE 350 Value Creation & Entrepreneurial Mindset framework (Curiosity, Connections, Creating Value), this project delivers multi-dimensional value:

* **Primary Stakeholders:** Homeowners, residents, property owners, and law enforcement / security personnel.
* **Risk Reduction & Safety Value:** Deters property intrusions and provides immediate audiovisual alerts when unauthorized entry occurs.
* **User & Stakeholder Value:** Incorporates a visual grace-period countdown (Yellow LED + LCD timer) that prevents false alarms for authorized residents while maintaining strict perimeter monitoring.
* **Technical & Functional Value:** Integrates real-time sensor polling/interrupts, multi-state visual/auditory feedback, and interactive user disarming on a Raspberry Pi platform.

---

## 2. System State Workflow

```text
+-----------------------------------------------------------------------+
|                           [ ARMED / STANDBY ]                         |
|                     • Green LED: ON                                   |
|                     • PIR Motion Sensor: Actively Monitoring          |
+-----------------------------------------------------------------------+
                                   |
                                   | (Motion Detected in Range)
                                   v
+-----------------------------------------------------------------------+
|                        [ WARNING / GRACE PERIOD ]                     |
|                     • Green LED: OFF | Yellow LED: ON                 |
|                     • LCD Screen: Live Disarm Countdown Timer         |
+-----------------------------------------------------------------------+
                  /                                 \
 (User Disarms Before 0s)                     (Countdown Hits 0s)
                /                                     \
               v                                       v
+------------------------------+       +--------------------------------+
|      [ SYSTEM DISARMED ]     |       |     [ INTRUSION / ALARM ]      |
|  • Returns to Safe/Standby   |       |  • Red LED: Flashing           |
|  • Alarm Prevented           |       |  • Passive Buzzer: Active      |
+------------------------------+       +--------------------------------+
```

---

## 3. Hardware Components & Bill of Materials

| Component | Quantity | Role in System |
| :--- | :---: | :--- |
| **Raspberry Pi** | 1 | Central embedded controller executing Python state logic and GPIO control |
| **Pyroelectric (PIR) Motion Sensor** | 1 | Detects human infrared motion within the monitored perimeter |
| **LCD Screen** | 1 | Displays real-time grace-period countdown timer and system status |
| **LEDs (Green, Yellow, Red)** | 3 | Visual state indicators: Armed (Green), Grace Period (Yellow), Alarm (Red) |
| **Passive Buzzer** | 1 | Generates audible alarm signal when countdown expires |
| **Resistors, Jumper Wires & Breadboard** | Assorted | Current limiting, circuit prototyping, and GPIO interfacing |

---

## 4. Repository Structure

```text
ECE350-embeddedSystems-HardwareInterface-Project/
├── Project-Details/
│   ├── ECE350 Project Proposal.pdf      # Team Mvidia project proposal & BOM
│   ├── ProjectDescription_FA26.pdf      # ECE-350 Fall 2026 course guidelines & rubric
│   ├── Slide_Deck_Value_Creation.pdf    # Value creation presentation slides
│   ├── Value_Creation_ECE350.pdf        # KEEN / Entrepreneurial Mindset documentation
│   └── README.md                        # Project documentation
└── src/                                 # Python source code & hardware control scripts
```

---

## 5. Software & Attribution Guidelines

Per ECE-350 Fall 2026 project requirements:
* **Core Libraries:** Built using Python (`gpiozero`, Adeept lab kit modules, and LCD driver libraries).
* **Code Attribution:** All external libraries, Adeept sample code, `gpiozero` documentation snippets, instructor-provided code, and Generative AI (GenAI) assisted code segments are explicitly documented via inline Python comments with source links.

### Running the Prototype
```bash
# Clone the repository
git clone [https://github.com/Xiao-XC/ECE350-embeddedSystems-HardwareInterface-Project.git](https://github.com/Xiao-XC/ECE350-embeddedSystems-HardwareInterface-Project.git)
cd ECE350-embeddedSystems-HardwareInterface-Project

# Execute the security system script on Raspberry Pi
python3 main.py
```

---

## 6. Course Milestones & Evaluation Breakdown

* **Proposal & Team Signup:** October 21, 2026
* **Showcase Presentations (The MIX):** Wednesday, December 2, 2026 (Group 1) / Monday, December 7, 2026 (Group 2)

| Evaluation Category | Weight |
| :--- | :---: |
| **Proposal (with Value Statement)** | 2 pts |
| **Overall Design** (Functionality, complexity, craftsmanship, aesthetics, cable management, interaction, creativity) | 10 pts |
| **Project Demonstration** (Working prototype at The MIX) | 10 pts |
| **Well-Commented Python Code** (Including proper external/GenAI citations) | 4 pts |
| **Total** | **26 pts** |
