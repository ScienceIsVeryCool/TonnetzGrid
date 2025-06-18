import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import numpy as np
import threading
import time # Import time for pauses
from collections import defaultdict

# For audio - you'll need to install: pip install pygame
try:
    import pygame
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    AUDIO_AVAILABLE = True
except ImportError:
    print("Warning: pygame not available. Install with: pip install pygame")
    AUDIO_AVAILABLE = False

class TonnetzGrid:
    def __init__(self, rows=7, cols=12):
        """
        Create a proper Tonnetz grid where:
        - Horizontal movement = Perfect 5th (7 semitones)
        - Diagonal NE movement = Major 3rd (4 semitones)
        - Diagonal SE movement = Minor 3rd (3 semitones)
        """
        self.rows = rows
        self.cols = cols
        
        # Musical constants
        self.pitch_classes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.enharmonics = {
            'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 'G#': 'Ab', 'A#': 'Bb',
            'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'
        }
        
        # A4 = 440Hz, calculate frequencies for all notes
        self.note_frequencies = {}
        a4_freq = 440.0
        a4_midi = 69
        
        for octave in range(9):
            for i, note in enumerate(self.pitch_classes):
                midi_number = (octave + 1) * 12 + i
                freq = a4_freq * (2 ** ((midi_number - a4_midi) / 12))
                self.note_frequencies[f"{note}{octave}"] = freq
        
        # Audio system for continuous playback
        self.playing_notes = {}  # note -> pygame.mixer.Channel
        self.note_sounds = {}    # note -> pygame.mixer.Sound
        self.audio_lock = threading.Lock()
        
        # Initialize the plot elements
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        self.hexagons = {}
        self.note_positions = defaultdict(list)  # Note can appear multiple times
        self.active_notes = set()  # Currently active (toggled on) notes
        self.chord_highlights = set()  # Notes highlighted by chord selection
        self.chord_triangles = []
        
        # Mouse dragging state
        self.is_dragging = False
        self.drag_toggle_state = None  # True = turning on, False = turning off
        self.already_toggled = set()  # Track which hexes were toggled in current drag
        
        # Tonnetz grid storage (will be populated later after sounds are ready)
        self.grid = {}  # (row, col) -> pitch class
        
        # Loading screen elements
        self.loading_text = None
        self.loading_symbol = None
        self.loading_messages = [
            "♪ Generating 60 seconds of pure musical bliss per note...",
            "♫ Teaching AI to sing in 12 different keys...", 
            "♪ Calculating the optimal sine wave curves...",
            "♫ Warming up the virtual vocal cords...",
            "♪ Tuning the mathematical guitars...",
            "♫ Loading piano keys from the cloud...",
            "♪ Inflating digital brass instruments...",
            "♫ Synchronizing quantum drum beats...",
            "♪ Stretching virtual violin strings...",
            "♫ Buffering the frequency spectrum...",
            "♪ Downloading more cowbell...",
            "♫ Converting coffee into audio waves..."
        ]
        self.current_message_idx = 0

        # Flag to indicate when pre-generation is complete
        self.sounds_pregenerated_event = threading.Event()

        # Call show_loading_screen first thing to ensure it gets drawn
        self.show_loading_screen()
        # Force a draw and flush events to make sure the loading screen appears immediately
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        
        # Start the sound pre-generation in a separate thread
        # This allows the main thread to remain responsive for GUI updates (like the loading screen)
        threading.Thread(target=self._run_pregeneration_task, daemon=True).start()

    def _run_pregeneration_task(self):
        """
        This method is run in a separate thread to perform the long-running
        sound pre-generation and then signal completion to the main thread.
        """
        print("Starting sound pre-generation...")
        self.pregenerate_sounds()
        print("Sound pre-generation complete.")
        # Set the event to signal that sounds are ready
        self.sounds_pregenerated_event.set()
        
        # After sounds are ready, schedule the main grid creation and hiding of loading screen
        # Use a simple lambda that takes no arguments and calls the setup method.
        self.fig.canvas.get_tk_widget().after_idle(self._post_generation_setup)
        
    def _post_generation_setup(self):
        """
        This method is called on the main GUI thread after sounds are pre-generated.
        It creates the main Tonnetz grid and hides the loading screen.
        """
        if not self.sounds_pregenerated_event.is_set():
            return
            
        print("Performing post-generation setup (creating grid, hiding loading screen)...")
        # Create the main Tonnetz grid data structure
        self.create_tonnetz_grid()
        
        # Hide the loading screen. This will also clear the axes and call create_hexagons.
        self.hide_loading_screen()
        print("Post-generation setup complete.")

    def show_loading_screen(self):
        """Show a simple loading screen"""
        self.ax.clear()
        self.ax.set_facecolor('#1a1a1a')
        self.ax.set_aspect('equal')
        
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-2, 2)
        
        # Add main loading text
        self.loading_text = self.ax.text(0, 0.5, self.loading_messages[0], 
                                       ha='center', va='center', 
                                       fontsize=14, color='white', 
                                       bbox=dict(boxstyle="round,pad=0.5", 
                                               facecolor='purple', alpha=0.8))
        
        # Add simple music symbol
        self.loading_symbol = self.ax.text(0, -0.5, "♪ ♫ ♪", ha='center', va='center',
                                         fontsize=40, color='gold')
        
        # Add title using simple symbols
        self.ax.text(0, 1.5, "♪ LOADING MUSICAL UNIVERSE ♪", 
                    ha='center', va='center', fontsize=16, 
                    color='cyan', fontweight='bold')
    
    def hide_loading_screen(self):
        """Hide the loading screen and restore the normal view"""
        # Clear loading elements
        if self.loading_text:
            self.loading_text.remove()
        if self.loading_symbol:
            self.loading_symbol.remove()
        self.loading_text = None
        self.loading_symbol = None
        
        # Restore the normal plot by clearing and re-drawing the main elements
        self.ax.clear()
        self.setup_plot() # Setup the main plot title and styling
        self.create_hexagons() # Re-add all hexagon patches and labels
        self.fig.canvas.draw() # Final draw for the main content
        self.fig.canvas.flush_events() # Flush events for the final display
    
    def pregenerate_sounds(self):
        """Pre-generate long sound loops for each note (long-running task)"""
        if not AUDIO_AVAILABLE:
            return
            
        for note in self.pitch_classes:
            note_key = f"{note}4"  # Use octave 4
            if note_key in self.note_frequencies:
                frequency = self.note_frequencies[note_key]
                audio_data = self.generate_long_tone(frequency, duration=60.0)
                if audio_data is not None:
                    try:
                        sound = pygame.sndarray.make_sound(audio_data)
                        self.note_sounds[note] = sound
                    except Exception as e:
                        print(f"Error creating sound for {note}: {e}")
    
    def pitch_class_to_index(self, note):
        """Convert note name to pitch class index (0-11)"""
        if note in self.enharmonics:
            alternatives = [note, self.enharmonics[note]]
        else:
            alternatives = [note]
            
        for alt in alternatives:
            if alt in self.pitch_classes:
                return self.pitch_classes.index(alt)
        return 0
    
    def index_to_pitch_class(self, index):
        """Convert pitch class index to note name"""
        return self.pitch_classes[index % 12]
    
    def create_tonnetz_grid(self):
        """Create the proper Tonnetz pitch relationships"""
        # Start with C in the middle
        start_row = self.rows // 2
        start_col = self.cols // 2
        self.grid[(start_row, start_col)] = 0  # C
        
        # Build the grid based on Tonnetz relationships
        for row in range(self.rows):
            for col in range(self.cols):
                if row == start_row and col == start_col:
                    continue
                    
                # Calculate pitch class based on position
                row_offset = row - start_row
                col_offset = col - start_col
                
                if col % 2 == 0:  # Even columns
                    pitch_index = (7 * col_offset + 4 * row_offset) % 12
                else:  # Odd columns are offset down
                    pitch_index = (7 * col_offset + 4 * (row_offset - 0.5)) % 12
                    pitch_index = int(pitch_index) % 12
                
                self.grid[(row, col)] = pitch_index
    
    def hex_corners(self, x, y, size=0.5):
        """Calculate pointy-topped hexagon corners"""
        angles = np.linspace(0, 2*np.pi, 7)
        corners_x = x + size * np.cos(angles)
        corners_y = y + size * np.sin(angles)
        return list(zip(corners_x, corners_y))
    
    def setup_plot(self):
        """Setup the matplotlib plot for the main grid display"""
        plt.rcParams['keymap.fullscreen'] = []
        plt.rcParams['keymap.quit'] = ['ctrl+w', 'cmd+w']
        
        self.ax.set_aspect('equal')
        self.ax.set_title('Interactive Tonnetz Grid\n→ = Perfect 5th, ↗ = Major 3rd, ↘ = Minor 3rd', 
                         fontsize=16, pad=20, color='white')
        self.ax.set_facecolor('#1a1a1a')
        self.fig.patch.set_facecolor('#0a0a0a')
        
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        
        instructions = ("Click to toggle notes ON/OFF | Drag to paint multiple notes\n"
                       "Keys: C,D,E,F,G,A,B = Major chords | c,d,e,f,g,a,b = Minor chords | Space = Clear all")
        self.fig.text(0.5, 0.02, instructions, ha='center', va='bottom', 
                     color='lightgray', fontsize=11)
    
    def create_hexagons(self):
        """Create hexagonal grid with PERFECT tessellation for pointy-topped hexagons"""
        hex_size = 0.5

        self.hexagons = {}
        self.note_positions.clear()

        h_spacing = hex_size * np.sqrt(3) * 0.93
        v_spacing = hex_size * 1.7
        
        for (row, col), pitch_index in self.grid.items():
            x = col * h_spacing
            y = row * v_spacing
            
            if col % 2 == 1:
                y += v_spacing / 2
            
            note = self.index_to_pitch_class(pitch_index)
            
            colors = plt.cm.hsv(np.linspace(0, 1, 12))
            color_index = (pitch_index * 7) % 12
            base_color = colors[color_index]
            
            corners = self.hex_corners(x, y, hex_size)
            hex_patch = patches.Polygon(corners, closed=True, 
                                      facecolor=base_color, 
                                      edgecolor='white', 
                                      linewidth=2, 
                                      alpha=0.6,
                                      picker=True)
            
            self.ax.add_patch(hex_patch)
            self.hexagons[(row, col)] = {
                'patch': hex_patch, 
                'note': note, 
                'pitch_index': pitch_index,
                'position': (x, y),
                'base_color': base_color,
                'active': False
            }
            self.note_positions[note].append((row, col))
            
            self.ax.text(x, y, note, ha='center', va='center', 
                        fontsize=14, fontweight='bold', color='white',
                        bbox=dict(boxstyle="round,pad=0.2", facecolor='black', alpha=0.5))
        
        x_coords = [h['position'][0] for h in self.hexagons.values()]
        y_coords = [h['position'][1] for h in self.hexagons.values()]
        padding = 1
        self.ax.set_xlim(min(x_coords) - padding, max(x_coords) + padding)
        self.ax.set_ylim(min(y_coords) - padding, max(y_coords) + padding)

        self.update_active_notes_display()
    
    def generate_long_tone(self, frequency, duration=60.0, sample_rate=22050):
        """Generate a long sine wave tone with harmonics for seamless looping"""
        if not AUDIO_AVAILABLE:
            return None
            
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        harmonics = [(1.0, 1), (0.5, 2), (0.3, 3), (0.2, 4)]
        
        for i in range(frames):
            sample = 0
            for amp, mult in harmonics:
                sample += amp * np.sin(2 * np.pi * frequency * mult * i / sample_rate)
            sample /= len(harmonics)
            
            arr[i][0] = sample
            arr[i][1] = sample
        
        arr = np.clip(arr * 15000, -32767, 32767).astype(np.int16)
        return arr
    
    def update_active_notes_display(self):
        """Ensures that the visual state of active notes is correctly restored after a redraw."""
        for (row, col) in self.active_notes:
            if (row, col) in self.hexagons:
                hex_data = self.hexagons[(row, col)]
                hex_data['patch'].set_facecolor('white')
                hex_data['patch'].set_alpha(1.0)
    
    def start_continuous_note(self, note):
        """Start playing a note continuously using long sample loop"""
        if not AUDIO_AVAILABLE or note not in self.note_sounds:
            print(f"Playing note: {note}")
            return
            
        with self.audio_lock:
            if note not in self.playing_notes:
                try:
                    channel = pygame.mixer.find_channel()
                    if channel:
                        channel.play(self.note_sounds[note], loops=-1)
                        self.playing_notes[note] = channel
                        print(f"Started playing {note}")
                except Exception as e:
                    print(f"Error starting {note}: {e}")
    
    def stop_continuous_note(self, note):
        """Stop playing a note"""
        if not AUDIO_AVAILABLE:
            return
            
        with self.audio_lock:
            if note in self.playing_notes:
                try:
                    self.playing_notes[note].stop()
                    del self.playing_notes[note]
                    print(f"Stopped playing {note}")
                except Exception as e:
                    print(f"Error stopping {note}: {e}")
    
    def toggle_note(self, row, col, play_sound=True):
        """Toggle a note on/off"""
        hex_data = self.hexagons[(row, col)]
        note = hex_data['note']
        
        if (row, col) in self.active_notes:
            self.active_notes.remove((row, col))
            hex_data['active'] = False
            hex_data['patch'].set_facecolor(hex_data['base_color'])
            hex_data['patch'].set_alpha(0.6)
            if play_sound:
                self.stop_continuous_note(note)
        else:
            self.active_notes.add((row, col))
            hex_data['active'] = True
            hex_data['patch'].set_facecolor('white')
            hex_data['patch'].set_alpha(1.0)
            if play_sound:
                self.start_continuous_note(note)
        
        self.fig.canvas.draw_idle()
    
    def highlight_chord(self, root, quality='major'):
        """Highlight a chord and show the triangle"""
        self.clear_chord_highlights()
        
        root_index = self.pitch_class_to_index(root)
        
        if quality == 'major':
            chord_indices = [root_index, (root_index + 4) % 12, (root_index + 7) % 12]
        else:  # minor
            chord_indices = [root_index, (root_index + 3) % 12, (root_index + 7) % 12]
        
        chord_positions = []
        for (row, col), hex_data in self.hexagons.items():
            if hex_data['pitch_index'] in chord_indices:
                self.chord_highlights.add((row, col))
                if (row, col) not in self.active_notes:
                    hex_data['patch'].set_facecolor('yellow')
                    hex_data['patch'].set_alpha(0.9)
                chord_positions.append(hex_data['position'])
        
        if len(chord_positions) >= 3:
            min_perimeter = float('inf')
            best_triangle = None
            
            for i in range(len(chord_positions)):
                for j in range(i+1, len(chord_positions)):
                    for k in range(j+1, len(chord_positions)):
                        p1, p2, p3 = chord_positions[i], chord_positions[j], chord_positions[k]
                        perimeter = (np.linalg.norm(np.array(p1) - np.array(p2)) +
                                   np.linalg.norm(np.array(p2) - np.array(p3)) +
                                   np.linalg.norm(np.array(p3) - np.array(p1)))
                        if perimeter < min_perimeter:
                            min_perimeter = perimeter
                            best_triangle = [p1, p2, p3]
            
            if best_triangle and min_perimeter < 6:
                triangle = patches.Polygon(best_triangle, closed=True,
                                         facecolor='none', 
                                         edgecolor='red' if quality == 'major' else 'blue',
                                         linewidth=3, alpha=0.8)
                self.ax.add_patch(triangle)
                self.chord_triangles.append(triangle)
        
        chord_notes = [self.index_to_pitch_class(i) for i in chord_indices]
        for i, note in enumerate(chord_notes):
            threading.Timer(i * 0.2, self.play_chord_preview, args=[note]).start()
        
        self.fig.canvas.draw()
    
    def play_chord_preview(self, note):
        """Play a brief preview of a chord note"""
        if AUDIO_AVAILABLE:
            try:
                note_key = f"{note}4"
                if note_key in self.note_frequencies:
                    frequency = self.note_frequencies[note_key]
                    
                    duration = 1.5
                    sample_rate = 22050
                    frames = int(duration * sample_rate)
                    arr = np.zeros((frames, 2))
                    
                    harmonics = [(1.0, 1), (0.5, 2), (0.3, 3), (0.2, 4)]
                    
                    for i in range(frames):
                        sample = 0
                        for amp, mult in harmonics:
                            sample += amp * np.sin(2 * np.pi * frequency * mult * i / sample_rate)
                        sample /= len(harmonics)
                        arr[i][0] = sample
                        arr[i][1] = sample
                    
                    fade_frames = int(0.3 * sample_rate)
                    for i in range(fade_frames):
                        arr[-(i+1)] *= i / fade_frames
                    
                    arr = np.clip(arr * 15000, -32767, 32767).astype(np.int16)
                    sound = pygame.sndarray.make_sound(arr)
                    channel = pygame.mixer.find_channel()
                    if channel:
                        channel.play(sound)
            except Exception as e:
                print(f"Error playing chord preview {note}: {e}")
    
    def clear_chord_highlights(self):
        """Clear chord highlights but keep manually toggled notes"""
        for (row, col) in self.chord_highlights:
            if (row, col) not in self.active_notes:
                hex_data = self.hexagons[(row, col)]
                hex_data['patch'].set_facecolor(hex_data['base_color'])
                hex_data['patch'].set_alpha(0.6)
        
        for triangle in self.chord_triangles:
            triangle.remove()
        
        self.chord_highlights.clear()
        self.chord_triangles.clear()
    
    def clear_all(self):
        """Clear all highlights and active notes"""
        self.clear_chord_highlights()
        
        if not AUDIO_AVAILABLE:
            return

        # Acquire the lock once to stop all playing notes safely
        with self.audio_lock:
            # Get a list of notes to stop to avoid modifying the dict while iterating
            notes_to_stop = list(self.playing_notes.keys()) 
            for note in notes_to_stop:
                try:
                    if note in self.playing_notes: # Check again in case it was stopped by another means
                        self.playing_notes[note].stop()
                        del self.playing_notes[note]
                        print(f"Stopped playing {note} during clear_all")
                except Exception as e:
                    print(f"Error stopping {note} during clear_all: {e}")
        
        # Visually update the hexagons and clear active notes
        for (row, col) in list(self.active_notes):
            hex_data = self.hexagons[(row, col)]
            hex_data['active'] = False
            hex_data['patch'].set_facecolor(hex_data['base_color'])
            hex_data['patch'].set_alpha(0.6)
        
        self.active_notes.clear()
        # Use draw_idle() to safely schedule a redraw from an event handler
        self.fig.canvas.draw_idle()
    
    def point_in_hex(self, point, hex_center, size=0.5):
        """Check if a point is inside a pointy-topped hexagon"""
        px, py = point
        hx, hy = hex_center
        
        dx = abs(px - hx)
        dy = abs(py - hy)
        
        if dy > size:
            return False
        
        max_x = size * np.sqrt(3) * (1 - dy / (2 * size))
        return dx <= max_x
    
    def find_hex_at_point(self, x, y):
        """Find which hexagon contains the given point"""
        for (row, col), hex_data in self.hexagons.items():
            if self.point_in_hex((x, y), hex_data['position']):
                return (row, col)
        return None
    
    def on_press(self, event):
        """Handle mouse button press"""
        if event.inaxes != self.ax or event.button != 1:
            return
        
        hex_pos = self.find_hex_at_point(event.xdata, event.ydata)
        if hex_pos:
            self.is_dragging = True
            self.already_toggled.clear()
            self.already_toggled.add(hex_pos)
            
            self.drag_toggle_state = hex_pos not in self.active_notes
            
            self.toggle_note(*hex_pos)
    
    def on_motion(self, event):
        """Handle mouse motion (dragging)"""
        if not self.is_dragging or event.inaxes != self.ax:
            return
        
        hex_pos = self.find_hex_at_point(event.xdata, event.ydata)
        if hex_pos and hex_pos not in self.already_toggled:
            self.already_toggled.add(hex_pos)
            
            is_active = hex_pos in self.active_notes
            if is_active != self.drag_toggle_state:
                self.toggle_note(*hex_pos, play_sound=True)
    
    def on_release(self, event):
        """Handle mouse button release"""
        self.is_dragging = False
        self.already_toggled.clear()
    
    def on_key(self, event):
        """Handle keyboard input for chords"""
        if event.key == ' ':
            self.clear_all()
        elif event.key.upper() in 'CDEFGAB':
            if event.key.isupper():
                self.highlight_chord(event.key, 'major')
                print(f"Playing {event.key} major")
            else:
                self.highlight_chord(event.key.upper(), 'minor')
                print(f"Playing {event.key.upper()} minor")
    
    def show(self):
        """Display the interactive plot"""
        # Connect event handlers
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        try:
            self.fig.canvas.manager.set_window_title('Tonnetz Grid - Musical Pitch Space')
        except AttributeError:
            pass
        
        plt.tight_layout()
        plt.show()

def main():
    """Run the Tonnetz grid application"""
    print("\n" + "="*60)
    print("INTERACTIVE TONNETZ GRID")
    print("="*60)
    print("\nThe Tonnetz (tone network) visualizes musical pitch relationships:")
    print("• Rightward movement = Perfect 5th (7 semitones)")
    print("• Northeast diagonal = Major 3rd (4 semitones)")  
    print("• Southeast diagonal = Minor 3rd (3 semitones)")
    print("\nThis creates a space where:")
    print("• Major triads form upward-pointing triangles")
    print("• Minor triads form downward-pointing triangles")
    print("• Common tones between chords are adjacent")
    print("\nCONTROLS:")
    print("• Click any hexagon to toggle it ON/OFF (continuous stable tone)")
    print("• Drag mouse to paint multiple notes")
    print("• Press C,D,E,F,G,A,B for major chords (yellow highlight)")
    print("• Press c,d,e,f,g,a,b for minor chords")
    print("• Press Space to clear all notes")
    print("\nNOTE: Loading may take a moment while we generate audio magic! ♪")
    print("\n" + "="*60 + "\n")
    
    tonnetz = TonnetzGrid(rows=7, cols=12)
    tonnetz.show()

if __name__ == "__main__":
    main()

