import time
import threading
import queue
import cv2 as cv

class VisionWorker(threading.Thread):
    def __init__(self, path_cam, yolo_model, conf, imgsz):
        super().__init__(daemon=True)
        self.path_cam = path_cam
        self.model = yolo_model
        self.conf = conf
        self.imgsz = imgsz

        self.stop_evt = threading.Event()
        self.search_evt = threading.Event()

        #result
        self.det_q = queue.Queue(maxsize=1)

        self.cap = None

        self.frame_center = None
        self.latest_frame = None
        self.frame_lock = threading.Lock()

    def run(self):
        self.cap = cv.VideoCapture(self.path_cam)
        
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

        while not self.stop_evt.is_set() and self.cap.isOpened():

            if self.search_evt.is_set():
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    time.sleep(0.01)
                    continue

                with self.frame_lock:
                    self.latest_frame = frame.copy()
                    
                frame_height, frame_width = frame.shape[:2]
                self.frame_center = frame_width / 2

                if self.search_evt.is_set():
                    with self.frame_lock:
                        img = self.latest_frame.copy()

                #searcning cubes
                results = self.model(img, conf=self.conf, imgsz=self.imgsz, verbose=False)
                r0 = results[0]

                det = None
                #bbox result with max conf
                if r0.boxes is not None and len(r0.boxes) > 0:
                    confs = r0.boxes.conf
                    best_i = int(confs.argmax().item())
                    xyxy = r0.boxes.xyxy[best_i].tolist()
                    conf = confs[best_i].item()
                    det = (xyxy, conf, time.time())

                    #debug
                    if det is not None:
                        dbg = img.copy()
                        x1, y1, x2, y2 = map(int, xyxy)
                        cv.rectangle(dbg, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv.putText(dbg, f"{conf:.3f}", (x1, max(20, y1 - 10)),
                        cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv.imwrite(f"/tmp/det_{int(time.time()*1000)}.jpg", dbg)

                    if self.det_q.full():
                        try: self.det_q.get_nowait()
                        except queue.Empty: pass
                self.det_q.put(det)

                #stop searching
                self.search_evt.clear()
            
            time.sleep(0.002)

        self.cap.release()

    def start_search(self):
        while not self.det_q.empty():
            try:
                self.det_q.get_nowait()
            except queue.Empty:
                break
        self.search_evt.set()

    def get_det(self):
        try:
            return self.det_q.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        self.search_evt.clear()
        self.stop_evt.set()

        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass

    def flush_camera(self, n=10):
        if self.cap is None:
            return
        for _ in range(n):
            self.cap.grab()