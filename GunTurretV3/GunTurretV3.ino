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

// Opprett AccelStepper-objekter (DRIVER-modus)
AccelStepper stepperX(AccelStepper::DRIVER, X_STEP_PIN, X_DIR_PIN);
AccelStepper stepperY(AccelStepper::DRIVER, Y_STEP_PIN, Y_DIR_PIN);

// Skalafaktorer for musepiksel -> steg
const float scalingFactorX = 2.3; 
const float scalingFactorY = 2.1;

// Midtpunkt for webkamera (640x480 => 320,240)
const int centerX = 320;
const int centerY = 240;

// Konstant: antall steg vi vil trekke inn etter limit for å få X-aksen i midten.
const long X_BACK_OFF = 2165;  

// For Y-aksen: kjør 1100 steg opp fra bunn.
const long Y_START_UP = 500; 

// Her definerer du antall steg for en full rotasjon for turret’en.
// Juster denne verdien til ditt system!
const long STEPS_PER_REV = 10000;

// Buffer for seriekommando
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

  // Stegparametere
  stepperX.setMaxSpeed(9000);
  stepperX.setAcceleration(115000);

  stepperY.setMaxSpeed(9000);
  stepperY.setAcceleration(115000);

  // Home X-aksen
  homeXAxis();

  // Kjør Y fra bunn -> 1100 steg opp => definer Y=0
  stepperY.setCurrentPosition(0);  // Antar Y=0 = bunn
  stepperY.move(Y_START_UP);       // Kjører +1100 steg
  while (stepperY.distanceToGo() != 0) {
    stepperY.run();
  }
  // Sett Y=0 ved "horisontal"
  stepperY.setCurrentPosition(0);
  Serial.println("Y homing (manuell) ferdig. Y=0.");

  Serial.println("Klar. Venter på (x,y) fra Python...");
}

void loop() {
  // 1) Les serie – drener alle tilgjengelige kommandoer slik at
  //    kun den siste kommandoen blir behandlet.
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n') {
      stringComplete = true;
      break;
    } else {
      inputString += c;
    }
  }

  // 2) Parse "x,y" og oppdater målposisjon
  if (stringComplete) {
    int commaIndex = inputString.indexOf(',');
    if (commaIndex > 0) {
      String xString = inputString.substring(0, commaIndex);
      String yString = inputString.substring(commaIndex + 1);

      int mouseX = xString.toInt();
      int mouseY = yString.toInt();

      // Beregn ønsket posisjon (lineært) ut fra museposisjonen:
      long desiredX = (mouseX - centerX) * scalingFactorX;
      long desiredY = (mouseY - centerY) * scalingFactorY;

      // --- For X-aksen: Beregn korteste vei til den nye posisjonen ---
      long currentX = stepperX.currentPosition();
      long diff = desiredX - currentX;
      // Hvis differansen er større enn halv omdreining, juster:
      if (diff > STEPS_PER_REV / 2) {
        diff -= STEPS_PER_REV;
      } else if (diff < -STEPS_PER_REV / 2) {
        diff += STEPS_PER_REV;
      }
      long targetX = currentX + diff;

      // For Y-aksen beholder vi den opprinnelige beregningen (merk -desiredY som tidligere)
      long targetY = -desiredY;

      // Oppdater mål for steppermotorene
      stepperX.moveTo(targetX);
      stepperY.moveTo(targetY);
    }
    // Nullstill buffer og flagg
    inputString = "";
    stringComplete = false;
  }

  // 3) Kjør steppermotorene
  stepperX.run();
  stepperY.run();
}

// -----------------------------------------------------------
// Homing X: 
// 1) Kjører i + retning til limit-bryter trigges (X_LIMIT_PIN blir LOW)
// 2) Definerer X=0
// 3) Kjører X_BACK_OFF steg for å komme til midten
// 4) Setter X=0 i midten
// -----------------------------------------------------------
void homeXAxis() {
  Serial.println("=== Starter homing av X-aksen...");

  // Lagre midlertidige parametere
  float savedMaxSpd = stepperX.maxSpeed();
  float savedAcc    = stepperX.acceleration();

  stepperX.setMaxSpeed(5000);

  // Kjører i + retning til bryter trigges
  stepperX.setSpeed(2000);
  while (digitalRead(X_LIMIT_PIN) == HIGH) {
    stepperX.runSpeed();
  }

  // Bryteren trigget => sett X=0
  Serial.println("X-limit trigget. Definerer X=0 der.");
  stepperX.setCurrentPosition(0);

  stepperX.move(-X_BACK_OFF);
  while (stepperX.distanceToGo() != 0) {
    stepperX.run();
  }

  // Sett X=0 i midten
  stepperX.setCurrentPosition(0);
  Serial.println("X homing ferdig. X=0 = midt.");

  // Gjenopprett parametere
  stepperX.setMaxSpeed(savedMaxSpd);
  stepperX.setAcceleration(savedAcc);
}
