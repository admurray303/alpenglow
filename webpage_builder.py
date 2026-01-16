#!/usr/bin/env python3
"""
Visual Webpage Builder
A drag-and-drop webpage editor with styling controls and HTML/CSS export
"""

import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox, font as tkfont
import json
from datetime import datetime

class Element:
    """Represents a webpage element with styling properties"""
    def __init__(self, element_type, x, y, width=150, height=40):
        self.type = element_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = self.get_default_text()
        self.bg_color = "#ffffff"
        self.text_color = "#000000"
        self.font_family = "Arial"
        self.font_size = 14
        self.font_weight = "normal"
        self.font_style = "normal"
        self.border_width = 1
        self.border_color = "#cccccc"
        self.border_radius = 0
        self.padding = 10
        self.margin = 0
        self.text_align = "left"
        
    def get_default_text(self):
        defaults = {
            "heading": "Heading Text",
            "paragraph": "Paragraph text goes here. Click to edit.",
            "button": "Button",
            "div": "Container"
        }
        return defaults.get(self.type, "Element")
    
    def get_html_tag(self):
        tags = {
            "heading": "h1",
            "paragraph": "p",
            "button": "button",
            "div": "div"
        }
        return tags.get(self.type, "div")

class WebpageBuilder(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Visual Webpage Builder")
        self.geometry("1400x900")
        
        self.elements = []
        self.selected_element = None
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.canvas_items = {}  # Maps elements to canvas item IDs
        
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the user interface"""
        # Main container
        main_container = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Element palette
        left_panel = ttk.Frame(main_container, width=200)
        main_container.add(left_panel, weight=0)
        self.setup_palette(left_panel)
        
        # Center panel - Canvas
        center_panel = ttk.Frame(main_container)
        main_container.add(center_panel, weight=1)
        self.setup_canvas(center_panel)
        
        # Right panel - Properties
        right_panel = ttk.Frame(main_container, width=300)
        main_container.add(right_panel, weight=0)
        self.setup_properties_panel(right_panel)
        
    def setup_palette(self, parent):
        """Create the element palette"""
        ttk.Label(parent, text="Elements", font=("Arial", 14, "bold")).pack(pady=10)
        
        elements = [
            ("Heading", "heading"),
            ("Paragraph", "paragraph"),
            ("Button", "button"),
            ("Container", "div")
        ]
        
        for label, element_type in elements:
            btn = ttk.Button(
                parent,
                text=f"+ {label}",
                command=lambda t=element_type: self.add_element(t)
            )
            btn.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        # Export button
        export_btn = ttk.Button(
            parent,
            text="Export HTML/CSS",
            command=self.export_code
        )
        export_btn.pack(fill=tk.X, padx=10, pady=5)
        
        # Clear canvas button
        clear_btn = ttk.Button(
            parent,
            text="Clear Canvas",
            command=self.clear_canvas
        )
        clear_btn.pack(fill=tk.X, padx=10, pady=5)
        
    def setup_canvas(self, parent):
        """Create the main canvas area"""
        # Toolbar
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(toolbar, text="Canvas Size:").pack(side=tk.LEFT, padx=5)
        
        self.canvas_width_var = tk.StringVar(value="800")
        width_entry = ttk.Entry(toolbar, textvariable=self.canvas_width_var, width=8)
        width_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(toolbar, text="x").pack(side=tk.LEFT)
        
        self.canvas_height_var = tk.StringVar(value="600")
        height_entry = ttk.Entry(toolbar, textvariable=self.canvas_height_var, width=8)
        height_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(toolbar, text="Resize", command=self.resize_canvas).pack(side=tk.LEFT, padx=5)
        
        # Canvas with scrollbars
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas
        self.canvas = tk.Canvas(
            canvas_frame,
            bg="white",
            width=800,
            height=600,
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set,
            scrollregion=(0, 0, 800, 600)
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Delete>", self.delete_selected)
        
    def setup_properties_panel(self, parent):
        """Create the properties panel"""
        ttk.Label(parent, text="Properties", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.properties_frame = scrollable_frame
        self.property_widgets = {}
        
        self.show_no_selection()
        
    def show_no_selection(self):
        """Display message when no element is selected"""
        for widget in self.properties_frame.winfo_children():
            widget.destroy()
        self.property_widgets.clear()
        
        ttk.Label(
            self.properties_frame,
            text="Select an element\nto edit properties",
            justify=tk.CENTER
        ).pack(pady=50)
        
    def show_properties(self, element):
        """Display properties for selected element"""
        for widget in self.properties_frame.winfo_children():
            widget.destroy()
        self.property_widgets.clear()
        
        # Text content
        self.add_property_field("Text:", element.text, "text", element)
        
        # Dimensions
        ttk.Label(self.properties_frame, text="Dimensions", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 5))
        self.add_property_field("Width:", str(element.width), "width", element, input_type="int")
        self.add_property_field("Height:", str(element.height), "height", element, input_type="int")
        
        # Colors
        ttk.Label(self.properties_frame, text="Colors", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 5))
        self.add_color_picker("Background:", element.bg_color, "bg_color", element)
        self.add_color_picker("Text Color:", element.text_color, "text_color", element)
        
        # Typography
        ttk.Label(self.properties_frame, text="Typography", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Font family
        font_frame = ttk.Frame(self.properties_frame)
        font_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Label(font_frame, text="Font:", width=12).pack(side=tk.LEFT)
        font_var = tk.StringVar(value=element.font_family)
        font_combo = ttk.Combobox(font_frame, textvariable=font_var, width=15, 
                                  values=["Arial", "Helvetica", "Times New Roman", "Georgia", "Verdana", "Courier"])
        font_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        font_combo.bind("<<ComboboxSelected>>", lambda e: self.update_property(element, "font_family", font_var.get()))
        self.property_widgets["font_family"] = font_var
        
        self.add_property_field("Font Size:", str(element.font_size), "font_size", element, input_type="int")
        
        # Font weight
        weight_frame = ttk.Frame(self.properties_frame)
        weight_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Label(weight_frame, text="Weight:", width=12).pack(side=tk.LEFT)
        weight_var = tk.StringVar(value=element.font_weight)
        weight_combo = ttk.Combobox(weight_frame, textvariable=weight_var, width=15, 
                                    values=["normal", "bold"])
        weight_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        weight_combo.bind("<<ComboboxSelected>>", lambda e: self.update_property(element, "font_weight", weight_var.get()))
        self.property_widgets["font_weight"] = weight_var
        
        # Font style
        style_frame = ttk.Frame(self.properties_frame)
        style_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Label(style_frame, text="Style:", width=12).pack(side=tk.LEFT)
        style_var = tk.StringVar(value=element.font_style)
        style_combo = ttk.Combobox(style_frame, textvariable=style_var, width=15, 
                                   values=["normal", "italic"])
        style_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        style_combo.bind("<<ComboboxSelected>>", lambda e: self.update_property(element, "font_style", style_var.get()))
        self.property_widgets["font_style"] = style_var
        
        # Text align
        align_frame = ttk.Frame(self.properties_frame)
        align_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Label(align_frame, text="Align:", width=12).pack(side=tk.LEFT)
        align_var = tk.StringVar(value=element.text_align)
        align_combo = ttk.Combobox(align_frame, textvariable=align_var, width=15, 
                                   values=["left", "center", "right"])
        align_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        align_combo.bind("<<ComboboxSelected>>", lambda e: self.update_property(element, "text_align", align_var.get()))
        self.property_widgets["text_align"] = align_var
        
        # Border
        ttk.Label(self.properties_frame, text="Border", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 5))
        self.add_property_field("Border Width:", str(element.border_width), "border_width", element, input_type="int")
        self.add_color_picker("Border Color:", element.border_color, "border_color", element)
        self.add_property_field("Border Radius:", str(element.border_radius), "border_radius", element, input_type="int")
        
        # Spacing
        ttk.Label(self.properties_frame, text="Spacing", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 5))
        self.add_property_field("Padding:", str(element.padding), "padding", element, input_type="int")
        self.add_property_field("Margin:", str(element.margin), "margin", element, input_type="int")
        
        # Delete button
        ttk.Button(
            self.properties_frame,
            text="Delete Element",
            command=lambda: self.delete_element(element)
        ).pack(pady=20)
        
    def add_property_field(self, label, value, prop_name, element, input_type="text"):
        """Add a text input field for a property"""
        frame = ttk.Frame(self.properties_frame)
        frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(frame, text=label, width=12).pack(side=tk.LEFT)
        
        var = tk.StringVar(value=value)
        entry = ttk.Entry(frame, textvariable=var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def on_change(*args):
            val = var.get()
            if input_type == "int":
                try:
                    val = int(val)
                except ValueError:
                    return
            self.update_property(element, prop_name, val)
        
        var.trace("w", on_change)
        self.property_widgets[prop_name] = var
        
    def add_color_picker(self, label, color, prop_name, element):
        """Add a color picker for a property"""
        frame = ttk.Frame(self.properties_frame)
        frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(frame, text=label, width=12).pack(side=tk.LEFT)
        
        color_var = tk.StringVar(value=color)
        entry = ttk.Entry(frame, textvariable=color_var, width=10)
        entry.pack(side=tk.LEFT, padx=2)
        
        color_display = tk.Frame(frame, width=30, height=20, bg=color)
        color_display.pack(side=tk.LEFT, padx=2)
        
        def pick_color():
            color = colorchooser.askcolor(initialcolor=color_var.get())[1]
            if color:
                color_var.set(color)
                color_display.config(bg=color)
                self.update_property(element, prop_name, color)
        
        ttk.Button(frame, text="Pick", command=pick_color, width=5).pack(side=tk.LEFT)
        
        def on_change(*args):
            self.update_property(element, prop_name, color_var.get())
            try:
                color_display.config(bg=color_var.get())
            except:
                pass
        
        color_var.trace("w", on_change)
        self.property_widgets[prop_name] = color_var
        
    def update_property(self, element, prop_name, value):
        """Update an element's property and redraw"""
        setattr(element, prop_name, value)
        self.redraw_canvas()
        
    def add_element(self, element_type):
        """Add a new element to the canvas"""
        # Add element at center of visible area
        x = 100
        y = 100 + len(self.elements) * 60
        
        element = Element(element_type, x, y)
        self.elements.append(element)
        self.redraw_canvas()
        
    def redraw_canvas(self):
        """Redraw all elements on the canvas"""
        self.canvas.delete("all")
        self.canvas_items.clear()
        
        for element in self.elements:
            self.draw_element(element)
            
    def draw_element(self, element):
        """Draw a single element on the canvas"""
        x, y = element.x, element.y
        w, h = element.width, element.height
        
        # Draw rectangle
        rect_id = self.canvas.create_rectangle(
            x, y, x + w, y + h,
            fill=element.bg_color,
            outline=element.border_color,
            width=element.border_width,
            tags="element"
        )
        
        # Draw text
        font_config = (element.font_family, element.font_size)
        if element.font_weight == "bold":
            font_config = (element.font_family, element.font_size, "bold")
        if element.font_style == "italic":
            font_config = font_config + ("italic",) if len(font_config) == 3 else (element.font_family, element.font_size, "italic")
            
        text_id = self.canvas.create_text(
            x + w/2, y + h/2,
            text=element.text,
            fill=element.text_color,
            font=font_config,
            width=w - 20,
            tags="element"
        )
        
        # Highlight if selected
        if element == self.selected_element:
            self.canvas.create_rectangle(
                x-2, y-2, x + w+2, y + h+2,
                outline="#007bff",
                width=2,
                tags="selection"
            )
        
        self.canvas_items[element] = (rect_id, text_id)
        
    def on_canvas_click(self, event):
        """Handle canvas click events"""
        clicked_element = self.find_element_at(event.x, event.y)
        
        if clicked_element:
            self.selected_element = clicked_element
            self.dragging = True
            self.drag_start_x = event.x - clicked_element.x
            self.drag_start_y = event.y - clicked_element.y
            self.show_properties(clicked_element)
        else:
            self.selected_element = None
            self.show_no_selection()
            
        self.redraw_canvas()
        
    def on_canvas_drag(self, event):
        """Handle canvas drag events"""
        if self.dragging and self.selected_element:
            self.selected_element.x = event.x - self.drag_start_x
            self.selected_element.y = event.y - self.drag_start_y
            self.redraw_canvas()
            
    def on_canvas_release(self, event):
        """Handle mouse release events"""
        self.dragging = False
        
    def find_element_at(self, x, y):
        """Find which element is at the given coordinates"""
        # Check in reverse order (top to bottom)
        for element in reversed(self.elements):
            if (element.x <= x <= element.x + element.width and
                element.y <= y <= element.y + element.height):
                return element
        return None
        
    def delete_element(self, element):
        """Delete an element"""
        if element in self.elements:
            self.elements.remove(element)
            self.selected_element = None
            self.show_no_selection()
            self.redraw_canvas()
            
    def delete_selected(self, event=None):
        """Delete the selected element"""
        if self.selected_element:
            self.delete_element(self.selected_element)
            
    def clear_canvas(self):
        """Clear all elements from canvas"""
        if messagebox.askyesno("Clear Canvas", "Are you sure you want to clear all elements?"):
            self.elements.clear()
            self.selected_element = None
            self.show_no_selection()
            self.redraw_canvas()
            
    def resize_canvas(self):
        """Resize the canvas"""
        try:
            width = int(self.canvas_width_var.get())
            height = int(self.canvas_height_var.get())
            self.canvas.config(width=width, height=height, scrollregion=(0, 0, width, height))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dimensions")
            
    def export_code(self):
        """Export HTML and CSS code"""
        if not self.elements:
            messagebox.showwarning("No Elements", "Add some elements before exporting!")
            return
            
        html, css = self.generate_code()
        
        # Save files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"webpage_{timestamp}"
        
        html_file = filedialog.asksaveasfilename(
            defaultextension=".html",
            initialfile=f"{base_name}.html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if html_file:
            with open(html_file, "w") as f:
                f.write(html)
                
            css_file = html_file.replace(".html", ".css")
            with open(css_file, "w") as f:
                f.write(css)
                
            messagebox.showinfo("Success", f"Files exported:\n{html_file}\n{css_file}")
            
    def generate_code(self):
        """Generate HTML and CSS code"""
        # Generate CSS
        css_lines = ["/* Generated by Visual Webpage Builder */", ""]
        css_lines.append("body {")
        css_lines.append("    margin: 0;")
        css_lines.append("    padding: 20px;")
        css_lines.append("    font-family: Arial, sans-serif;")
        css_lines.append("}")
        css_lines.append("")
        css_lines.append(".webpage-container {")
        css_lines.append("    position: relative;")
        css_lines.append(f"    width: {self.canvas_width_var.get()}px;")
        css_lines.append(f"    min-height: {self.canvas_height_var.get()}px;")
        css_lines.append("}")
        css_lines.append("")
        
        for i, element in enumerate(self.elements):
            class_name = f"element-{i}"
            css_lines.append(f".{class_name} {{")
            css_lines.append(f"    position: absolute;")
            css_lines.append(f"    left: {element.x}px;")
            css_lines.append(f"    top: {element.y}px;")
            css_lines.append(f"    width: {element.width}px;")
            css_lines.append(f"    height: {element.height}px;")
            css_lines.append(f"    background-color: {element.bg_color};")
            css_lines.append(f"    color: {element.text_color};")
            css_lines.append(f"    font-family: {element.font_family};")
            css_lines.append(f"    font-size: {element.font_size}px;")
            css_lines.append(f"    font-weight: {element.font_weight};")
            css_lines.append(f"    font-style: {element.font_style};")
            css_lines.append(f"    text-align: {element.text_align};")
            css_lines.append(f"    border: {element.border_width}px solid {element.border_color};")
            css_lines.append(f"    border-radius: {element.border_radius}px;")
            css_lines.append(f"    padding: {element.padding}px;")
            css_lines.append(f"    margin: {element.margin}px;")
            css_lines.append(f"    box-sizing: border-box;")
            if element.type == "button":
                css_lines.append(f"    cursor: pointer;")
            css_lines.append("}")
            css_lines.append("")
            
        css = "\n".join(css_lines)
        
        # Generate HTML
        html_lines = ["<!DOCTYPE html>", "<html lang=\"en\">", "<head>"]
        html_lines.append("    <meta charset=\"UTF-8\">")
        html_lines.append("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
        html_lines.append("    <title>My Webpage</title>")
        html_lines.append("    <link rel=\"stylesheet\" href=\"" + html_lines[0].replace(".html", ".css").split("/")[-1] + "\">")
        html_lines.append("</head>")
        html_lines.append("<body>")
        html_lines.append("    <div class=\"webpage-container\">")
        
        for i, element in enumerate(self.elements):
            tag = element.get_html_tag()
            class_name = f"element-{i}"
            html_lines.append(f"        <{tag} class=\"{class_name}\">{element.text}</{tag}>")
            
        html_lines.append("    </div>")
        html_lines.append("</body>")
        html_lines.append("</html>")
        
        html = "\n".join(html_lines)
        
        return html, css

def main():
    app = WebpageBuilder()
    app.mainloop()

if __name__ == "__main__":
    main()
