/*
  Buggy Motor Controller
  ------------------------------------------------------------
  Receives (steer, throttle) commands over Serial from the host
  running inference.py (QNN NPU inference), and converts them
  into PWM signals for a steering servo and a throttle ESC.

  Wire format (from host, one line per command, newline terminated):
      <steer>,<throttle>\n
  e.g.
      0.3521,-0.1002\n

  steer, throttle are both floats in [-1, 1], matching the
  deterministic_continuous_actions output of the RL policy.

  Wiring:
    - STEER_SERVO_PIN -> steering servo signal wire
    - THROTTLE_ESC_PIN -> ESC signal wire (treated like a servo)
    - Servo/ESC power comes from a separate BEC/battery, NOT the
      Arduino 5V rail, unless you know your ESC has a BEC rated
      for it. Common ground with the Arduino is required.
*/

#include <Servo.h>

// ---------------- Pin config ----------------
const int STEER_SERVO_PIN   = 9;
const int THROTTLE_ESC_PIN  = 10;

// ---------------- Calibration ----------------
// Adjust these to match your actual servo/ESC endpoints.
const int STEER_CENTER_US   = 1500;
const int STEER_RANGE_US    = 500;   // full lock = center +/- this value

const int THROTTLE_NEUTRAL_US = 1500;
const int THROTTLE_RANGE_US   = 500;

// ---------------- Failsafe ----------------
// If no valid command is received within this window, go neutral.
const unsigned long COMMAND_TIMEOUT_MS = 500;

Servo steerServo;
Servo throttleESC;

String inputBuffer = "";
unsigned long lastCommandMillis = 0;
bool failsafeActive = false;

void setup() {
  Serial.begin(115200);

  steerServo.attach(STEER_SERVO_PIN);
  throttleESC.attach(THROTTLE_ESC_PIN);

  // Neutral on boot
  steerServo.writeMicroseconds(STEER_CENTER_US);
  throttleESC.writeMicroseconds(THROTTLE_NEUTRAL_US);

  // Many ESCs need to see neutral for a moment to arm
  delay(2000);

  lastCommandMillis = millis();
  Serial.println("READY");
}

void loop() {
  // --- Read any pending serial data ---
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      processCommand(inputBuffer);
      inputBuffer = "";
    } else if (c != '\r') {
      inputBuffer += c;
    }
  }

  // --- Failsafe: no command recently -> go neutral ---
  if (millis() - lastCommandMillis > COMMAND_TIMEOUT_MS) {
    if (!failsafeActive) {
      steerServo.writeMicroseconds(STEER_CENTER_US);
      throttleESC.writeMicroseconds(THROTTLE_NEUTRAL_US);
      failsafeActive = true;
      Serial.println("FAILSAFE: no command, holding neutral");
    }
  }
}

void processCommand(String line) {
  line.trim();
  if (line.length() == 0) return;

  int commaIdx = line.indexOf(',');
  if (commaIdx == -1) {
    Serial.println("ERR bad format, expected steer,throttle");
    return;
  }

  float steer    = line.substring(0, commaIdx).toFloat();
  float throttle = line.substring(commaIdx + 1).toFloat();

  // Clamp to the policy's valid action range
  steer    = constrain(steer, -1.0, 1.0);
  throttle = constrain(throttle, -1.0, 1.0);

  int steerUs    = STEER_CENTER_US    + (int)(steer    * STEER_RANGE_US);
  int throttleUs = THROTTLE_NEUTRAL_US + (int)(throttle * THROTTLE_RANGE_US);

  steerServo.writeMicroseconds(steerUs);
  throttleESC.writeMicroseconds(throttleUs);

  lastCommandMillis = millis();
  failsafeActive = false;

  Serial.print("OK ");
  Serial.print(steer, 4);
  Serial.print(",");
  Serial.println(throttle, 4);
}
