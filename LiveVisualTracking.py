import cv2
import mediapipe as mp
import numpy as np

class FaceTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        cv2.namedWindow('Face Tracking', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Face Tracking', 1280, 720)
        cv2.namedWindow('Settings', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Settings', 400, 600)
        self.mode = 0
        self.modes = ['Mesh', 'Dots']
        self.dot_color = [255, 255, 0]
        self.line_color = [0, 255, 0]
        self.bg_color = [0, 0, 0]
        self.dot_size = 2
        self.line_thickness = 1
        self.connection_types = {
            'TESSELATION': self.mp_face_mesh.FACEMESH_TESSELATION,
            'CONTOURS': self.mp_face_mesh.FACEMESH_CONTOURS,
            'FACE_OVAL': self.mp_face_mesh.FACEMESH_FACE_OVAL,
            'LIPS': self.mp_face_mesh.FACEMESH_LIPS,
            'LEFT_EYE': self.mp_face_mesh.FACEMESH_LEFT_EYE,
            'RIGHT_EYE': self.mp_face_mesh.FACEMESH_RIGHT_EYE
        }
        self.current_connection = 'TESSELATION'
        self.hand_tessellation = self.create_hand_tessellation()
        self.create_trackbars()
        self.ascii_chars = ' .:-=+*#%@'
        
    def on_mode_change(self, value):
        self.mode = value
        
    def update_color(self, target, channel, value):
        if target == 'dot':
            self.dot_color[channel] = value
        elif target == 'line':
            self.line_color[channel] = value
        elif target == 'bg':
            self.bg_color[channel] = value
        
    def create_trackbars(self):
        cv2.createTrackbar('Mode', 'Settings', self.mode, len(self.modes)-1, self.on_mode_change)
        cv2.createTrackbar('Dot R', 'Settings', self.dot_color[2], 255, lambda x: self.update_color('dot', 2, x))
        cv2.createTrackbar('Dot G', 'Settings', self.dot_color[1], 255, lambda x: self.update_color('dot', 1, x))
        cv2.createTrackbar('Dot B', 'Settings', self.dot_color[0], 255, lambda x: self.update_color('dot', 0, x))
        cv2.createTrackbar('Line R', 'Settings', self.line_color[2], 255, lambda x: self.update_color('line', 2, x))
        cv2.createTrackbar('Line G', 'Settings', self.line_color[1], 255, lambda x: self.update_color('line', 1, x))
        cv2.createTrackbar('Line B', 'Settings', self.line_color[0], 255, lambda x: self.update_color('line', 0, x))
        cv2.createTrackbar('BG R', 'Settings', self.bg_color[2], 255, lambda x: self.update_color('bg', 2, x))
        cv2.createTrackbar('BG G', 'Settings', self.bg_color[1], 255, lambda x: self.update_color('bg', 1, x))
        cv2.createTrackbar('BG B', 'Settings', self.bg_color[0], 255, lambda x: self.update_color('bg', 0, x))
        cv2.createTrackbar('Dot Size', 'Settings', self.dot_size, 10, lambda x: setattr(self, 'dot_size', max(1, x)))
        cv2.createTrackbar('Line Width', 'Settings', self.line_thickness, 5, lambda x: setattr(self, 'line_thickness', max(1, x)))
        connection_names = list(self.connection_types.keys())
        cv2.createTrackbar('Connection', 'Settings', 0, len(connection_names)-1, 
                          lambda x: setattr(self, 'current_connection', connection_names[x]))
    
    def create_hand_tessellation(self):
        tessellation = []
        tessellation.extend([
            (0, 1), (0, 5), (0, 9), (0, 13), (0, 17),
            (1, 2), (2, 5), (5, 9), (9, 13), (13, 17),
            (1, 5), (5, 9), (9, 13), (13, 17),
            (0, 2), (0, 6), (0, 10), (0, 14), (0, 18),
        ])
        tessellation.extend([
            (1, 2), (2, 3), (3, 4),
            (1, 3), (2, 4),
        ])
        tessellation.extend([
            (5, 6), (6, 7), (7, 8),
            (5, 7), (6, 8),
        ])
        tessellation.extend([
            (9, 10), (10, 11), (11, 12),
            (9, 11), (10, 12),
        ])
        tessellation.extend([
            (13, 14), (14, 15), (15, 16),
            (13, 15), (14, 16),
        ])
        tessellation.extend([
            (17, 18), (18, 19), (19, 20),
            (17, 19), (18, 20),
        ])
        tessellation.extend([
            (2, 5),
            (5, 9), (9, 13), (13, 17),
            (1, 9), (5, 13), (9, 17),
            (2, 9), (5, 17),
        ])
        return list(set(tessellation))
        
    def update_color(self, target, channel, value):
        if target == 'dot':
            self.dot_color[channel] = value
        elif target == 'line':
            self.line_color[channel] = value
        elif target == 'bg':
            self.bg_color[channel] = value
    
    def draw_mesh(self, output_frame, face_landmarks, frame_shape, hand_results=None):
        for idx, landmark in enumerate(face_landmarks.landmark):
            x = int(landmark.x * frame_shape[1])
            y = int(landmark.y * frame_shape[0])
            cv2.circle(output_frame, (x, y), self.dot_size, tuple(self.dot_color), -1)
        connections = self.connection_types[self.current_connection]
        for connection in connections:
            start_idx = connection[0]
            end_idx = connection[1]
            start_point = face_landmarks.landmark[start_idx]
            end_point = face_landmarks.landmark[end_idx]
            start_x = int(start_point.x * frame_shape[1])
            start_y = int(start_point.y * frame_shape[0])
            end_x = int(end_point.x * frame_shape[1])
            end_y = int(end_point.y * frame_shape[0])
            cv2.line(output_frame, (start_x, start_y), (end_x, end_y), 
                    tuple(self.line_color), self.line_thickness)
        if hand_results and hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    x = int(landmark.x * frame_shape[1])
                    y = int(landmark.y * frame_shape[0])
                    cv2.circle(output_frame, (x, y), self.dot_size, tuple(self.dot_color), -1)
                hand_connections = self.hand_tessellation if self.current_connection == 'TESSELATION' else self.mp_hands.HAND_CONNECTIONS
                for connection in hand_connections:
                    start_idx = connection[0]
                    end_idx = connection[1]
                    if start_idx < len(hand_landmarks.landmark) and end_idx < len(hand_landmarks.landmark):
                        start_point = hand_landmarks.landmark[start_idx]
                        end_point = hand_landmarks.landmark[end_idx]
                        start_x = int(start_point.x * frame_shape[1])
                        start_y = int(start_point.y * frame_shape[0])
                        end_x = int(end_point.x * frame_shape[1])
                        end_y = int(end_point.y * frame_shape[0])
                        cv2.line(output_frame, (start_x, start_y), (end_x, end_y), 
                                tuple(self.line_color), self.line_thickness)
    
    def draw_dots_only(self, output_frame, face_landmarks, frame_shape, hand_results=None):
        for idx, landmark in enumerate(face_landmarks.landmark):
            x = int(landmark.x * frame_shape[1])
            y = int(landmark.y * frame_shape[0])
            cv2.circle(output_frame, (x, y), self.dot_size * 2, tuple(self.dot_color), -1)
        if hand_results and hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    x = int(landmark.x * frame_shape[1])
                    y = int(landmark.y * frame_shape[0])
                    cv2.circle(output_frame, (x, y), self.dot_size * 2, tuple(self.dot_color), -1)

    def update_settings_display(self):
        settings_frame = np.zeros((600, 400, 3), dtype=np.uint8)
        font = cv2.FONT_HERSHEY_SIMPLEX
        y_pos = 30
        cv2.putText(settings_frame, f"Mode: {self.modes[self.mode]}", 
                   (10, y_pos), font, 0.7, (255, 255, 255), 1)
        y_pos += 40
        cv2.putText(settings_frame, f"Connection: {self.current_connection}", 
                   (10, y_pos), font, 0.7, (255, 255, 255), 1)
        y_pos += 40
        cv2.rectangle(settings_frame, (10, y_pos), (40, y_pos + 30), tuple(self.dot_color), -1)
        cv2.putText(settings_frame, "Dot Color", (50, y_pos + 20), font, 0.6, (255, 255, 255), 1)
        y_pos += 40
        cv2.rectangle(settings_frame, (10, y_pos), (40, y_pos + 30), tuple(self.line_color), -1)
        cv2.putText(settings_frame, "Line Color", (50, y_pos + 20), font, 0.6, (255, 255, 255), 1)
        y_pos += 40
        cv2.rectangle(settings_frame, (10, y_pos), (40, y_pos + 30), tuple(self.bg_color), -1)
        cv2.putText(settings_frame, "Background", (50, y_pos + 20), font, 0.6, (255, 255, 255), 1)
        cv2.imshow('Settings', settings_frame)
    
    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            hand_results = None
            if self.mode in [0, 1]:
                hand_results = self.hands.process(rgb_frame)
            output_frame = np.full_like(frame, self.bg_color)
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    if self.mode == 0:
                        self.draw_mesh(output_frame, face_landmarks, frame.shape, hand_results)
                    elif self.mode == 1:
                        self.draw_dots_only(output_frame, face_landmarks, frame.shape, hand_results)
            cv2.imshow('Face Tracking', output_frame)
            self.update_settings_display()
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):
                self.mode = (self.mode + 1) % len(self.modes)
                cv2.setTrackbarPos('Mode', 'Settings', self.mode)
        self.cap.release()
        cv2.destroyAllWindows()
        self.face_mesh.close()
        self.hands.close()

tracker = FaceTracker()
tracker.run()