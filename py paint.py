import tkinter as tk
from tkinter import Canvas, Scale, Label, Button, Frame, colorchooser
from PIL import Image, ImageDraw, ImageTk
import os

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyPaint")

        # Brush settings
        self.brush_size = tk.IntVar(value=5)
        self.brush_color = "black"
        self.eraser_mode = False
        self.last_x, self.last_y = None, None
        self.cursor_preview = None

        # Canvas and image setup
        self.canvas_width = 500
        self.canvas_height = 500
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)

        # Gallery directory setup
        self.gallery_path = "gallery"
        os.makedirs(self.gallery_path, exist_ok=True)

        # Create main canvas
        self.canvas = Canvas(
            self.root,
            bg="white",
            width=self.canvas_width,
            height=self.canvas_height
        )
        self.canvas.pack()

        # Bind drawing events
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonPress-1>", self.set_start_position)
        self.canvas.bind("<Motion>", self.update_cursor)

        # Create control panel
        controls_frame = Frame(self.root)
        controls_frame.pack(pady=5)

        Label(controls_frame, text="Brush/Eraser Size:").pack(side="left")
        Scale(
            controls_frame,
            from_=1,
            to=30,
            orient="horizontal",
            variable=self.brush_size
        ).pack(side="left", padx=5)
        Button(
            controls_frame,
            text="Choose Color",
            command=self.choose_color
        ).pack(side="left", padx=5)
        Button(
            controls_frame,
            text="Eraser",
            command=self.toggle_eraser
        ).pack(side="left", padx=5)
        Button(
            controls_frame,
            text="Clear",
            command=self.clear_canvas
        ).pack(side="left", padx=5)
        Button(
            controls_frame,
            text="Save",
            command=self.save_image
        ).pack(side="left", padx=5)
        Button(
            controls_frame,
            text="Load",
            command=self.load_image
        ).pack(side="left", padx=5)
        Button(
            controls_frame,
            text="Delete",
            command=self.delete_image
        ).pack(side="left", padx=5)

        # Create gallery frame for thumbnails
        self.gallery_frame = Frame(self.root)
        self.gallery_frame.pack(pady=5)
        self.load_gallery()

    def choose_color(self):
        """Open a color chooser dialog and set the brush color."""
        color = colorchooser.askcolor(title="Choose Brush Color")
        # color is a tuple like: ((R, G, B), "#rrggbb")
        if color[1]:
            self.brush_color = color[1]
            self.eraser_mode = False

    def toggle_eraser(self):
        """Toggle eraser mode – when active, drawing uses white."""
        self.eraser_mode = not self.eraser_mode
        self.brush_color = "white" if self.eraser_mode else "black"

    def set_start_position(self, event):
        """Store the starting position for drawing."""
        self.last_x, self.last_y = event.x, event.y

    def paint(self, event):
        """
        Draw a line on the canvas and on the image from the last point
        to the current mouse position.
        """
        if self.last_x is not None and self.last_y is not None:
            x, y = event.x, event.y
            self.canvas.create_line(
                self.last_x, self.last_y, x, y,
                width=self.brush_size.get(),
                fill=self.brush_color,
                capstyle=tk.ROUND,
                smooth=True
            )
            self.draw.line(
                [self.last_x, self.last_y, x, y],
                fill=self.brush_color,
                width=self.brush_size.get()
            )
        self.last_x, self.last_y = event.x, event.y
        self.update_cursor(event)

    def update_cursor(self, event):
        """Display a circular preview of the brush at the cursor position."""
        if self.cursor_preview is not None:
            self.canvas.delete(self.cursor_preview)
        r = self.brush_size.get()
        self.cursor_preview = self.canvas.create_oval(
            event.x - r, event.y - r,
            event.x + r, event.y + r,
            outline="black",
            width=1
        )

    def clear_canvas(self):
        """Clear the canvas and reset the drawing image."""
        self.canvas.delete("all")
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)

    def save_image(self):
        """
        Save the current image to the gallery with an incremental filename
        and update the gallery thumbnails.
        """
        existing = [f for f in os.listdir(self.gallery_path) if f.endswith(".png")]
        filename = os.path.join(self.gallery_path, f"drawing_{len(existing) + 1}.png")
        self.image.save(filename)
        self.load_gallery()

    def load_image(self):
        """
        Load the most recent image from the gallery and update the canvas.
        """
        png_files = sorted(
            [f for f in os.listdir(self.gallery_path) if f.endswith(".png")]
        )
        if png_files:
            latest_image = png_files[-1]
            loaded_image = Image.open(os.path.join(self.gallery_path, latest_image))
            self.image = loaded_image.copy()
            self.draw = ImageDraw.Draw(self.image)
            self.update_canvas()

    def update_canvas(self):
        """Redraw the image on the canvas."""
        self.canvas.delete("all")
        tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=tk_image)
        # Keep a reference to prevent garbage collection.
        self.canvas.image = tk_image

    def delete_image(self):
        """
        Delete the most recent image from the gallery and update the thumbnails.
        """
        png_files = sorted(
            [f for f in os.listdir(self.gallery_path) if f.endswith(".png")]
        )
        if png_files:
            latest_image = png_files[-1]
            os.remove(os.path.join(self.gallery_path, latest_image))
            self.load_gallery()

    def load_gallery(self):
        """Load thumbnails of all saved images into the gallery frame."""
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()
        png_files = sorted(
            [f for f in os.listdir(self.gallery_path) if f.endswith(".png")]
        )
        for filename in png_files:
            filepath = os.path.join(self.gallery_path, filename)
            img = Image.open(filepath).resize((100, 100))
            tk_img = ImageTk.PhotoImage(img)
            lbl = Label(self.gallery_frame, image=tk_img)
            lbl.image = tk_img  # Prevent garbage collection.
            lbl.pack(side="left", padx=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()
