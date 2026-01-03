import cv2
import json
import numpy as np
from datetime import datetime

class ZoneManager:
    def __init__(self):
        self.zones = []
        self.drawing = False
        self.current_points = []
        self.selected_zone_id = -1
        self.editing_mode = False
        self.preview_points = []
        self.zone_colors = [
            (0, 255, 0),    # Green
            (255, 0, 0),    # Blue
            (0, 0, 255),    # Red
            (255, 255, 0),  # Cyan
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Yellow
        ]
    
    def load_zones(self, filename="zones.json"):
        """Load zones from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.zones = data.get('zones', [])
            print(f"Loaded {len(self.zones)} zones from {filename}")
            return True
        except FileNotFoundError:
            print(f"No existing zones file found. Starting fresh.")
            self.zones = []
            return False
        except json.JSONDecodeError:
            print(f"Error reading zones file. Starting fresh.")
            self.zones = []
            return False
    
    def save_zones(self, filename="zones.json"):
        """Save zones to JSON file"""
        try:
            data = {'zones': self.zones}
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Saved {len(self.zones)} zones to {filename}")
            return True
        except Exception as e:
            print(f"Error saving zones: {e}")
            return False
    
    def start_drawing(self, x, y):
        """Start drawing a new zone"""
        self.drawing = True
        self.current_points = [(x, y)]
        self.preview_points = [(x, y)]
    
    def add_point(self, x, y):
        """Add a point to the current zone being drawn"""
        if self.drawing:
            self.current_points.append((x, y))
            self.preview_points = self.current_points.copy()
    
    def finish_drawing(self, x, y):
        """Finish drawing the current zone"""
        if self.drawing and len(self.current_points) >= 3:
            # Add the final point and create the zone
            self.current_points.append((x, y))
            
            zone_id = len(self.zones) + 1
            new_zone = {
                'id': zone_id,
                'name': f'Zone {zone_id}',
                'points': self.current_points,
                'color': self.zone_colors[(zone_id - 1) % len(self.zone_colors)],
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.zones.append(new_zone)
            print(f"Created Zone {zone_id} with {len(self.current_points)} points")
        
        self.drawing = False
        self.current_points = []
        self.preview_points = []
    
    def draw_zones(self, frame, show_labels=True):
        """Draw all zones on the frame"""
        for zone in self.zones:
            points = np.array(zone['points'], np.int32)
            color = zone.get('color', (0, 255, 0))
            
            # Draw filled polygon with transparency
            overlay = frame.copy()
            cv2.fillPoly(overlay, [points], color)
            cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
            
            # Draw polygon outline
            cv2.polylines(frame, [points], True, color, 2)
            
            # Draw zone label
            if show_labels:
                centroid = np.mean(points, axis=0)
                label = zone['name']
                if zone['id'] == self.selected_zone_id:
                    label += " (Selected)"
                
                cv2.putText(frame, label, 
                           (int(centroid[0]) - 30, int(centroid[1])), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw preview (current zone being drawn)
        if self.drawing and len(self.preview_points) > 1:
            preview_color = (255, 255, 255)  # White for preview
            points_array = np.array(self.preview_points, np.int32)
            cv2.polylines(frame, [points_array], False, preview_color, 2)
            
            # Draw points
            for point in self.preview_points:
                cv2.circle(frame, point, 5, preview_color, -1)
        
        return frame
    
    def select_zone(self, x, y):
        """Select a zone based on click position"""
        for zone in self.zones:
            points = np.array(zone['points'], np.int32)
            if cv2.pointPolygonTest(points, (x, y), False) >= 0:
                self.selected_zone_id = zone['id']
                print(f"Selected Zone {zone['id']} - {zone['name']}")
                return zone['id']
        
        self.selected_zone_id = -1
        return -1
    
    def edit_zone(self, new_points):
        """Edit the selected zone with new points"""
        if self.selected_zone_id == -1:
            print("No zone selected for editing")
            return False
        
        for zone in self.zones:
            if zone['id'] == self.selected_zone_id:
                zone['points'] = new_points
                zone['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"Updated Zone {zone['id']} with {len(new_points)} points")
                return True
        
        return False
    
    def delete_zone(self, zone_id=None):
        """Delete a zone"""
        if zone_id is None:
            zone_id = self.selected_zone_id
        
        if zone_id == -1:
            print("No zone selected for deletion")
            return False
        
        for i, zone in enumerate(self.zones):
            if zone['id'] == zone_id:
                deleted_zone = self.zones.pop(i)
                print(f"Deleted Zone {deleted_zone['id']} - {deleted_zone['name']}")
                
                # Reset selection
                self.selected_zone_id = -1
                return True
        
        return False
    
    def clear_all_zones(self):
        """Clear all zones"""
        self.zones = []
        self.selected_zone_id = -1
        print("All zones cleared")
    
    def get_zone_count(self):
        """Get total number of zones"""
        return len(self.zones)