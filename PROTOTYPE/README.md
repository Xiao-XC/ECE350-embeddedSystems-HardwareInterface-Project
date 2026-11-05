# Automatic Security System — Hardware Prototype (`PROTOTYPE/`)

**Team Name:** Mvidia (Tom Chen, Jake Yurasko)  
**Course:** ECE-350 Interactive Embedded Systems Design Project  

---

## 1. Prototype Overview
This directory contains the hardware interface tests and prototype code for the **Automatic Security System**. The goal of this prototype is to verify real-time peripheral integration on the Raspberry Pi—specifically combining a **PIR motion sensor**, a **180° servo motor**, a **passive buzzer**, and **three status LEDs (Green, Yellow, Red)** across three distinct operational states.

---

## 2. Prototype State Machine & Logic

### State Summary
| System State | Trigger Condition | Green LED | Yellow LED | Red LED | Servo Motor | Passive Buzzer |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **1. Standby (Clear)** | No motion detected | **ON** | OFF | OFF | `0°` (Home) | OFF |
| **2. Warning (Triggered)** | Initial motion detected | OFF | **ON** | OFF | Moves **`180°`** | OFF |
| **3. Alarm (Sustained)** | Continuous motion over time threshold | OFF | OFF | **ON** | Holds `180°` | **ACTIVE (Sounding)** |

---

### State Transition Diagram

```text
+-----------------------------------------------------------------------+
|                        [ 1. STANDBY / NO MOTION ]                     |
|                     • Green LED: ON                                   |
|                     • Yellow & Red LEDs: OFF                          |
|                     • Servo Position: 0°  |  Buzzer: OFF              |
+-----------------------------------------------------------------------+
                                   |
                                   | (Motion Detected)
                                   v
+-----------------------------------------------------------------------+
|                       [ 2. INITIAL MOTION WARNING ]                   |
|                     • Green LED: OFF  |  Yellow LED: ON               |
|                     • Servo Action: Rotates 180°                      |
|                     • Duration Timer: Starts tracking presence        |
+-----------------------------------------------------------------------+
                  /                                 \
 (Motion Stops Before Threshold)         (Motion Persists Over Time Threshold)
                /                                     \
               v                                       v
+------------------------------+       +--------------------------------+
|     [ RESET TO STANDBY ]     |       |     [ 3. SUSTAINED ALARM ]     |
|  • Green LED: ON             |       |  • Yellow LED: OFF             |
|  • Servo Returns to 0°       |       |  • Red LED: ON                 |
|  • Timer Resets              |       |  • Buzzer: SOUNDING            |
+------------------------------+       +--------------------------------+
```

---

## 3. Prototype Hardware Components

| Component | Quantity | Prototype Function |
| :--- | :---: | :--- |
| **Raspberry Pi** | 1 | Reads PIR sensor input and drives LED, PWM servo, and buzzer outputs |
| **PIR Motion Sensor** | 1 | Detects infrared motion and outputs a digital `HIGH` signal |
| **Servo Motor** | 1 | Sweeps `180°` immediately when motion is first detected |
| **Green LED** | 1 | Indicates area is clear (`NO MOTION`) |
| **Yellow LED** | 1 | Indicates initial motion detected (`WARNING` / Servo active) |
| **Red LED** | 1 | Indicates sustained presence (`ALARM` triggered) |
| **Passive Buzzer** | 1 | Emits an audible alarm tone alongside the Red LED |
| **Resistors, Jumper Wires & Breadboard** | Assorted | Current-limiting protection (`220Ω–330Ω`) and GPIO breadboard routing |

---

## 4. GPIO Pinout Mapping (Placeholder)

> *Update the BCM pin numbers below to match your exact breadboard wiring:*

| Peripheral | GPIO Pin (BCM) | Physical Pin | Signal Type |
| :--- | :---: | :---: | :--- |
| **PIR Motion Sensor (`OUT`)** | `GPIO 17` | Pin 11 | Digital Input |
| **Green LED** | `GPIO 27` | Pin 13 | Digital Output |
| **Yellow LED** | `GPIO 22` | Pin 15 | Digital Output |
| **Red LED** | `GPIO 23` | Pin 16 | Digital Output |
| **Servo Motor (`PWM`)** | `GPIO 18` | Pin 12 | PWM Output |
| **Passive Buzzer** | `GPIO 24` | Pin 18 | PWM / Tone Output |

---

## 5. Running the Prototype

```bash
# Navigate to the prototype directory
cd PROTOTYPE

# Run the prototype script on the Raspberry Pi
python3 prototype_test.py
```
