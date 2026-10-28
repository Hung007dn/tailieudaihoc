int pir = 2;   // Sửa lại cho đúng với sơ đồ Proteus của bạn
int led = 8;   

void setup() {
  pinMode(pir, INPUT);
  pinMode(led, OUTPUT);
  Serial.begin(9600); // Thêm cái này để xem trạng thái trên máy tính
}

void loop() {
  int trangThai = digitalRead(pir); 

  if (trangThai == HIGH) {
    digitalWrite(led, HIGH);   
    Serial.println("Phat hien chuyen dong!");
    delay(2000); // Giữ LED sáng ít nhất 2 giây khi có người
  } else {
    digitalWrite(led, LOW);    
  }
}
