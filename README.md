# Robot Turret med Homing & GUI

Dette prosjektet demonstrerer en steppermotor‐drevet “turret” (eller robotarm) med:

1. **Homing av X‐aksen** ved oppstart (finner endestopp) og kjører til midtposisjon.  
2. **Y‐aksen** starter fysisk nederst, kjører 1100 steg opp for en “horisontal” start.  
3. **GUI i Python** (Tkinter) som viser webkamerabilde og har ulike “modus”:  
   - **Museklikk** (klikk i bilde => `(x,y)` til Arduino)  
   - **Musebevegelse** (flytt musen => `(x,y)` til Arduino)  
   - **Objektdeteksjon** (f.eks. “blå gjenstand” i kamera => `(cx, cy)` til Arduino)

Arduino‐koden mottar \((x,y)\) og oversetter disse til steg‐posisjoner for X og Y, med limit switch på X og manuell startposisjon for Y.

---

## Innhold

1. [Oversikt](#oversikt)  
2. [Maskinvare](#maskinvare)  
3. [Programvare & Filer](#programvare--filer)  
4. [Oppsett & Kjøring](#oppsett--kjøring)  
5. [Bilder](#bilder)  

---

## Oversikt

- **Homing**:  
  - X kjører i positiv retning til bryter trigges. Setter X=0 i den posisjonen, kjører innover 1450 steg, setter X=0 i midten.  
  - Y kjører 1100 steg opp fra bunn, setter Y=0 der.

- **GUI**:  
  - Viser webkamera i en tkinter‐Label.  
  - Knapp for “Mouse Click Tracking”: Ved klikk i video => `(x,y)` seriellsendes til Arduino.  
  - Knapp for “Mouse Move Tracking”: Musebevegelse i video => `(x,y)` seriellsendes.  
  - Knapp for “Object Detection”: Finner “blå” konturer, tegner rektangel, sender senter `(cx, cy)` til Arduino.  

På Arduino‐siden tolkes `(x,y)` i 640×480 (typisk), regner `(x-320)*scaleX`, `(240-y)*scaleY`, og kjører stepperne med AccelStepper.

---

## Maskinvare

1. **Arduino uno wifi** 
2. **2x Stepperdrivere** (TMC2209),  
3. **To steppermotorer** (Nema 17).  
4. **Limit switch** på X (NO->pin7, COM->GND).  
5. **12/24V strømforsyning**  
6. **gt2 reim / tannhjul** for X og Y



