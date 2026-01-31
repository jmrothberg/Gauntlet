#!/usr/bin/env python3
"""
convert_sprites_gui.py - GUI Image to Sprite Converter

A graphical user interface for converting images to game sprites with
transparency control. Supports both single images and batch folder processing.

Features:
  - Select single image files or entire folders of images
  - Automatic white background to transparency conversion
  - Output as PNG sprites or embedded JavaScript (base64)
  - Batch processing with progress feedback
  - Auto-suggested output filenames

Supported Input Formats:
  - PNG, JPG/JPEG, BMP, GIF, TIFF

Output Formats:
  - PNG: Individual sprite files (32x32 pixels)
  - JavaScript: Base64-encoded sprites in a JS object

Usage:
    python convert_sprites_gui.py

Prerequisites:
    - tkinter (usually included with Python)
    - PIL (Pillow) library: pip install Pillow

Author: JMR
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from PIL import Image
import base64

class SpriteConverterGUI:
    """
    Main GUI class for the sprite converter application.
    
    Provides a tkinter-based interface for:
      - Selecting input images (single file or folder)
      - Configuring transparency and output format options
      - Converting images to sprites with visual feedback
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Image to Sprite Converter")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.transparent_var = tk.BooleanVar(value=True)  # Default to transparent
        self.output_format = tk.StringVar(value="png")  # png or js

        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="Image to Sprite Converter",
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        # Input selection frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Select Input:", font=("Arial", 12)).pack()

        # Buttons for selecting input
        button_frame = tk.Frame(input_frame)
        button_frame.pack(pady=5)

        folder_btn = tk.Button(button_frame, text="📁 Select Folder",
                              command=self.select_folder, width=15)
        folder_btn.pack(side=tk.LEFT, padx=5)

        file_btn = tk.Button(button_frame, text="🖼️ Select Image",
                            command=self.select_file, width=15)
        file_btn.pack(side=tk.LEFT, padx=5)

        # Show selected path
        self.path_label = tk.Label(input_frame, text="No selection",
                                  fg="gray", wraplength=400)
        self.path_label.pack(pady=5)

        # Options frame
        options_frame = tk.Frame(self.root)
        options_frame.pack(pady=10)

        tk.Label(options_frame, text="Options:", font=("Arial", 12)).pack()

        # Transparency checkbox
        self.transparent_check = tk.Checkbutton(options_frame,
                                               text="Make white backgrounds transparent",
                                               variable=self.transparent_var)
        self.transparent_check.pack(pady=5)

        # Output format selection
        format_frame = tk.Frame(options_frame)
        format_frame.pack(pady=5)

        tk.Label(format_frame, text="Output format:").pack(side=tk.LEFT)
        tk.Radiobutton(format_frame, text="PNG Sprite", variable=self.output_format,
                      value="png").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(format_frame, text="JavaScript", variable=self.output_format,
                      value="js").pack(side=tk.LEFT, padx=10)

        # Output file frame
        output_frame = tk.Frame(self.root)
        output_frame.pack(pady=10)

        tk.Label(output_frame, text="Output:", font=("Arial", 12)).pack()

        output_entry_frame = tk.Frame(output_frame)
        output_entry_frame.pack(pady=5)

        self.output_entry = tk.Entry(output_entry_frame, textvariable=self.output_path,
                                    width=30)
        self.output_entry.pack(side=tk.LEFT, padx=5)

        browse_output_btn = tk.Button(output_entry_frame, text="📄 Browse",
                                     command=self.select_output)
        browse_output_btn.pack(side=tk.LEFT)

        # Convert button
        self.convert_btn = tk.Button(self.root, text="🚀 Convert Sprites",
                                    command=self.convert_sprites,
                                    bg="#4CAF50", fg="white",
                                    font=("Arial", 12, "bold"),
                                    height=2, width=20)
        self.convert_btn.pack(pady=20)

        # Status label
        self.status_label = tk.Label(self.root, text="", fg="blue")
        self.status_label.pack(pady=5)

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select folder containing images")
        if folder_path:
            self.input_path.set(folder_path)
            self.path_label.config(text=f"📁 {folder_path}", fg="black")
            self.update_output_path()
            self.status_label.config(text="")

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select image file",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                      ("PNG files", "*.png"),
                      ("JPEG files", "*.jpg *.jpeg"),
                      ("All files", "*.*")]
        )
        if file_path:
            self.input_path.set(file_path)
            self.path_label.config(text=f"🖼️ {file_path}", fg="black")
            self.update_output_path()
            self.status_label.config(text="")

    def update_output_path(self):
        """Update the output path based on input selection and format"""
        input_path = self.input_path.get()
        if not input_path:
            return

        if os.path.isdir(input_path):
            # For directories, suggest a JS file for embedded sprites
            dirname = os.path.basename(input_path)
            self.output_path.set(f"{dirname}_sprites.js")
            self.output_format.set("js")
        else:
            # For single files, suggest PNG output
            filename = os.path.splitext(os.path.basename(input_path))[0]
            self.output_path.set(f"{filename}_sprite.png")
            self.output_format.set("png")

    def select_output(self):
        format_type = self.output_format.get()
        if format_type == "js":
            file_path = filedialog.asksaveasfilename(
                title="Save JavaScript file",
                defaultextension=".js",
                filetypes=[("JavaScript files", "*.js"), ("All files", "*.*")],
                initialfile=self.output_path.get()
            )
        else:  # png
            file_path = filedialog.asksaveasfilename(
                title="Save PNG sprite",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialfile=self.output_path.get()
            )
        if file_path:
            self.output_path.set(file_path)

    def convert_image_to_sprite(self, input_path, output_path, make_transparent=True, size=(32, 32)):
        """
        Converts a single image file to a sprite with optional transparency.
        
        Args:
            input_path: Path to the source image file
            output_path: Path for the output PNG sprite
            make_transparent: If True, converts white pixels to transparent
            size: Tuple (width, height) for output sprite dimensions
            
        The conversion process:
          1. Opens and converts image to RGBA mode
          2. If transparency enabled, makes near-white pixels transparent
          3. Resizes to target sprite dimensions using LANCZOS filter
          4. Saves as PNG with alpha channel
        """
        try:
            # Open the image
            with Image.open(input_path) as img:
                print(f"Original size: {img.size}")
                print(f"Original format: {img.format}")

                # Convert to RGBA if not already (for transparency support)
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')

                # Make white pixels transparent if requested
                if make_transparent:
                    print("   Making white pixels transparent...")
                    pixels = img.load()
                    width, height = img.size

                    for y in range(height):
                        for x in range(width):
                            r, g, b, a = pixels[x, y]
                            # Check if pixel is white (allowing some tolerance for JPEG compression artifacts)
                            if r > 240 and g > 240 and b > 240:  # Very close to white
                                pixels[x, y] = (r, g, b, 0)  # Set alpha to 0 (transparent)

                # Resize to sprite dimensions
                resized_img = img.resize(size, Image.Resampling.LANCZOS)

                # Save as PNG
                resized_img.save(output_path, 'PNG')

                print(f"✅ Converted {input_path} -> {output_path}")
                print(f"   New size: {resized_img.size}")
                print(f"   File size: {os.path.getsize(output_path)} bytes")

        except Exception as e:
            print(f"❌ Error converting {input_path}: {e}")
            raise

    def convert_to_base64(self, image_path):
        """
        Converts an image file to a base64 data URL string.
        
        Args:
            image_path: Path to the PNG image file
            
        Returns:
            str: Data URL in format "data:image/png;base64,..."
        """
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded_string}"

    def convert_sprites(self):
        input_path = self.input_path.get()
        output_path = self.output_path.get()
        make_transparent = self.transparent_var.get()
        output_format = self.output_format.get()

        if not input_path:
            messagebox.showerror("Error", "Please select a folder or image file first!")
            return

        if not output_path:
            messagebox.showerror("Error", "Please specify an output file!")
            return

        try:
            self.status_label.config(text="Converting...", fg="orange")
            self.convert_btn.config(state="disabled")
            self.root.update()

            if output_format == "png":
                # Single PNG sprite output
                if os.path.isdir(input_path):
                    messagebox.showerror("Error", "For PNG output, please select a single image file, not a folder.")
                    return

                self.convert_image_to_sprite(input_path, output_path, make_transparent)
                self.status_label.config(
                    text=f"✅ Success! Created sprite: {output_path}",
                    fg="green"
                )
                messagebox.showinfo("Success", f"Successfully converted sprite!\n\nOutput: {output_path}")

            else:  # js format
                # JavaScript embedded sprites output
                with open(output_path, 'w') as f:
                    f.write("// Embedded sprite data\n")
                    f.write("const embeddedSprites = {\n")

                    if os.path.isdir(input_path):
                        # Process all images in directory
                        extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')
                        image_files = [f for f in os.listdir(input_path) if f.lower().endswith(extensions)]
                        converted_count = 0

                        for filename in sorted(image_files):
                            input_file = os.path.join(input_path, filename)
                            temp_png = f"temp_{filename}.png"
                            try:
                                self.convert_image_to_sprite(input_file, temp_png, make_transparent)

                                # Convert to base64 and add to JS
                                base64_data = self.convert_to_base64(temp_png)
                                key_name = os.path.splitext(filename)[0]

                                f.write(f'    "{key_name}": "{base64_data}"')
                                if converted_count < len(image_files) - 1:
                                    f.write(',\n')
                                else:
                                    f.write('\n')

                                # Clean up temp file
                                os.remove(temp_png)
                                converted_count += 1

                            except Exception as e:
                                print(f"Failed to process {filename}: {e}")
                                if os.path.exists(temp_png):
                                    os.remove(temp_png)
                                continue

                        f.write("};\n")

                        self.status_label.config(
                            text=f"✅ Success! Created {output_path} with {converted_count} sprites",
                            fg="green"
                        )
                        messagebox.showinfo("Success",
                                          f"Successfully converted {converted_count} sprites!\n\nOutput: {output_path}")

                    else:
                        # Single image to JS
                        temp_png = "temp_sprite.png"
                        self.convert_image_to_sprite(input_path, temp_png, make_transparent)

                        base64_data = self.convert_to_base64(temp_png)
                        filename = os.path.splitext(os.path.basename(input_path))[0]

                        f.write(f'    "{filename}": "{base64_data}"\n')
                        f.write("};\n")

                        # Clean up temp file
                        os.remove(temp_png)

                        self.status_label.config(
                            text=f"✅ Success! Created {output_path} with 1 sprite",
                            fg="green"
                        )
                        messagebox.showinfo("Success",
                                          f"Successfully converted 1 sprite!\n\nOutput: {output_path}")

        except Exception as e:
            self.status_label.config(text=f"❌ Error: {str(e)}", fg="red")
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")
        finally:
            self.convert_btn.config(state="normal")

def main():
    """
    Entry point for the sprite converter GUI application.
    Creates and runs the main tkinter window.
    """
    root = tk.Tk()
    app = SpriteConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
