import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import colorsys
import webcolors

def rgb_to_cmyk(r, g, b):
    if (r, g, b) == (0, 0, 0):
        return 0, 0, 0, 100
    c = 1 - r / 255
    m = 1 - g / 255
    y = 1 - b / 255
    min_cmy = min(c, m, y)
    c = (c - min_cmy) / (1 - min_cmy) * 100
    m = (m - min_cmy) / (1 - min_cmy) * 100
    y = (y - min_cmy) / (1 - min_cmy) * 100
    k = min_cmy * 100
    return round(c), round(m), round(y), round(k)

def rgb_to_hsl(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    return round(h*360), round(s*100), round(l*100)

def closest_color(requested_rgb):
    def distance(c1, c2):
        return sum((a - b) ** 2 for a, b in zip(c1, c2))
    color_names = webcolors.names(spec='css3')
    closest = min(
        color_names,
        key=lambda name: distance(webcolors.name_to_rgb(name, spec='css3'), requested_rgb)
    )
    return closest

class ColorIdentifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Color Identifier")
        self.root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
        self.root.configure(bg="#2c3e50")

        self.zoom_level = 1.0
        self.original_image = None
        self.display_image = None
        self.magnifier_mode = None

        self.create_widgets()
        self.bind_events()

    def create_widgets(self):
        top_controls = tk.Frame(self.root, bg="#2c3e50")
        top_controls.pack(fill=tk.X, pady=10)

        tk.Button(top_controls, text="Upload Image", command=self.upload_image,
                  bg="#3498db", fg="white", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)

        self.zoom_in_btn = tk.Button(top_controls, text="🔍+", command=self.zoom_in_mode,
                                     bg="#27ae60", fg="white", font=("Arial", 12))
        self.zoom_in_btn.pack(side=tk.LEFT)

        self.zoom_out_btn = tk.Button(top_controls, text="🔍-", command=self.zoom_out_mode,
                                      bg="#c0392b", fg="white", font=("Arial", 12))
        self.zoom_out_btn.pack(side=tk.LEFT)

        self.pointer_btn = tk.Button(top_controls, text="Pointer Mode", command=self.reset_pointer_mode,
                                     bg="#95a5a6", fg="white", font=("Arial", 12))
        self.pointer_btn.pack(side=tk.LEFT, padx=10)

        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(pady=5)

        self.scroll_x = tk.Scrollbar(self.image_frame, orient=tk.HORIZONTAL)
        self.scroll_y = tk.Scrollbar(self.image_frame, orient=tk.VERTICAL)

        self.canvas = tk.Canvas(self.image_frame, bg="white", cursor="cross",
                                width=1000, height=500,
                                xscrollcommand=self.scroll_x.set,
                                yscrollcommand=self.scroll_y.set)
        self.scroll_x.config(command=self.canvas.xview)
        self.scroll_y.config(command=self.canvas.yview)

        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT)

        self.canvas.bind("<Button-1>", self.get_color)

        self.info_frame = tk.Frame(self.root, bg="#2c3e50")
        self.info_frame.pack(pady=10, fill=tk.X)

    def bind_events(self):
        self.root.bind("<Control-MouseWheel>", self.ctrl_scroll_zoom)
        self.canvas.bind("<MouseWheel>", self.scroll_y_only)
        self.canvas.bind("<Shift-MouseWheel>", self.scroll_x_only)

    def ctrl_scroll_zoom(self, event):
        scale = 1.25 if event.delta > 0 else 0.8
        self.zoom_at_cursor(scale, event)

    def scroll_y_only(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def scroll_x_only(self, event):
        self.canvas.xview_scroll(-1 * (event.delta // 120), "units")

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if not file_path:
            return
        self.original_image = Image.open(file_path).convert("RGBA")
        self.zoom_level = 1.0
        self.render_image()

    def render_image(self):
        if not self.original_image:
            return
        width = int(self.original_image.width * self.zoom_level)
        height = int(self.original_image.height * self.zoom_level)
        self.display_image = self.original_image.resize((width, height), Image.Resampling.NEAREST)
        self.tk_img = ImageTk.PhotoImage(self.display_image)
        self.canvas.config(scrollregion=(0, 0, width, height))
        self.canvas.delete("all")
        self.canvas_image = self.canvas.create_image(0, 0, image=self.tk_img, anchor=tk.NW)
        self.canvas.image = self.tk_img

    def zoom_at_cursor(self, scale, event):
        if not self.original_image:
            return

        new_zoom = self.zoom_level * scale
        new_zoom = max(0.1, min(3.0, new_zoom))

        mouse_x = self.canvas.canvasx(event.x)
        mouse_y = self.canvas.canvasy(event.y)

        ratio_x = mouse_x / self.display_image.width
        ratio_y = mouse_y / self.display_image.height

        self.zoom_level = new_zoom
        self.render_image()

        new_mouse_x = int(ratio_x * self.display_image.width)
        new_mouse_y = int(ratio_y * self.display_image.height)

        self.canvas.xview_moveto(new_mouse_x / self.display_image.width)
        self.canvas.yview_moveto(new_mouse_y / self.display_image.height)

    def zoom_in_mode(self):
        self.canvas.config(cursor="plus")
        self.magnifier_mode = "in"
        self.canvas.bind("<Button-1>", self.click_zoom)

    def zoom_out_mode(self):
        self.canvas.config(cursor="circle")
        self.magnifier_mode = "out"
        self.canvas.bind("<Button-1>", self.click_zoom)


    def reset_pointer_mode(self):
        self.canvas.config(cursor="cross")
        self.magnifier_mode = None
        self.canvas.bind("<Button-1>", self.get_color)

    def click_zoom(self, event):
        if not self.original_image:
            return
        scale = 1.25 if self.magnifier_mode == "in" else 0.8
        self.zoom_at_cursor(scale, event)

    def display_color_info(self, info_dict):
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        for label, value in info_dict.items():
            frame = tk.Frame(self.info_frame, bg="#2c3e50")
            frame.pack(anchor='w', padx=10, pady=2, fill=tk.X)
            lbl = tk.Label(frame, text=f"{label}:", width=18, anchor='w',
                           bg="#2c3e50", fg="white", font=("Courier", 11, "bold"))
            lbl.pack(side=tk.LEFT)
            val_lbl = tk.Label(frame, text=value, anchor='w',
                               bg="#2c3e50", fg="lightgreen", font=("Courier", 11))
            val_lbl.pack(side=tk.LEFT, padx=(5, 10))
            copy_btn = tk.Button(frame, text="Copy", command=lambda v=value: self.copy_to_clipboard(v),
                                 bg="#1abc9c", fg="white", font=("Arial", 9, "bold"))
            copy_btn.pack(side=tk.LEFT)

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

    def get_color(self, event):
        if not self.original_image:
            return
        x = int(self.canvas.canvasx(event.x) / self.zoom_level)
        y = int(self.canvas.canvasy(event.y) / self.zoom_level)
        if x >= self.original_image.width or y >= self.original_image.height:
            return
        rgba = self.original_image.getpixel((x, y))
        r, g, b, a = rgba
        hex_val = '#{:02x}{:02x}{:02x}'.format(r, g, b)
        h, s, l = rgb_to_hsl(r, g, b)
        c, m, yk, k = rgb_to_cmyk(r, g, b)
        try:
            name = webcolors.rgb_to_name((r, g, b), spec='css3')
        except Exception:
            name = closest_color((r, g, b))
        info = {
            "Position": f"({x}, {y})",
            "Hex": hex_val,
            "RGB": f"({r}, {g}, {b})",
            "RGBA": f"({r}, {g}, {b}, {a})",
            "HSL": f"({h}°, {s}%, {l}%)",
            "CMYK": f"({c}%, {m}%, {yk}%, {k}%)",
            "Nearest Named Color": name
        }
        self.display_color_info(info)

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorIdentifierApp(root)
    root.mainloop()
