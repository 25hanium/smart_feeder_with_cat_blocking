#include <Stepper.h>
#include <Servo.h>
#include <DHT11.h>
#include <Adafruit_HX711.h>
#define TRIG 6
#define ECHO 7

const int stepsPerRevolution = 2048;
Stepper myStepper(stepsPerRevolution, 11, 9, 10, 8);
Servo myServo;

const uint8_t DATA_PIN = 13;  // pin for hx711
const uint8_t CLOCK_PIN = 2; // pin for hx711
Adafruit_HX711 hx711(DATA_PIN, CLOCK_PIN);

DHT11 dht11(5);

int infsensor1=A5;
int infvalue1=0;
int infsensor2=A4;
int infvalue2=0;
int infsensor3=A3;
int infvalue3=0;

char c_status = '0';

int32_t weightA128=0;
int32_t scale_para=0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  myStepper.setSpeed(14);
  myServo.attach(12);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  hx711.begin();
  // read and toss 3 values each
  Serial.println("Tareing....");
  for (uint8_t t=0; t<3; t++) {
    hx711.tareA(hx711.readChannelRaw(CHAN_A_GAIN_128));
    hx711.tareA(hx711.readChannelRaw(CHAN_A_GAIN_128));
  }
    for(int i=0;i<10;i++)
  {
   scale_para = hx711.readChannelBlocking(CHAN_A_GAIN_128);
  }
  for(int i=0;i<5;i++)
  {
   scale_para += hx711.readChannelBlocking(CHAN_A_GAIN_128);
  }
  scale_para=scale_para/6;

}

void loop() {
  // put your main code here, to run repeatedly:
  long duration, distance;
  int temperature = 0;
  int humidity = 0;
  c_status = '0';  // 초기값 설정

  int result = dht11.readTemperatureHumidity(temperature, humidity);


  infvalue1=analogRead(infsensor1);
  infvalue2=analogRead(infsensor2);
  infvalue3=analogRead(infsensor3);

  if (Serial.available() > 0) {
    c_status = Serial.read();
  }
  myServo.write(160);

  if (c_status == '1') {

    myStepper.step(stepsPerRevolution);
  } else if (c_status == '2') {

    myStepper.step(stepsPerRevolution * 2);
  } else if (c_status == '3') {

    myStepper.step(stepsPerRevolution * 3);
  } else {
    myServo.write(160);
  }
  if (c_status == '4') {
    myServo.write(0);
  }

  weightA128 = hx711.readChannelBlocking(CHAN_A_GAIN_128)-scale_para;

  
  
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  duration = pulseIn (ECHO, HIGH);

  distance = duration * 17 / 1000; 
  //Serial.println(duration ); 

  Serial.print(c_status);

  if (result == 0) {
        Serial.print(",");
        Serial.print(temperature);
        Serial.print(",");
        Serial.print(humidity);
        Serial.print(",");
    } else {
        // Print error message based on the error code.
        Serial.print(DHT11::getErrorString(result));
    }

  
  Serial.print(infvalue1);
  Serial.print(",");
  Serial.print(infvalue2);
  Serial.print(",");
  Serial.print(infvalue3);
  Serial.print(",");
  Serial.print(weightA128);
  Serial.print(",");
  Serial.print(distance);
  Serial.print("\n");//sending data array : cat_status(is cat on way),temperature,humidity,weight,distance
  //cat status : if 1==open once, 2==open twice, 3==open thrice, 4==close bowl

  delay(1000);
}
