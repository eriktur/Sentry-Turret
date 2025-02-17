#include <AccelStepper.h>

// --- Pinner for X-akse ---
#define X_STEP_PIN  2
#define X_DIR_PIN   3
#define X_EN_PIN    6

// --- Pinner for Y-akse ---
#define Y_STEP_PIN  9
#define Y_DIR_PIN   8
#define Y_EN_PIN   12

// Limit switch for X (NO->pin7, COM->GND)
#define X_LIMIT_PIN 7

AccelStepper stepperX(AccelStepper::DRIVER, X_STEP_PIN, X_DIR_PIN);
AccelStepper stepperY(AccelStepper::DRIVER, Y_STEP_PIN, Y_DIR_PIN);

const float scalingFactorX = 2.3; 
const float scalingFactorY = 2.1;

const int centerX = 320;
const int centerY = 240;

const long X_BACK_OFF = 2165;  

const long Y_START_UP = 500; 

const long STEPS_PER_REV = 10000;

String inputString = "";
bool stringComplete = false;

void homeXAxis();

void setup() {
  Serial.begin(9600);
  Serial.println("Oppstart...");

  // Enable-pinner
  pinMode(X_EN_PIN, OUTPUT);
  pinMode(Y_EN_PIN, OUTPUT);
  digitalWrite(X_EN_PIN, LOW);
  digitalWrite(Y_EN_PIN, LOW);

  // Limit switch (INPUT_PULLUP) => NO->pin7, COM->GND
  pinMode(X_LIMIT_PIN, INPUT_PULLUP);

  stepperX.setMaxSpeed(9000);
  stepperX.setAcceleration(115000);

  stepperY.setMaxSpeed(9000);
  stepperY.setAcceleration(115000);

  // Home X-aksen
  homeXAxis();

  stepperY.setCurrentPosition(0);
  stepperY.move(Y_START_UP);
  while (stepperY.distanceToGo() != 0) {
    stepperY.run();
  }
  stepperY.setCurrentPosition(0);
  Serial.println("Y homing (manuell) ferdig. Y=0.");

  Serial.println("Klar. Venter på (x,y) fra Python...");
}

void loop() {

  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n') {
      stringComplete = true;
      break;
    } else {
      inputString += c;
    }
  }

  if (stringComplete) {
    int commaIndex = inputString.indexOf(',');
    if (commaIndex > 0) {
      String xString = inputString.substring(0, commaIndex);
      String yString = inputString.substring(commaIndex + 1);

      int mouseX = xString.toInt();
      int mouseY = yString.toInt();


      long desiredX = (mouseX - centerX) * scalingFactorX;
      long desiredY = (mouseY - centerY) * scalingFactorY;

      long currentX = stepperX.currentPosition();
      long diff = desiredX - currentX;

      if (diff > STEPS_PER_REV / 2) {
        diff -= STEPS_PER_REV;
      } else if (diff < -STEPS_PER_REV / 2) {
        diff += STEPS_PER_REV;
      }
      long targetX = currentX + diff;


      long targetY = -desiredY;


      stepperX.moveTo(targetX);
      stepperY.moveTo(targetY);
    }

    inputString = "";
    stringComplete = false;
  }


  stepperX.run();
  stepperY.run();
}

void homeXAxis() {
  Serial.println("=== Starter homing av X-aksen...");


  float savedMaxSpd = stepperX.maxSpeed();
  float savedAcc    = stepperX.acceleration();

  stepperX.setMaxSpeed(5000);


  stepperX.setSpeed(2000);
  while (digitalRead(X_LIMIT_PIN) == HIGH) {
    stepperX.runSpeed();
  }

  Serial.println("X-limit trigget. Definerer X=0 der.");
  stepperX.setCurrentPosition(0);

  stepperX.move(-X_BACK_OFF);
  while (stepperX.distanceToGo() != 0) {
    stepperX.run();
  }


  stepperX.setCurrentPosition(0);
  Serial.println("X homing ferdig. X=0 = midt.");


  stepperX.setMaxSpeed(savedMaxSpd);
  stepperX.setAcceleration(savedAcc);
}
