import serial
import pandas as pd
import time
import os

# Cấu hình
SERIAL_PORT = 'COM5'  # Thay bằng cổng Serial
BAUD_RATE = 115200
CSV_FILE = 'ecg_data.csv'
DURATION = 30  # Thời gian ghi (giây)

# Khởi tạo Serial
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
except Exception as e:
    print(f"Lỗi mở cổng Serial: {e}")
    exit()

# Khởi tạo danh sách lưu dữ liệu
data = {'Time (s)': [], 'ECG': []}

# Bắt đầu ghi dữ liệu
print(f"Bắt đầu ghi dữ liệu ECG trong {DURATION} giây...")
start_time = time.time()

while (time.time() - start_time) < DURATION:
    try:
        line = ser.readline().decode('utf-8').strip()
        if line and ',' in line:
            parts = line.split(',')
            if len(parts) == 2:
                try:
                    t = float(parts[0])
                    ecg = int(parts[1])
                    data['Time (s)'].append(t)
                    data['ECG'].append(ecg)
                    print(f"Time: {t:.3f}s, ECG: {ecg}")
                except ValueError:
                    continue
        elif "Leads Off" in line:
            print("Leads Off!")
            data['Time (s)'].append((time.time() - start_time))
            data['ECG'].append(0)
        elif "Heart Rate" in line:
            print(line)
    except Exception as e:
        print(f"Lỗi đọc Serial: {e}")

# Đóng Serial
ser.close()

# Lưu vào CSV
df = pd.DataFrame(data)
df.to_csv(CSV_FILE, index=False)
print(f"Dữ liệu ECG lưu vào {CSV_FILE}")

# Hiển thị thông tin
print("\nThống kê dữ liệu:")
print(df.describe())