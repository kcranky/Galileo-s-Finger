/*
Arduino Motor Controller
For Arduino-Stellarium integration
Keegan Crankshaw, 2015
http://github.com/KCrankshaw
*/

//Initialize pin variables
const byte xDir = 4;
const byte yDir = 6;

const byte xMotor = 5;
const byte yMotor = 7;

//The total steps the motor has to make
int tSteps = 0;

//data transfer
char t = 'a'; //Needs to be set to a literal
char mot = 't'; //random, not x or y on purpose

//Assuming the device has been aligned
int xPos=0;
int yPos=0;

//Setup Loop
void setup(){
  //To link to the python script
    Serial.begin(9600);
    
  //Configure pins
    pinMode(xDir, OUTPUT);
    pinMode(yDir, OUTPUT);
    pinMode(xMotor, OUTPUT);
    pinMode(yMotor, OUTPUT);
  
  //Set initial direction
    digitalWrite(xDir, LOW);
    digitalWrite(yDir, LOW);

}


void loop() {
 while(Serial.available()) {
   if(Serial.available() >0){
     t = Serial.read();
     
     if (t == 'e' ){
       analyzeInput();
       
     }
     else if(t=='s'){
       tSteps=tSteps+1;
     }
     else if(t=='x' || t=='y'){
       mot = t;
       
     }
   }
 }

}

void analyzeInput(){
  int steps = 0;
  boolean dir = false;

  
  if(mot == 'x'){
    if(max(xPos, tSteps)==xPos){//We're past the position we need to be
      dir = false;
      steps = xPos - tSteps;
      
    }
    else if(max(xPos, tSteps)==tSteps){ //we're before where we need to be
      dir = true;
      steps = tSteps - xPos;
    }
    else if (xPos == tSteps){ //We dont need to step at all!
      steps =0;
    }
    
    xPos = tSteps;//update the position of the motor
    tSteps = 0;
    stepMotor(xMotor, dir, int(steps));
  }
  
  if(mot=='y'){
    if(max(yPos, tSteps)==yPos){//We're past the position we need to be
      dir = false;
    steps = yPos - tSteps;
      
    }
    else if(max(yPos, tSteps)==tSteps){ //we're before where we need to be
      dir = true;
      steps = tSteps - yPos;
    }
    else if (yPos == tSteps){ //We dont need to step at all!
      steps =0;
    }
    
    yPos = tSteps;//update the position of the motor
    tSteps = 0;
    stepMotor(yMotor, dir, steps);
  }
  
}

//Step the motor
//NB: THERE ARE 400 STEPS ON THE MOTOR USED - MAP TO THE CORRECT AMOUNT
void stepMotor(byte motor, boolean dir, int amount){
  //Set the correct direction
  if(motor == xMotor)
    digitalWrite(xDir, dir);
  else
    digitalWrite(yDir, dir);
    
  //Step the motor  
  for(int i=0;i<amount;i++){
    digitalWrite(motor, HIGH);
    digitalWrite(motor, LOW);
    delay(38);
  }
  
}
