# Face & Hand Tracking Visualizer

A real-time face and hand tracking application using MediaPipe and OpenCV that creates beautiful mesh visualizations of facial features and hand movements.

## Features

- **Real-time face tracking**: Detects and tracks facial landmarks with 468 points
- **Hand tracking**: Tracks both hands with custom tessellation patterns
- **Two visualization modes**:
  - Mesh mode: Shows connected points forming a detailed mesh
  - Dots mode: Displays only the landmark points
- **Customizable appearance**:
  - Adjustable colors for dots, lines, and background
  - Variable dot sizes and line thickness
  - Multiple connection patterns (tessellation, contours, face oval, etc.)
- **High performance**: Runs at 60 FPS with 1280x720 resolution
- **Interactive settings window**: Real-time adjustment of all parameters

## Requirements

- Python 3.7 - 3.11
- Webcam

## Installation
### Option 1:

1. Click the "Code" button

2. Click "Download ZIP"

3. Install required packages:
```bash
pip install opencv-python mediapipe numpy
```

### Option 2:

1. Clone this repository:
```bash
git clone https://github.com/yourusername/face-hand-tracker.git
cd face-hand-tracker
```

2. Install required packages:
```bash
pip install opencv-python mediapipe numpy
```

## Usage

Run the script:
```bash
python face_tracker.py
```

### Controls

- **Q**: Quit the application
- **Space**: Toggle between Mesh and Dots mode
- **Settings Window**: Use trackbars to adjust:
  - Visualization mode
  - Colors (RGB values for dots, lines, background)
  - Dot size
  - Line thickness
  - Connection type (for face mesh)

### Visualization Modes

1. **Mesh Mode**: Displays both face and hands with connected points forming a mesh
2. **Dots Mode**: Shows only the landmark points without connections

### Connection Types

The face mesh can display different connection patterns:
- **TESSELLATION**: Detailed triangular mesh (default)
- **CONTOURS**: Face contour lines
- **FACE_OVAL**: Outer face boundary
- **LIPS**: Lip contours only
- **LEFT_EYE**: Left eye connections
- **RIGHT_EYE**: Right eye connections

## How It Works

The application uses:
- **MediaPipe Face Mesh**: Detects 468 facial landmarks in real-time
- **MediaPipe Hands**: Tracks 21 landmarks per hand
- **OpenCV**: Handles webcam input and visualization
- **Custom tessellation**: Creates triangular patterns for hand visualization

## Performance

- Default resolution: 1280x720
- Target FPS: 60
- Optimized for real-time performance with minimal latency

## Customization

You can modify the default settings in the `__init__` method:
- Camera resolution
- Frame rate
- Default colors
- Detection confidence thresholds

## Troubleshooting

- **No camera detected**: Make sure your webcam is properly connected
- **Low FPS**: Try reducing the resolution or disabling hand tracking
- **Detection issues**: Ensure good lighting and adjust confidence thresholds

## Contributing

Feel free to open issues or submit pull requests with improvements!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [MediaPipe](https://github.com/google-ai-edge/mediapipe) by Google for face and hand detection
- [OpenCV](https://opencv.org) for computer vision functionality

## Future Improvements

- [ ] Add more visualization modes
- [ ] Support for multiple faces
- [ ] 3D face rotation tracking
- [ ] Export tracking data
- [ ] Add face filters and effects
- [ ] Performance profiling tools
