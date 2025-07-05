import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import os
import zipfile
import tempfile
import shutil
from PIL import Image, ImageTk
import threading
from typing import List, Tuple, Optional

class ModernImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        self.resizer = ImageResizer()
        
    def setup_window(self):
        self.root.title("🖼️ Image Resizer Pro")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")
        
        # Configure root background
        self.root.configure(bg='#f0f0f0')
        
    def setup_styles(self):
        # Configure ttk styles for modern look
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 20, 'bold'),
                       background='#f0f0f0',
                       foreground='#2c3e50')
        
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 11),
                       background='#f0f0f0',
                       foreground='#34495e')
        
        style.configure('Modern.TButton',
                       font=('Segoe UI', 10),
                       padding=(20, 10))
        
        # Configure Notebook (tabs) style
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TNotebook.Tab', padding=[20, 8])
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🖼️ Image Resizer Pro", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Resize images individually, in bulk from folders, or from zip files", style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create tabs
        self.create_single_image_tab()
        self.create_folder_tab()
        self.create_zip_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, padding=(10, 5))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def create_single_image_tab(self):
        # Single Image Tab
        single_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(single_frame, text="📷 Single Image")
        
        # Left side - controls
        left_frame = ttk.Frame(single_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Image selection
        ttk.Label(left_frame, text="Select Image:", font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        img_frame = ttk.Frame(left_frame)
        img_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.single_image_var = tk.StringVar()
        ttk.Entry(img_frame, textvariable=self.single_image_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(img_frame, text="Browse", command=self.browse_single_image, style='Modern.TButton').pack(side=tk.RIGHT)
        
        # Dimensions
        ttk.Label(left_frame, text="Dimensions:", font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        dim_frame = ttk.Frame(left_frame)
        dim_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(dim_frame, text="Width:").pack(side=tk.LEFT)
        self.single_width_var = tk.StringVar(value="800")
        width_spin = ttk.Spinbox(dim_frame, from_=1, to=10000, textvariable=self.single_width_var, width=10)
        width_spin.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(dim_frame, text="Height:").pack(side=tk.LEFT)
        self.single_height_var = tk.StringVar(value="600")
        height_spin = ttk.Spinbox(dim_frame, from_=1, to=10000, textvariable=self.single_height_var, width=10)
        height_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        # Options
        self.single_maintain_aspect = tk.BooleanVar(value=True)
        ttk.Checkbutton(left_frame, text="Maintain aspect ratio", variable=self.single_maintain_aspect).pack(anchor=tk.W, pady=(0, 10))
        
        # PNG Background Color Selection
        png_bg_frame = ttk.LabelFrame(left_frame, text="PNG Background Color", padding="10")
        png_bg_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.png_bg_option = tk.StringVar(value="auto")
        ttk.Radiobutton(png_bg_frame, text="Auto-detect from image", variable=self.png_bg_option, value="auto").pack(anchor=tk.W)
        ttk.Radiobutton(png_bg_frame, text="Black background", variable=self.png_bg_option, value="black").pack(anchor=tk.W)
        ttk.Radiobutton(png_bg_frame, text="White background", variable=self.png_bg_option, value="white").pack(anchor=tk.W)
        ttk.Radiobutton(png_bg_frame, text="Custom color", variable=self.png_bg_option, value="custom").pack(anchor=tk.W)
        
        # Custom color selection
        custom_color_frame = ttk.Frame(png_bg_frame)
        custom_color_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.custom_color = tk.StringVar(value="#FFFFFF")
        ttk.Label(custom_color_frame, text="Custom color:").pack(side=tk.LEFT)
        color_entry = ttk.Entry(custom_color_frame, textvariable=self.custom_color, width=10)
        color_entry.pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(custom_color_frame, text="Choose", command=self.choose_custom_color).pack(side=tk.LEFT)
        
        # Process button
        ttk.Button(left_frame, text="🔄 Resize Image", command=self.process_single_image, style='Modern.TButton').pack(pady=10)
        
        # Status
        self.single_status_var = tk.StringVar()
        ttk.Label(left_frame, textvariable=self.single_status_var, wraplength=350).pack(anchor=tk.W, pady=(10, 0))
        
        # Right side - preview
        right_frame = ttk.Frame(single_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_frame, text="Preview:", font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        # Image preview
        self.preview_frame = ttk.Frame(right_frame, relief=tk.SUNKEN, borderwidth=2)
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_label = ttk.Label(self.preview_frame, text="No image selected", anchor=tk.CENTER)
        self.preview_label.pack(expand=True)
    
    def create_folder_tab(self):
        # Folder Processing Tab
        folder_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(folder_frame, text="📁 Folder Processing")
        
        # Folder selection
        ttk.Label(folder_frame, text="Select Folder:", font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        folder_select_frame = ttk.Frame(folder_frame)
        folder_select_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.folder_path_var = tk.StringVar()
        ttk.Entry(folder_select_frame, textvariable=self.folder_path_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(folder_select_frame, text="Browse", command=self.browse_folder, style='Modern.TButton').pack(side=tk.RIGHT)
        
        # Dimensions
        ttk.Label(folder_frame, text="Dimensions:", font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        folder_dim_frame = ttk.Frame(folder_frame)
        folder_dim_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(folder_dim_frame, text="Width:").pack(side=tk.LEFT)
        self.folder_width_var = tk.StringVar(value="800")
        ttk.Spinbox(folder_dim_frame, from_=1, to=10000, textvariable=self.folder_width_var, width=10).pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(folder_dim_frame, text="Height:").pack(side=tk.LEFT)
        self.folder_height_var = tk.StringVar(value="600")
        ttk.Spinbox(folder_dim_frame, from_=1, to=10000, textvariable=self.folder_height_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # Options
        self.folder_maintain_aspect = tk.BooleanVar(value=True)
        ttk.Checkbutton(folder_frame, text="Maintain aspect ratio", variable=self.folder_maintain_aspect).pack(anchor=tk.W, pady=(0, 10))
        
        # PNG Background Color Selection for Folder
        folder_png_bg_frame = ttk.LabelFrame(folder_frame, text="PNG Background Color", padding="10")
        folder_png_bg_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.folder_png_bg_option = tk.StringVar(value="auto")
        ttk.Radiobutton(folder_png_bg_frame, text="Auto-detect from image", variable=self.folder_png_bg_option, value="auto").pack(anchor=tk.W)
        ttk.Radiobutton(folder_png_bg_frame, text="Black background", variable=self.folder_png_bg_option, value="black").pack(anchor=tk.W)
        ttk.Radiobutton(folder_png_bg_frame, text="White background", variable=self.folder_png_bg_option, value="white").pack(anchor=tk.W)
        ttk.Radiobutton(folder_png_bg_frame, text="Custom color", variable=self.folder_png_bg_option, value="custom").pack(anchor=tk.W)
        
        # Custom color selection for folder
        folder_custom_color_frame = ttk.Frame(folder_png_bg_frame)
        folder_custom_color_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.folder_custom_color = tk.StringVar(value="#FFFFFF")
        ttk.Label(folder_custom_color_frame, text="Custom color:").pack(side=tk.LEFT)
        ttk.Entry(folder_custom_color_frame, textvariable=self.folder_custom_color, width=10).pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(folder_custom_color_frame, text="Choose", command=self.choose_folder_custom_color).pack(side=tk.LEFT)
        
        # Process button
        ttk.Button(folder_frame, text="🔄 Process Folder", command=self.process_folder, style='Modern.TButton').pack(pady=10)
        
        # Progress bar
        self.folder_progress = ttk.Progressbar(folder_frame, mode='indeterminate')
        self.folder_progress.pack(fill=tk.X, pady=(10, 0))
        
        # Status
        self.folder_status_var = tk.StringVar()
        status_label = ttk.Label(folder_frame, textvariable=self.folder_status_var, wraplength=800)
        status_label.pack(anchor=tk.W, pady=(10, 0))
    
    def create_zip_tab(self):
        # Zip Processing Tab
        zip_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(zip_frame, text="🗜️ Zip Processing")
        
        # Zip file selection
        ttk.Label(zip_frame, text="Select Zip File:", font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        zip_select_frame = ttk.Frame(zip_frame)
        zip_select_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.zip_path_var = tk.StringVar()
        ttk.Entry(zip_select_frame, textvariable=self.zip_path_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(zip_select_frame, text="Browse", command=self.browse_zip_file, style='Modern.TButton').pack(side=tk.RIGHT)
        
        # Dimensions
        ttk.Label(zip_frame, text="Dimensions:", font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        zip_dim_frame = ttk.Frame(zip_frame)
        zip_dim_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(zip_dim_frame, text="Width:").pack(side=tk.LEFT)
        self.zip_width_var = tk.StringVar(value="800")
        ttk.Spinbox(zip_dim_frame, from_=1, to=10000, textvariable=self.zip_width_var, width=10).pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(zip_dim_frame, text="Height:").pack(side=tk.LEFT)
        self.zip_height_var = tk.StringVar(value="600")
        ttk.Spinbox(zip_dim_frame, from_=1, to=10000, textvariable=self.zip_height_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # Options
        self.zip_maintain_aspect = tk.BooleanVar(value=True)
        ttk.Checkbutton(zip_frame, text="Maintain aspect ratio", variable=self.zip_maintain_aspect).pack(anchor=tk.W, pady=(0, 10))
        
        # PNG Background Color Selection for Zip
        zip_png_bg_frame = ttk.LabelFrame(zip_frame, text="PNG Background Color", padding="10")
        zip_png_bg_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.zip_png_bg_option = tk.StringVar(value="auto")
        ttk.Radiobutton(zip_png_bg_frame, text="Auto-detect from image", variable=self.zip_png_bg_option, value="auto").pack(anchor=tk.W)
        ttk.Radiobutton(zip_png_bg_frame, text="Black background", variable=self.zip_png_bg_option, value="black").pack(anchor=tk.W)
        ttk.Radiobutton(zip_png_bg_frame, text="White background", variable=self.zip_png_bg_option, value="white").pack(anchor=tk.W)
        ttk.Radiobutton(zip_png_bg_frame, text="Custom color", variable=self.zip_png_bg_option, value="custom").pack(anchor=tk.W)
        
        # Custom color selection for zip
        zip_custom_color_frame = ttk.Frame(zip_png_bg_frame)
        zip_custom_color_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.zip_custom_color = tk.StringVar(value="#FFFFFF")
        ttk.Label(zip_custom_color_frame, text="Custom color:").pack(side=tk.LEFT)
        ttk.Entry(zip_custom_color_frame, textvariable=self.zip_custom_color, width=10).pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(zip_custom_color_frame, text="Choose", command=self.choose_zip_custom_color).pack(side=tk.LEFT)
        
        # Process button
        ttk.Button(zip_frame, text="🔄 Process Zip File", command=self.process_zip_file, style='Modern.TButton').pack(pady=10)
        
        # Progress bar
        self.zip_progress = ttk.Progressbar(zip_frame, mode='indeterminate')
        self.zip_progress.pack(fill=tk.X, pady=(10, 0))
        
        # Status
        self.zip_status_var = tk.StringVar()
        ttk.Label(zip_frame, textvariable=self.zip_status_var, wraplength=800).pack(anchor=tk.W, pady=(10, 0))
    
    # Event handlers
    def browse_single_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.single_image_var.set(file_path)
            self.load_image_preview(file_path)
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder Containing Images")
        if folder_path:
            self.folder_path_var.set(folder_path)
    
    def browse_zip_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Zip File",
            filetypes=[("Zip files", "*.zip"), ("All files", "*.*")]
        )
        if file_path:
            self.zip_path_var.set(file_path)
    
    def choose_custom_color(self):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(title="Choose Background Color")
        if color[1]:  # If user didn't cancel
            self.custom_color.set(color[1])
    
    def choose_folder_custom_color(self):
        """Open color chooser dialog for folder processing"""
        color = colorchooser.askcolor(title="Choose Background Color")
        if color[1]:  # If user didn't cancel
            self.folder_custom_color.set(color[1])
    
    def choose_zip_custom_color(self):
        """Open color chooser dialog for zip processing"""
        color = colorchooser.askcolor(title="Choose Background Color")
        if color[1]:  # If user didn't cancel
            self.zip_custom_color.set(color[1])
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def load_image_preview(self, image_path):
        try:
            # Load and resize image for preview
            image = Image.open(image_path)
            # Resize for preview (max 300x300)
            image.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update preview
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo  # Keep a reference
            
        except Exception as e:
            self.preview_label.configure(image="", text=f"Error loading preview:\n{str(e)}")
    
    def process_single_image(self):
        if not self.single_image_var.get():
            messagebox.showerror("Error", "Please select an image file first")
            return
        
        def process():
            try:
                self.status_var.set("Processing single image...")
                self.root.update()
                
                width = int(self.single_width_var.get())
                height = int(self.single_height_var.get())
                maintain_aspect = self.single_maintain_aspect.get()
                
                # Get PNG background color option
                png_bg_option = self.png_bg_option.get()
                custom_color = None
                if png_bg_option == "custom":
                    custom_color = self.hex_to_rgb(self.custom_color.get())
                
                result = self.resizer.process_single_image_file(
                    self.single_image_var.get(), width, height, maintain_aspect, png_bg_option, custom_color
                )
                
                if result:
                    self.single_status_var.set(f"✅ Success")
                    messagebox.showinfo("Success", f"Image processed successfully!\n\n{result}")
                else:
                    self.single_status_var.set("❌ Failed to process image")
                
                self.status_var.set("Ready")
                
            except Exception as e:
                self.single_status_var.set(f"❌ Error: {str(e)}")
                messagebox.showerror("Error", f"Failed to process image: {str(e)}")
                self.status_var.set("Ready")
        
        threading.Thread(target=process, daemon=True).start()
    
    def process_folder(self):
        if not self.folder_path_var.get():
            messagebox.showerror("Error", "Please select a folder first")
            return
        
        def process():
            try:
                self.status_var.set("Processing folder...")
                self.folder_progress.start()
                self.root.update()
                
                width = int(self.folder_width_var.get())
                height = int(self.folder_height_var.get())
                maintain_aspect = self.folder_maintain_aspect.get()
                
                # Get PNG background color option
                png_bg_option = self.folder_png_bg_option.get()
                custom_color = None
                if png_bg_option == "custom":
                    custom_color = self.hex_to_rgb(self.folder_custom_color.get())
                
                processed_files, status = self.resizer.process_folder(
                    self.folder_path_var.get(), width, height, maintain_aspect, png_bg_option, custom_color
                )
                
                self.folder_progress.stop()
                
                if processed_files:
                    self.folder_status_var.set(f"✅ Success - {len(processed_files)} images processed")
                    messagebox.showinfo("Success", f"Folder processed successfully!\n\n{status}")
                else:
                    self.folder_status_var.set(f"❌ Failed")
                    messagebox.showerror("Error", status)
                
                self.status_var.set("Ready")
                
            except Exception as e:
                self.folder_progress.stop()
                self.folder_status_var.set(f"❌ Error: {str(e)}")
                messagebox.showerror("Error", f"Failed to process folder: {str(e)}")
                self.status_var.set("Ready")
        
        threading.Thread(target=process, daemon=True).start()
    
    def process_zip_file(self):
        if not self.zip_path_var.get():
            messagebox.showerror("Error", "Please select a zip file first")
            return
        
        def process():
            try:
                self.status_var.set("Processing zip file...")
                self.zip_progress.start()
                self.root.update()
                
                width = int(self.zip_width_var.get())
                height = int(self.zip_height_var.get())
                maintain_aspect = self.zip_maintain_aspect.get()
                
                # Get PNG background color option
                png_bg_option = self.zip_png_bg_option.get()
                custom_color = None
                if png_bg_option == "custom":
                    custom_color = self.hex_to_rgb(self.zip_custom_color.get())
                
                output_zip, status = self.resizer.process_zip_file(
                    self.zip_path_var.get(), width, height, maintain_aspect, png_bg_option, custom_color
                )
                
                self.zip_progress.stop()
                
                if output_zip:
                    self.zip_status_var.set(f"✅ Success - ZIP processed")
                    
                    # Ask user where to save the output zip
                    save_path = filedialog.asksaveasfilename(
                        title="Save Resized Images Zip",
                        defaultextension=".zip",
                        filetypes=[("Zip files", "*.zip")]
                    )
                    
                    if save_path:
                        shutil.move(output_zip, save_path)
                        messagebox.showinfo("Success", f"Zip file processed and saved successfully!\n\n{status}\n\nSaved to: {save_path}")
                    else:
                        # Clean up if user cancelled save
                        if os.path.exists(output_zip):
                            os.remove(output_zip)
                else:
                    self.zip_status_var.set(f"❌ Failed")
                    messagebox.showerror("Error", status)
                
                self.status_var.set("Ready")
                
            except Exception as e:
                self.zip_progress.stop()
                self.zip_status_var.set(f"❌ Error: {str(e)}")
                messagebox.showerror("Error", f"Failed to process zip file: {str(e)}")
                self.status_var.set("Ready")
        
        threading.Thread(target=process, daemon=True).start()


class ImageResizer:
    def __init__(self):
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
    
    def get_background_color(self, image: Image.Image) -> tuple:
        """Detect background color from image corners"""
        try:
            # Ensure image is in RGB mode
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            width, height = image.size
            
            # Sample corner pixels (avoid single pixel - use small area)
            corner_size = min(10, width//10, height//10)  # 10x10 or smaller
            
            corners = []
            # Top-left corner
            corners.extend(list(image.crop((0, 0, corner_size, corner_size)).getdata()))
            # Top-right corner  
            corners.extend(list(image.crop((width-corner_size, 0, width, corner_size)).getdata()))
            # Bottom-left corner
            corners.extend(list(image.crop((0, height-corner_size, corner_size, height)).getdata()))
            # Bottom-right corner
            corners.extend(list(image.crop((width-corner_size, height-corner_size, width, height)).getdata()))
            
            # Calculate average color
            if corners:
                avg_r = sum(pixel[0] for pixel in corners) // len(corners)
                avg_g = sum(pixel[1] for pixel in corners) // len(corners)
                avg_b = sum(pixel[2] for pixel in corners) // len(corners)
                return (avg_r, avg_g, avg_b)
            
        except Exception:
            pass
        
        # Fallback to white if detection fails
        return (255, 255, 255)

    def resize_image(self, image: Image.Image, width: int, height: int, maintain_aspect: bool = True, png_bg_option: str = "auto", custom_color: tuple = None, is_png: bool = False) -> Image.Image:
        """Add smart background canvas padding to image to reach target dimensions"""
        
        # Special handling for PNG files
        if image.format == 'PNG' or is_png:
            # Check if PNG has transparency
            has_transparency = False
            if image.mode == 'RGBA':
                alpha = image.getchannel('A')
                has_transparency = any(pixel < 255 for pixel in alpha.getdata())
            
            # Choose background color based on user selection
            if png_bg_option == "black":
                bg_color = (0, 0, 0)
            elif png_bg_option == "white":
                bg_color = (255, 255, 255)
            elif png_bg_option == "custom" and custom_color:
                bg_color = custom_color
            elif png_bg_option == "auto":
                if has_transparency:
                    # For transparent PNG, use black background by default
                    bg_color = (0, 0, 0)
                else:
                    # For non-transparent PNG, detect background color
                    bg_color = self.get_background_color(image)
            else:
                # Fallback to auto-detection
                bg_color = self.get_background_color(image)
        else:
            # For non-PNG images, use smart background detection
            bg_color = self.get_background_color(image)
        
        # Create canvas with detected/selected background color
        canvas = Image.new('RGB', (width, height), color=bg_color)
        
        # Calculate position to center the original image
        orig_width, orig_height = image.size
        
        if maintain_aspect:
            # Scale down image if it's larger than target canvas
            if orig_width > width or orig_height > height:
                image.thumbnail((width, height), Image.Resampling.LANCZOS)
                orig_width, orig_height = image.size
        
        # Calculate center position
        x = (width - orig_width) // 2
        y = (height - orig_height) // 2
        
        # Handle different image modes for pasting
        if image.mode == 'RGBA':
            # For RGBA images (transparent PNG), paste with alpha mask
            canvas.paste(image, (x, y), image)
        else:
            # Ensure image has RGB mode for pasting
            if image.mode in ('LA', 'P'):
                image = image.convert('RGB')
            # Paste original image onto smart background canvas
            canvas.paste(image, (x, y))
        
        return canvas
    
    def process_single_image_file(self, image_path: str, width: int, height: int, maintain_aspect: bool = True, png_bg_option: str = "auto", custom_color: tuple = None) -> str:
        """Process a single image file and save it"""
        try:
            # Open and resize the image
            image = Image.open(image_path)
            
            # Check if file is PNG based on extension
            is_png = image_path.lower().endswith(('.png',))
            
            original_size = image.size
            resized_image = self.resize_image(image, width, height, maintain_aspect, png_bg_option, custom_color, is_png)
            new_size = resized_image.size
            
            # Ask user where to save the resized image
            from tkinter import filedialog
            name, ext = os.path.splitext(image_path)
            suggested_name = f"{os.path.basename(name)}{ext}"
            
            # Ask user for save location
            output_path = filedialog.asksaveasfilename(
                title="Save Resized Image",
                defaultextension=ext,
                initialfile=suggested_name,
                filetypes=[
                    ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                    ("All files", "*.*")
                ]
            )
            
            if not output_path:
                return "Save cancelled by user"
                
            resized_image.save(output_path, quality=95)
            
            return f"Original: {original_size[0]}x{original_size[1]} → Resized: {new_size[0]}x{new_size[1]}\nSaved to: {output_path}"
            
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")
    
    def process_folder(self, folder_path: str, width: int, height: int, maintain_aspect: bool = True, png_bg_option: str = "auto", custom_color: tuple = None) -> Tuple[List[str], str]:
        """Process all images in a folder"""
        if not folder_path or not os.path.exists(folder_path):
            return [], "Invalid folder path"
        
        processed_files = []
        error_files = []
        
        # Create output directory
        output_dir = os.path.join(os.path.dirname(folder_path), f"resized_{os.path.basename(folder_path)}")
        os.makedirs(output_dir, exist_ok=True)
        
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(self.supported_formats):
                try:
                    file_path = os.path.join(folder_path, filename)
                    image = Image.open(file_path)
                    
                    # Check if file is PNG based on extension
                    is_png = filename.lower().endswith(('.png',))
                    
                    resized_image = self.resize_image(image, width, height, maintain_aspect, png_bg_option, custom_color, is_png)
                    
                    # Save resized image (without _resized suffix)
                    output_path = os.path.join(output_dir, filename)
                    resized_image.save(output_path, quality=95)
                    processed_files.append(output_path)
                    
                except Exception as e:
                    error_files.append(f"{filename}: {str(e)}")
        
        status = f"Processed {len(processed_files)} images successfully\nOutput folder: {output_dir}"
        if error_files:
            status += f"\nErrors with {len(error_files)} files: {'; '.join(error_files[:3])}"
        
        return processed_files, status
    
    def process_zip_file(self, zip_path: str, width: int, height: int, maintain_aspect: bool = True, png_bg_option: str = "auto", custom_color: tuple = None) -> Tuple[str, str]:
        """Process images from a zip file and return a new zip with resized images"""
        try:
            # Create temporary directories
            temp_extract_dir = tempfile.mkdtemp()
            temp_output_dir = tempfile.mkdtemp()
            
            # Extract zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_dir)
            
            processed_count = 0
            error_files = []
            
            # Process all images in extracted folder
            for root, dirs, files in os.walk(temp_extract_dir):
                for filename in files:
                    if filename.lower().endswith(self.supported_formats):
                        try:
                            file_path = os.path.join(root, filename)
                            image = Image.open(file_path)
                            
                            # Check if file is PNG based on extension
                            is_png = filename.lower().endswith(('.png',))
                            
                            resized_image = self.resize_image(image, width, height, maintain_aspect, png_bg_option, custom_color, is_png)
                            
                            # Maintain folder structure in output
                            rel_path = os.path.relpath(file_path, temp_extract_dir)
                            output_path = os.path.join(temp_output_dir, rel_path)
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            
                            # Save without _resized suffix (same filename as original)
                            resized_image.save(output_path, quality=95)
                            processed_count += 1
                            
                        except Exception as e:
                            error_files.append(f"{filename}: {str(e)}")
            
            # Create output zip file
            output_zip_path = tempfile.mktemp(suffix='.zip')
            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                for root, dirs, files in os.walk(temp_output_dir):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        arcname = os.path.relpath(file_path, temp_output_dir)
                        zip_out.write(file_path, arcname)
            
            # Clean up temporary directories
            shutil.rmtree(temp_extract_dir)
            shutil.rmtree(temp_output_dir)
            
            status = f"Processed {processed_count} images successfully"
            if error_files:
                status += f"\nErrors with {len(error_files)} files: {'; '.join(error_files[:3])}"
            
            return output_zip_path, status
            
        except Exception as e:
            return None, f"Error processing zip file: {str(e)}"


def main():
    root = tk.Tk()
    app = ModernImageResizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main() 
