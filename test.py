import cv2
import os

# Đường dẫn đến file video
video_path = "assets/videos/knee_raise.mov"

# Kiểm tra file tồn tại
if not os.path.exists(video_path):
    print(f"Error: File {video_path} not found.")
    exit()

# Mở video
cap = cv2.VideoCapture(video_path)

# Kiểm tra xem video có mở được không
if not cap.isOpened():
    print(f"Error: Could not open video {video_path}")
    exit()

# Lấy thông tin video
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Video resolution: {width}x{height}, FPS: {fps}")

# Đọc và hiển thị video
while True:
    ret, frame = cap.read()
    if not ret:
        print("End of video or error reading frame.")
        break
    # Hiển thị frame
    cv2.imshow('Video Test', frame)
    # Dừng khi nhấn phím bất kỳ
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()