# Image Color Identifier

## App Description

This is a simple desktop tool that allows users to upload an image and click anywhere to inspect the color at that pixel.  
It displays the color in multiple formats:

- Hex  
- RGB / RGBA  
- HSL  
- CMYK  
- Nearest Named Color (CSS3)

---

## Install Required Libraries

Make sure you have Python 3.7+ installed.

Install the required packages with:

```bash
pip install pillow webcolors
```

---

## How to Run

```bash
python main.py
```

---

## How to Use

1. Click **Upload Image** and select an image file.
2. Click anywhere on the image to display the pixel's color values.
3. Use the following controls:

### Zoom & Scroll Controls

- **Ctrl + Scroll Wheel** — Zoom in/out at the mouse cursor position  
- **Scroll Wheel** — Scroll vertically within the image  
- **Shift + Scroll Wheel** — Scroll horizontally  

### Zoom Tool Buttons

- **🔍+ (Zoom In)** — Enables zoom-in mode with magnifier cursor  
- **🔍− (Zoom Out)** — Enables zoom-out mode with magnifier cursor  
- **Pointer Mode** — Returns the cursor to normal for color picking

### Copying Values

- Click the **Copy** button next to any displayed value (Hex, RGB, etc.) to copy it to your clipboard.



