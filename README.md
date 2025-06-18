# Interactive Tonnetz Grid

## Overview

The Interactive Tonnetz Grid is a Python application that visualizes and allows interaction with the Tonnetz, a conceptual lattice structure representing musical pitch relationships. This application provides an intuitive graphical interface where users can explore pitch space, activate individual notes, and highlight major and minor chords, accompanied by real-time audio playback.

The Tonnetz is a fundamental concept in neo-Riemannian music theory, offering a geometric representation of pitch relationships where common musical intervals correspond to consistent movements across the grid.

## Features

* **Interactive Tonnetz Visualization**: Displays a grid of hexagons, each representing a pitch class (C, C#, D, etc.).
* **Pitch Relationships at a Glance**:
    * Horizontal movement (left/right) represents a **Perfect Fifth** (7 semitones).
    * Diagonal movement to the **northeast** represents a **Major Third** (4 semitones).
    * Diagonal movement to the **southeast** represents a **Minor Third** (3 semitones).
* **Real-time Audio Playback**:
    * Clicking a hexagon toggles the corresponding note on/off, playing a continuous, stable tone.
    * Drag the mouse to "paint" and toggle multiple notes simultaneously.
* **Chord Highlighting**:
    * Press `C`, `D`, `E`, `F`, `G`, `A`, `B` to highlight the corresponding **Major chords** (yellow triangles).
    * Press `c`, `d`, `e`, `f`, `g`, `a`, `b` to highlight the corresponding **Minor chords** (blue triangles).
    * Chord highlights are accompanied by a brief audio preview of the chord notes.
* **Clear All**: Press `Spacebar` to clear all active notes and chord highlights.
* **Loading Screen**: A dynamic loading screen is displayed while the application pre-generates audio samples for seamless playback.

## The Tonnetz Explained (Background)

The Tonnetz (German for "tone network") is a specialized lattice diagram that visually represents the relationships between musical pitches in a non-linear way. Its origins can be traced back to Leonhard Euler in the 18th century, but it was significantly developed and popularized by German music theorist Hugo Riemann in the 19th century. Riemann used it to illustrate harmonic relationships and transformations.

Unlike a traditional linear scale, the Tonnetz emphasizes the intervallic distances between notes, particularly **perfect fifths**, **major thirds**, and **minor thirds**. This hexagonal grid offers a profound geometric insight into how chords and keys relate to each other.

### Key Relationships on the Tonnetz:

* **Perfect Fifths (P5)**: Moving horizontally across the Tonnetz (left or right) always results in a perfect fifth interval. For example, moving from C to G (right) or C to F (left). These movements represent fundamental harmonic progressions.
* **Major Thirds (M3)**: Moving diagonally in a "northeast" direction (up and right) yields a major third. For example, moving from C to E.
* **Minor Thirds (m3)**: Moving diagonally in a "southeast" direction (down and right) yields a minor third. For example, moving from C to Eb.

### Triads and Neo-Riemannian Transformations:

One of the most elegant aspects of the Tonnetz is how it represents triads:

* **Major Triads** (e.g., C-E-G) always form **upward-pointing triangles** on the grid.
* **Minor Triads** (e.g., C-Eb-G) always form **downward-pointing triangles**.

This geometric representation makes it easy to visualize common tone relationships between chords and understand concepts like **neo-Riemannian transformations**. These transformations describe the minimal movement between chords that share common tones, often involving a single voice leading change. The most common are:

* **P-transformation (Parallel)**: Converts a major triad into its parallel minor (e.g., C Major to C minor) or vice-versa. This involves moving one vertex of the triangle across a horizontal axis.
* **R-transformation (Relative)**: Converts a major triad into its relative minor (e.g., C Major to A minor) or vice-versa. This involves moving one vertex across a diagonal axis.
* **L-transformation (Leittonwechsel)**: Converts a major triad into its leading-tone exchange minor (e.g., C Major to E minor) or vice-versa. This also involves moving one vertex across a diagonal axis.

The Tonnetz, therefore, is not just a pretty diagram but a powerful analytical tool for understanding voice leading, harmonic progression, and the underlying symmetries of musical space, particularly in the study of Romantic and post-Romantic harmony. It's a valuable resource for composers seeking new harmonic pathways and for theorists analyzing complex musical structures.

## Getting Started

### Prerequisites

Before running the application, ensure you have Python installed. You will also need to install the following Python libraries: `matplotlib`, `numpy`, and `pygame`.

To manage dependencies cleanly, it's highly recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html).

### Installation


1.  **Create and activate a virtual environment**:
    Open your terminal or command prompt and navigate to the directory where you saved `music.py` and `requirements.txt`. Then, run the following commands:

    ```bash
    # Create a virtual environment named 'venv'
    python -m venv venv

    # Activate the virtual environment
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

2.  **Install dependencies**:
    With your virtual environment activated, install the required libraries:

    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Save the code**: Save the provided Python code as `music.py` in the same directory as your `requirements.txt`.
2.  **Run from terminal**: Ensure your virtual environment is active, then run:

    ```bash
    python music.py
    ```

3.  **Loading Screen**: Upon launch, a loading screen will appear. This indicates that the application is pre-generating 60-second audio loops for each pitch class to ensure smooth and continuous playback. This process may take a moment depending on your system.
4.  **Interact**: Once the loading screen disappears, the interactive Tonnetz grid will be displayed, and you can start interacting with it using your mouse and keyboard.

## How to Use

* **Toggle Notes**:
    * **Click** any hexagon to toggle the corresponding musical note on or off. When a note is active, its hexagon will turn white, and its continuous tone will play.
    * **Click and Drag** your mouse across multiple hexagons to toggle them on or off in a "painting" style. The initial click determines whether you are turning notes on or off during the drag.
* **Highlight Chords**:
    * Press the **uppercase letter keys** (`C`, `D`, `E`, `F`, `G`, `A`, `B`) to highlight the corresponding **Major Triads**. A yellow triangle will appear connecting the notes of the chord, and the chord notes will briefly play.
    * Press the **lowercase letter keys** (`c`, `d`, `e`, `f`, `g`, `a`, `b`) to highlight the corresponding **Minor Triads**. A blue triangle will appear, and the chord notes will briefly play.
* **Clear All**: Press the **Spacebar** (` `) to turn off all active notes and remove any chord highlights.

## Technical Details

* **Audio Generation**: The application pre-generates 60-second sine wave audio samples for each pitch class at octave 4 (e.g., C4, D4). These samples include basic harmonics to create a richer, more pleasing tone and are designed to loop seamlessly for continuous playback. `pygame.mixer` is used for efficient audio management.
* **Grid Construction**: The Tonnetz grid is constructed programmatically, with each hexagon's position calculated to maintain the correct intervallic relationships (Perfect 5th horizontally, Major 3rd NE, Minor 3rd SE).
* **Event Handling**: `matplotlib`'s event handling system is used to capture mouse clicks, drags, and keyboard presses, translating them into interactive changes on the grid and controlling audio playback.
* **Multithreading**: Audio pre-generation is performed in a separate thread to prevent the GUI from freezing during the initial loading phase, ensuring a smoother user experience.

## Contributing

Feel free to fork the repository, make improvements, or suggest new features.

## License

This project is open-source and available under the MIT License.
