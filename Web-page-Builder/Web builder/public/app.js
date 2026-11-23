const statusBadge = document.querySelector("#status-badge");
const statusLabel = document.querySelector("#status-label");
const lastEvent = document.querySelector("#last-event");
const countdownWrap = document.querySelector("#countdown-wrap");
const countdown = document.querySelector("#countdown");
const panel = document.querySelector(".verification-panel");
const panelTitle = document.querySelector("#panel-title");
const panelKicker = document.querySelector(".panel-kicker");
const panelDescription = document.querySelector("#panel-description");
const pinForm = document.querySelector("#pin-form");
const pinInputs = [...document.querySelectorAll("#pin-inputs input")];
const pinGroup = document.querySelector("#pin-inputs");
const pinError = document.querySelector("#pin-error");
const submitButton = document.querySelector("#submit-button");
const successPanel = document.querySelector("#success-panel");
const resetButton = document.querySelector("#reset-button");
const activityBody = document.querySelector("#activity-body");
const simulateButton = document.querySelector("#simulate-button");
const debugMessage = document.querySelector("#debug-message");

let current = { status: "IDLE" };
let busy = false;
let historyKey = "";

function formatTime(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat(undefined, {
    month: "short", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit"
  }).format(new Date(value));
}

function showError(message) {
  pinError.textContent = message;
  pinError.hidden = false;
  pinGroup.classList.remove("shake");
  void pinGroup.offsetWidth;
  pinGroup.classList.add("shake");
  pinInputs.forEach((input) => { input.value = ""; });
  pinInputs[0].focus();
}

function updateView(data) {
  const changedEvent = data.id !== current.id || data.status !== current.status;
  current = data;
  const status = data.status;
  statusBadge.dataset.status = status;
  statusLabel.textContent = status === "PENDING" ? "ALERT: VERIFICATION REQUIRED"
    : status === "VERIFIED" ? "DISARMED / OK SENT" : "IDLE";
  lastEvent.textContent = formatTime(data.timestamp);
  countdownWrap.hidden = status !== "PENDING";

  if (status === "PENDING") {
    panel.hidden = false;
    panel.classList.remove("is-verified");
    pinForm.hidden = false;
    successPanel.hidden = true;
    panelKicker.textContent = "VERIFICATION REQUIRED";
    panelTitle.innerHTML = "Enter your<br>access code";
    panelDescription.textContent = "A 4-digit code was sent to your registered email. The code expires in 5 minutes.";
    pinInputs.forEach((input) => { input.disabled = busy; });
  } else if (status === "VERIFIED") {
    panel.hidden = false;
    panel.classList.add("is-verified");
    pinForm.hidden = true;
    successPanel.hidden = false;
    panelKicker.textContent = "VERIFICATION COMPLETE";
    panelTitle.textContent = "System cleared";
    panelDescription.textContent = "Your identity is verified. The all-clear signal is ready for your Raspberry Pi.";
  } else {
    panel.hidden = false;
    panel.classList.remove("is-verified");
    pinForm.hidden = true;
    successPanel.hidden = true;
    panelKicker.textContent = "STANDBY";
    panelTitle.textContent = "System is idle";
    if (data.lastResult === "EXPIRED") {
      panelDescription.textContent = "That verification code expired. Trigger the sensor again to request a new code.";
      statusBadge.dataset.status = "EXPIRED";
      statusLabel.textContent = "CODE EXPIRED";
    } else if (data.lastResult === "LOCKED") {
      panelDescription.textContent = "Too many incorrect attempts. Trigger the sensor again to request a new code.";
      statusBadge.dataset.status = "INVALID";
      statusLabel.textContent = "ATTEMPTS LOCKED";
    } else {
      panelDescription.textContent = "No active security event. The system is monitoring for a sensor trigger.";
    }
  }
  if (changedEvent && status === "PENDING") {
    pinError.hidden = true;
    pinInputs.forEach((input) => { input.value = ""; input.disabled = false; });
  }
  if (changedEvent && status === "IDLE") {
    pinError.hidden = true;
  }
}

function updateCountdown() {
  if (current.status !== "PENDING" || !current.expiresAt) return;
  const seconds = Math.max(0, Math.ceil((new Date(current.expiresAt).getTime() - Date.now()) / 1000));
  countdown.textContent = `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
  if (seconds === 0) refreshStatus();
}

async function refreshStatus() {
  try {
    const response = await fetch("/api/status", { cache: "no-store" });
    if (!response.ok) throw new Error("Status request failed.");
    updateView(await response.json());
    await refreshHistory();
  } catch {
    statusLabel.textContent = "CONNECTION LOST";
    statusBadge.dataset.status = "INVALID";
  }
}

async function refreshHistory() {
  try {
    const response = await fetch("/api/history", { cache: "no-store" });
    if (!response.ok) return;
    const data = await response.json();
    const key = JSON.stringify(data.events);
    if (key === historyKey) return;
    historyKey = key;
    if (!data.events.length) {
      activityBody.innerHTML = '<tr><td class="empty-row" colspan="4">No events recorded yet.</td></tr>';
      return;
    }
    activityBody.innerHTML = data.events.map((event) => {
      const responseTime = event.responseMs == null ? "—" : `${(event.responseMs / 1000).toFixed(1)}s`;
      return `<tr><td>#${event.id}</td><td>${formatTime(event.timestamp)}</td><td><span class="event-status" data-status="${event.status}">${event.status.replaceAll("_", " ")}</span></td><td>${responseTime}</td></tr>`;
    }).join("");
  } catch {
    // The main status view remains usable if the activity history is temporarily unavailable.
  }
}

function moveFocus(index) {
  if (index >= 0 && index < pinInputs.length) pinInputs[index].focus();
}

pinInputs.forEach((input, index) => {
  input.addEventListener("input", () => {
    const digit = input.value.replace(/\D/g, "").slice(-1);
    input.value = digit;
    pinError.hidden = true;
    if (digit) {
      if (index < pinInputs.length - 1) moveFocus(index + 1);
      else pinForm.requestSubmit();
    }
  });
  input.addEventListener("keydown", (event) => {
    if (event.key === "Backspace" && !input.value && index > 0) moveFocus(index - 1);
    if (event.key === "ArrowLeft") moveFocus(index - 1);
    if (event.key === "ArrowRight") moveFocus(index + 1);
  });
  input.addEventListener("paste", (event) => {
    const pasted = event.clipboardData.getData("text").replace(/\D/g, "").slice(0, 4);
    if (!pasted) return;
    event.preventDefault();
    pasted.split("").forEach((digit, digitIndex) => { pinInputs[digitIndex].value = digit; });
    if (pasted.length === 4) pinForm.requestSubmit();
    else moveFocus(pasted.length);
  });
});

pinForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const pin = pinInputs.map((input) => input.value).join("");
  if (pin.length !== 4 || busy) return;
  busy = true;
  submitButton.disabled = true;
  pinInputs.forEach((input) => { input.disabled = true; });
  pinError.hidden = true;
  try {
    const response = await fetch("/api/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin })
    });
    const result = await response.json();
    if (!response.ok) {
      showError(result.message || result.error || "Verification failed.");
      if (result.reason === "LOCKED" || result.reason === "EXPIRED") await refreshStatus();
      return;
    }
    updateView({ ...current, ...result, id: current.id });
    await refreshHistory();
  } catch {
    showError("Could not reach the verification service. Try again.");
  } finally {
    busy = false;
    submitButton.disabled = false;
    if (current.status === "PENDING") pinInputs.forEach((input) => { input.disabled = false; });
  }
});

resetButton.addEventListener("click", async () => {
  resetButton.disabled = true;
  try {
    const response = await fetch("/api/reset", {
      method: "POST",
      headers: { "X-Requested-With": "SentinelDashboard" }
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "System reset failed.");
    updateView({ ...result, timestamp: current.timestamp, id: current.id });
    await refreshHistory();
  } catch (error) {
    window.alert(error.message);
  } finally {
    resetButton.disabled = false;
  }
});

simulateButton.addEventListener("click", async () => {
  simulateButton.disabled = true;
  debugMessage.hidden = false;
  debugMessage.textContent = "Sending test trigger…";
  try {
    const response = await fetch("/api/simulate", { method: "POST" });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Simulation failed.");
    debugMessage.textContent = "Test trigger sent. Check the registered email for the code.";
    await refreshStatus();
  } catch (error) {
    debugMessage.textContent = error.message;
  } finally {
    simulateButton.disabled = false;
  }
});

async function loadConfig() {
  try {
    const response = await fetch("/api/config", { cache: "no-store" });
    const config = await response.json();
    simulateButton.hidden = !config.simulationEnabled;
  } catch {
    simulateButton.hidden = true;
  }
}

loadConfig();
refreshStatus();
window.setInterval(refreshStatus, 2000);
window.setInterval(updateCountdown, 250);
