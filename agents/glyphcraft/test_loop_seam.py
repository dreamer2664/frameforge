import subprocess, json
import numpy as np
import cv2

loop_path = "frameforge/agents/glyphcraft/renders/loop.mp4"

# Read first frame (0.0s) and last frame (10.0s)
cap = cv2.VideoCapture(loop_path)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"Loop total frames: {total_frames}")

ret, frame_first = cap.read()
assert ret, "Failed to read first frame"

cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
ret, frame_last = cap.read()
assert ret, "Failed to read last frame"
cap.release()

# Calculate pixel difference
diff = cv2.absdiff(frame_first, frame_last)
mae = np.mean(diff)
max_diff = np.max(diff)
print(f"Loop seam difference: MAE = {mae:.4f}, MAX = {max_diff}")

# Save seam comparison
comp = np.hstack([frame_first, frame_last, diff * 10])
cv2.imwrite("frameforge/agents/glyphcraft/work/inspection/loop_seam_check.jpg", comp)
print("Saved loop seam comparison image.")
