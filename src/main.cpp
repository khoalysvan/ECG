#include <Arduino.h>

// Cấu hình AD8232
#define ECG_PIN 34 // GPIO 34 (VP)
#define LO_PLUS 4
#define LO_MINUS 2

// Biến toàn cục
int ecg_value = 0;
float heart_rate = 0;
unsigned long last_beat = 0;
int threshold = 2000; // Ngưỡng phát hiện đỉnh R
bool peak_detected = false;
unsigned long start_time = 0;

// Tính nhịp tim từ ECG
void calculateHeartRate(int ecg_value)
{
  if (ecg_value > threshold && !peak_detected)
  {
    unsigned long current_time = millis();
    if (last_beat > 0)
    {
      float interval = (current_time - last_beat) / 1000.0; // giây
      heart_rate = 60.0 / interval;                         // bpm
      Serial.print("Heart Rate: ");
      Serial.print(heart_rate);
      Serial.println(" bpm");
    }
    last_beat = current_time;
    peak_detected = true;
  }
  else if (ecg_value < threshold - 100)
  {
    peak_detected = false;
  }
}

void setup()
{
  Serial.begin(115200);
  delay(1000); // Chờ Serial ổn định
  pinMode(LO_PLUS, INPUT);
  pinMode(LO_MINUS, INPUT);
  start_time = millis();
}

void loop()
{
  unsigned long current_time = millis() - start_time; // Thời gian tương đối (ms)

  // Đọc ECG
  if (digitalRead(LO_PLUS) == 1 || digitalRead(LO_MINUS) == 1)
  {
    Serial.println("Leads Off!");
    ecg_value = 0;
  }
  else
  {
    ecg_value = analogRead(ECG_PIN);
    calculateHeartRate(ecg_value);
  }

  // Gửi dữ liệu qua Serial
  Serial.print(current_time / 1000.0, 3); // Thời gian (giây)
  Serial.print(",");
  Serial.println(ecg_value);

  delay(0.125); // Lấy mẫu ~100Hz
}