/*
RFID 부분은 예제를 사용하되, 불필요한 부분은 없앰
카드를 첫번째로 태그하면 문이 열림
카드를 두번째로 태그하면 가변저항값을 블루투스로 보내고 문을 닫음
*/

// RFID 핀 정보
/*
 * -----------------------------------------------------------------------------------------
 *             Arduino    
 *             Nano v3    
 * Signal      Pin       
 * -----------------------------------------------------------------------------------------
 * RST/Reset   D9         
 * SPI SS      D10        
 * SPI MOSI    D11      
 * SPI MISO    D12        
 * SPI SCK     D13        
 */

#include <SPI.h> //RFID 해더
#include <MFRC522.h>//RFID 해더
#include <Servo.h> //서보모터 해더
#include <SoftwareSerial.h>//블루투스 해더

int servoPin = 6; //서보모터 핀

Servo servo; //서보모터 변수
SoftwareSerial btSerial(2,3); //블루투스 핀, 2, 3에 연결
int angle = 150; // servo position in degrees 

// SS(Chip Select)과 RST(Reset) 핀 설정
// 나머지 PIN은 SPI 라이브러리를 사용하기에 별도의 설정이 필요없다.
#define SS_PIN 10
#define RST_PIN 9
 
// 라이브러리 생성
MFRC522 rfid(SS_PIN, RST_PIN); // Instance of the class
MFRC522::MIFARE_Key key; 

//이전 ID와 비교하기위한 변수
byte nuidPICC[3];

void setup() { 
  pinMode(4, OUTPUT); //블루투스 enable 핀
  digitalWrite(4,HIGH); // 블루투스 enable on
  btSerial.begin(9600); // 블루투스 bitrate 설정
  Serial.begin(9600);// 시리얼(모니터링)통신 bitrate 설정
  SPI.begin(); // Init SPI bus
  rfid.PCD_Init(); // Init MFRC522 
  servo.attach(servoPin);//서보모터 핀 연결
  //초기 키 ID 초기화
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }

  Serial.println(F("This code scan the MIFARE Classsic NUID."));
  Serial.print(F("Using the following key:"));
  printHex(key.keyByte, MFRC522::MF_KEY_SIZE);
}
 int curState = 1;
 int reading = 0;
void loop() {
  
  // 카드가 인식되었다면 다음으로 넘어가고 아니면 더이상 
  // 실행 안하고 리턴
  if ( ! rfid.PICC_IsNewCardPresent())
    return;

  // ID가 읽혀졌다면 다음으로 넘어가고 아니면 더이상 
  // 실행 안하고 리턴
  if ( ! rfid.PICC_ReadCardSerial())
    return;

  Serial.print(F("PICC type: "));
  //카드의 타입을 읽어온다.
  MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
  //모니터에 출력
  Serial.println(rfid.PICC_GetTypeName(piccType));

  // 만약 바로 전에 인식한 RF 카드와 다르다면..
  if (rfid.uid.uidByte[0] != nuidPICC[0] || 
    rfid.uid.uidByte[1] != nuidPICC[1] || 
    rfid.uid.uidByte[2] != nuidPICC[2] || 
    rfid.uid.uidByte[3] != nuidPICC[3] ) {
    Serial.println(F("A new card has been detected."));
   //원래는 ID를 저장하지만 저장하지 않고 실행하도록 함

    //카드가 인식되면 밑에 문 실행
   //curState로 방향을 전환하도록 함
    curState = -curState;
    if(curState == -1){//문이 열림. angle로 각도를 조절. delay로 속도 조절
      for(angle =100 ; angle > 0; angle--) 
      { 
        servo.write(angle); 
        delay(15); 
      } 
    }
    else{//아날로그 핀0에서 가변저항 값을 가져옴
       //아날로그 값을 블루투스로 보냄
       //문이 닫힘. angle로 각도를 조절. delay로 속도 조절
      reading = analogRead(0);
      btSerial.println(reading);
      Serial.println(reading);
      for(angle = 0; angle < 100; angle++) 
      { 
        servo.write(angle); 
        delay(15); 
      } 
    }
  }
  //바로 전에 인식한 것과 동일하다면
  else Serial.println(F("Card read previously."));

  // PICC 종료
  rfid.PICC_HaltA();

  // 암호화 종료
  rfid.PCD_StopCrypto1();
}
//이 밑은 모니터링과 ID를 저장할 때 사용함. 현재 사용하지 않음

//16진수로 변환하는 함수
void printHex(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
}

//10진수로 변환하는 함수
void printDec(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], DEC);
  }
}
