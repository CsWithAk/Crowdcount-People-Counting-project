import cv2
import numpy as np
from camera_feed import CameraFeed
from zones import ZoneManager

class CrowdCountApp:
    def __init__(self):
        self.camera = CameraFeed()
        self.zone_manager = ZoneManager()
        self.current_frame = None
        self.mode = "view"  # Modes: view, draw, edit
        self.show_info = True
        
    def setup_mouse_callbacks(self):
        """Setup mouse callback for zone drawing"""
        cv2.namedWindow('Crowd Count - Zone Management')
        cv2.setMouseCallback('Crowd Count - Zone Management', self.mouse_callback)
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for zone drawing and selection"""
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.mode == "draw":
                self.zone_manager.start_drawing(x, y)
            elif self.mode == "edit":
                self.zone_manager.select_zone(x, y)
                
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.mode == "draw" and self.zone_manager.drawing:
                self.zone_manager.add_point(x, y)
                
        elif event == cv2.EVENT_LBUTTONUP:
            if self.mode == "draw" and self.zone_manager.drawing:
                self.zone_manager.finish_drawing(x, y)
                self.zone_manager.save_zones()
    
    def add_frame_info(self, frame):
        """Add frame information overlay"""
        if not self.show_info:
            return frame
            
        # Add frame counter and mode info
        info_text = [
            f"Mode: {self.mode.upper()}",
            f"Zones: {self.zone_manager.get_zone_count()}",
            f"Selected Zone: {self.zone_manager.selected_zone_id if self.zone_manager.selected_zone_id != -1 else 'None'}",
            "Controls:",
            "D - Draw Mode | E - Edit Mode | V - View Mode",
            "S - Save Zones | C - Clear All | Q - Quit",
            "1-6 - Select Zone | DEL - Delete Selected"
        ]
        
        y_offset = 30
        for i, text in enumerate(info_text):
            color = (255, 255, 255) if i < 3 else (200, 200, 100)
            font_size = 0.5 if i >= 3 else 0.6
            cv2.putText(frame, text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_size, color, 1)
            y_offset += 25 if i < 3 else 20
            
        return frame
    
    def handle_keypress(self, key):
        """Handle keyboard input"""
        # Mode switching
        if key == ord('d'):
            self.mode = "draw"
            print("Switched to DRAW mode - Click to draw zone points")
        elif key == ord('e'):
            self.mode = "edit"
            print("Switched to EDIT mode - Click to select zones")
        elif key == ord('v'):
            self.mode = "view"
            print("Switched to VIEW mode")
            
        # Zone management
        elif key == ord('s'):
            self.zone_manager.save_zones()
        elif key == ord('c'):
            self.zone_manager.clear_all_zones()
            self.zone_manager.save_zones()
            
        # Zone selection (1-6 keys)
        elif ord('1') <= key <= ord('6'):
            zone_id = key - ord('1') + 1
            if zone_id <= self.zone_manager.get_zone_count():
                self.zone_manager.selected_zone_id = zone_id
                print(f"Selected Zone {zone_id}")
                
        # Delete selected zone
        elif key == 8 or key == 255:  # Delete key
            if self.zone_manager.selected_zone_id != -1:
                self.zone_manager.delete_zone()
                self.zone_manager.save_zones()
                
        # Toggle info display
        elif key == ord('i'):
            self.show_info = not self.show_info
            
        return key != ord('q')  # Continue if not 'q'
    
    def run(self):
        """Main application loop"""
        print("Initializing Crowd Count - Milestone 1")
        print("=" * 50)
        
        # Start camera
        if not self.camera.start_camera():
            print("Failed to start camera. Exiting.")
            return
        
        # Load existing zones
        self.zone_manager.load_zones()
        
        # Setup mouse callbacks
        self.setup_mouse_callbacks()
        
        print("\nApplication Started!")
        print("Draw zones by pressing 'D' and clicking points")
        print("Press 'Q' to quit\n")
        
        # Main loop
        while True:
            # Read frame
            ret, frame = self.camera.read_frame()
            if not ret:
                break
            
            self.current_frame = frame.copy()
            
            # Draw zones on frame
            frame_with_zones = self.zone_manager.draw_zones(self.current_frame)
            
            # Add frame information
            frame_with_info = self.add_frame_info(frame_with_zones)
            
            # Display frame
            cv2.imshow('Crowd Count - Zone Management', frame_with_info)
            
            # Handle keypress
            key = cv2.waitKey(1) & 0xFF
            if not self.handle_keypress(key):
                break
        
        # Cleanup
        self.zone_manager.save_zones()
        self.camera.stop_camera()
        print("Application closed successfully")

if __name__ == "__main__":
    app = CrowdCountApp()
    app.run()