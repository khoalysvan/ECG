import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import pywt
import os

# === CẤU HÌNH ===
CSV_INPUT = 'ecg_data.csv'  # File đầu vào
CSV_OUTPUT = 'ecg_processed1.csv'  # File đầu ra
FS = 100  # Tần số lấy mẫu (Hz), dựa trên delay(10) trong mã ESP32 (~100Hz)
LOWCUT = 5.0  # Tần số cắt thấp (Hz)
HIGHCUT = 40.0  # Tần số cắt cao (Hz)
WAVELET = 'db6'  # Wavelet cho khử nhiễu
LEVEL = 4  # Mức phân rã wavelet

# === HÀM BỘ LỌC THÔNG DẢI ===
def bandpass_filter(signal, fs, lowcut, highcut, order=2):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)

# === HÀM KHỬ NHIỄU WAVELET ===
def wavelet_denoise(signal, wavelet='coif3', level=4, threshold_type='soft'):
    coeffs = pywt.wavedec(signal, wavelet, level=level)
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745
    threshold = sigma * np.sqrt(2 * np.log(len(signal))) * 0.5
    coeffs[1:] = [pywt.threshold(c, threshold, mode=threshold_type) for c in coeffs[1:]]
    try:
        denoised_signal = pywt.waverec(coeffs, wavelet)
        return denoised_signal[:len(signal)]
    except Exception as e:
        print(f"Lỗi tái tạo wavelet: {e}")
        return signal

# === ĐỌC DỮ LIỆU ===
try:
    df = pd.read_csv(CSV_INPUT)
    print("Đã đọc file CSV:")
    print(df.head())
except Exception as e:
    print(f"Lỗi đọc file CSV: {e}")
    exit()

# Kiểm tra cột
if 'Time (s)' not in df.columns or 'ECG' not in df.columns:
    print("File CSV phải có cột 'Time (s)' và 'ECG'")
    exit()

time = df['Time (s)'].values
ecg = df['ECG'].values

# Chuẩn hóa ECG (từ 0-4095 sang mV, giả định 3.3V tương ứng 4095)
ecg_mv = (ecg / 4095.0) * 3.3 * 1000  # Chuyển sang mV

# === LỌC NHIỄU ===
# Bộ lọc thông dải
ecg_filtered = bandpass_filter(ecg_mv, FS, LOWCUT, HIGHCUT)

# Wavelet
ecg_denoised = wavelet_denoise(ecg_filtered, wavelet=WAVELET, level=LEVEL)

# === LƯU DỮ LIỆU XỬ LÝ ===
df_processed = pd.DataFrame({
    'Time (s)': time,
    'ECG_Original (mV)': ecg_mv,
    'ECG_Filtered (mV)': ecg_filtered,
    'ECG_Denoised (mV)': ecg_denoised
})
df_processed.to_csv(CSV_OUTPUT, index=False)
print(f"Dữ liệu đã xử lý lưu vào {CSV_OUTPUT}")

# === HIỂN THỊ TÍN HIỆU ===
plt.figure(figsize=(12, 9))

# Tín hiệu gốc
plt.subplot(3, 1, 1)
plt.plot(time, ecg_mv, label='ECG gốc', color='red')
plt.title('Tín hiệu ECG gốc (từ CSV)')
plt.xlabel('Thời gian (s)')
plt.ylabel('Biên độ (mV)')
plt.legend()
plt.xlim([0, min(10, max(time))])
plt.grid(True)

# Sau lọc thông dải
plt.subplot(3, 1, 2)
plt.plot(time, ecg_filtered, label='ECG sau lọc thông dải', color='blue')
plt.title(f'ECG sau lọc thông dải ({LOWCUT}-{HIGHCUT} Hz)')
plt.xlabel('Thời gian (s)')
plt.ylabel('Biên độ (mV)')
plt.legend()
plt.xlim([0, min(10, max(time))])
plt.grid(True)

# Sau wavelet
plt.subplot(3, 1, 3)
plt.plot(time, ecg_denoised, label='ECG sau khử nhiễu wavelet', color='green')
plt.title(f'ECG sau khử nhiễu Wavelet ({WAVELET}, level={LEVEL})')
plt.xlabel('Thời gian (s)')
plt.ylabel('Biên độ (mV)')
plt.legend()
plt.xlim([0, min(10, max(time))])
plt.grid(True)

plt.tight_layout()
plt.show()

# === THỐNG KÊ ===
print("\nThống kê dữ liệu:")
print(df_processed.describe())