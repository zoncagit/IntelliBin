"""
IntelliBin Simulator - Waste Disposal UI
Separates dangerous and non-dangerous disposables.
"""

import customtkinter as ctk
from typing import Optional
import sys
from pathlib import Path
import tkinter as tk
from datetime import datetime
from PIL import Image

# ============================================
# DESIGN SYSTEM - TACTICAL HUD THEME
# ============================================

COLORS = {
    # Primary Accent - Ambre / Tactical Orange
    "accent_primary": "#DB835C",
    "accent_hover": "#E59A78",
    
    # Backgrounds - Dark Mode
    "bg_pure": "#050505",
    "bg_card": "#1A1A1A",
    "bg_elevated": "#252525",
    
    # Text
    "text_main": "#FFFFFF",
    "text_secondary": "#989796",
    "text_muted": "#6E6E6E",
    
    # Status Colors
    "alert_error": "#FF3B30",
    "status_success": "#34C759",
    "status_warning": "#FF9500",
    "danger": "#E53935",
    "safe": "#43A047",
    
    # Borders
    "border_glass": "#3D2E24",
    "border_subtle": "#2A2A2A",
}

# All fonts use JetBrains Mono (falls back to Menlo on macOS)
_FONT = "JetBrains Mono"

FONTS = {
    "logo": (_FONT, 28, "bold"),
    "heading": (_FONT, 18, "bold"),
    "subheading": (_FONT, 14, "bold"),
    "body": (_FONT, 12),
    "body_bold": (_FONT, 12, "bold"),
    "small": (_FONT, 11),
    "tiny": (_FONT, 9),
    "button": (_FONT, 11, "bold"),
}

# ============================================
# DISPOSABLES DATA
# ============================================

DISPOSABLES = [
    # Non-dangerous items
    {"name": "Paper", "dangerous": False, "category": "recyclable"},
    {"name": "Cardboard", "dangerous": False, "category": "recyclable"},
    {"name": "Plastic Bottle", "dangerous": False, "category": "recyclable"},
    {"name": "Plastic Bag", "dangerous": False, "category": "recyclable"},
    {"name": "Food Wrapper", "dangerous": False, "category": "general"},
    {"name": "Tissue Paper", "dangerous": False, "category": "general"},
    {"name": "Newspaper", "dangerous": False, "category": "recyclable"},
    {"name": "Magazine", "dangerous": False, "category": "recyclable"},
    
    # Dangerous items
    {"name": "Glass Bottle", "dangerous": True, "category": "glass"},
    {"name": "Broken Glass", "dangerous": True, "category": "glass"},
    {"name": "Glass Jar", "dangerous": True, "category": "glass"},
    {"name": "Petri Dish (used)", "dangerous": True, "category": "microbio"},
    {"name": "Culture Tube", "dangerous": True, "category": "microbio"},
    {"name": "Biohazard Waste", "dangerous": True, "category": "microbio"},
    {"name": "Contaminated Swab", "dangerous": True, "category": "microbio"},
    {"name": "Aluminium Can", "dangerous": True, "category": "aluminium"},
    {"name": "Aluminium Foil", "dangerous": True, "category": "aluminium"},
    {"name": "Metal Scrap", "dangerous": True, "category": "metals"},
    {"name": "Steel Can", "dangerous": True, "category": "metals"},
    {"name": "Metal Wire", "dangerous": True, "category": "metals"},
    {"name": "Copper Wire", "dangerous": True, "category": "metals"},
    {"name": "Syringe (used)", "dangerous": True, "category": "sharps"},
    {"name": "Scalpel Blade", "dangerous": True, "category": "sharps"},
]

# Container definitions
CONTAINERS = {
    "NON-DANGEROUS": {
        "id": "GENERAL-01",
        "name": "General Waste",
        "accepts": ["recyclable", "general"],
        "dangerous": False,
        "capacity": 1000,
        "current_fill": 0,
        "color": COLORS["safe"],
    },
    "GLASS": {
        "id": "GLASS-01",
        "name": "Glass Container",
        "accepts": ["glass"],
        "dangerous": True,
        "capacity": 500,
        "current_fill": 0,
        "color": "#2196F3",
    },
    "MICROBIO": {
        "id": "BIO-01",
        "name": "Biohazard",
        "accepts": ["microbio"],
        "dangerous": True,
        "capacity": 300,
        "current_fill": 0,
        "color": "#FF9800",
    },
    "ALUMINIUM": {
        "id": "ALU-01",
        "name": "Aluminium",
        "accepts": ["aluminium"],
        "dangerous": True,
        "capacity": 400,
        "current_fill": 0,
        "color": "#9E9E9E",
    },
    "METALS": {
        "id": "METAL-01",
        "name": "Metals",
        "accepts": ["metals"],
        "dangerous": True,
        "capacity": 500,
        "current_fill": 0,
        "color": "#607D8B",
    },
    "SHARPS": {
        "id": "SHARP-01",
        "name": "Sharps",
        "accepts": ["sharps"],
        "dangerous": True,
        "capacity": 200,
        "current_fill": 0,
        "color": "#E91E63",
    },
}


# ============================================
# CUSTOM WIDGETS
# ============================================

class GlassCard(ctk.CTkFrame):
    """A card with glass effect"""
    
    def __init__(self, master, highlight=False, **kwargs):
        border_color = COLORS["accent_primary"] if highlight else COLORS["border_glass"]
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=border_color,
            **kwargs
        )


class StatusDot(ctk.CTkFrame):
    """Status indicator dot"""
    
    def __init__(self, master, status="active", size=8, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        colors = {
            "active": COLORS["accent_primary"],
            "warning": COLORS["status_warning"],
            "error": COLORS["alert_error"],
            "success": COLORS["status_success"],
            "danger": COLORS["danger"],
            "safe": COLORS["safe"],
        }
        
        self.dot = ctk.CTkLabel(
            self,
            text="●",
            font=("Arial", size),
            text_color=colors.get(status, COLORS["accent_primary"])
        )
        self.dot.pack()


class SignatureLine(ctk.CTkFrame):
    """Ambre accent line"""
    
    def __init__(self, master, width=100, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["accent_primary"],
            height=2,
            corner_radius=1,
            **kwargs
        )
        if width:
            self.configure(width=width)


class CompactContainerCard(ctk.CTkFrame):
    """Compact container card"""
    
    def __init__(self, master, container_data: dict, **kwargs):
        is_danger = container_data.get("dangerous", False)
        border_color = COLORS["danger"] if is_danger else COLORS["safe"]
        
        super().__init__(
            master,
            fg_color=COLORS["bg_elevated"],
            corner_radius=8,
            border_width=2,
            border_color=border_color,
            **kwargs
        )
        
        self.data = container_data
        self._create_widgets()
    
    def _create_widgets(self):
        # Header row
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(8, 4))
        
        # Status dot
        status = "danger" if self.data["dangerous"] else "safe"
        dot = StatusDot(header, status=status, size=8)
        dot.pack(side="left", padx=(0, 6))
        
        # Container ID
        ctk.CTkLabel(
            header,
            text=self.data["id"],
            font=FONTS["tiny"],
            text_color=self.data["color"]
        ).pack(side="left")
        
        # Name
        ctk.CTkLabel(
            self,
            text=self.data["name"].upper(),
            font=FONTS["small"],
            text_color=COLORS["text_main"]
        ).pack(anchor="w", padx=8)
        
        # Progress bar
        fill_pct = (self.data["current_fill"] / self.data["capacity"]) * 100
        
        if fill_pct >= 90:
            prog_color = COLORS["alert_error"]
        elif fill_pct >= 70:
            prog_color = COLORS["status_warning"]
        else:
            prog_color = self.data["color"]
        
        progress = ctk.CTkProgressBar(
            self,
            progress_color=prog_color,
            fg_color=COLORS["bg_card"],
            height=4,
            corner_radius=2
        )
        progress.set(fill_pct / 100)
        progress.pack(fill="x", padx=8, pady=(4, 2))
        
        # Fill text
        ctk.CTkLabel(
            self,
            text=f"{fill_pct:.0f}% • {self.data['current_fill']}/{self.data['capacity']}",
            font=FONTS["tiny"],
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=8, pady=(0, 8))


# ============================================
# MAIN APPLICATION
# ============================================

class IntelliBinSimulator(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        self.title("IntelliBin Simulator")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=COLORS["bg_pure"])
        
        # Initialize containers state
        self.containers = {k: dict(v) for k, v in CONTAINERS.items()}
        
        # Disposal log
        self.disposal_log = []
        
        # Create layout
        self._create_layout()
    
    def _create_layout(self):
        """Create the main layout"""
        # Header
        self._create_header()
        
        # Main content
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Two columns: left (input + model) and right (containers + log)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Left column
        self._create_left_column()
        
        # Right column
        self._create_right_column()
    
    def _create_header(self):
        """Create header"""
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20)
        
        # Logo
        logo_frame = ctk.CTkFrame(inner, fg_color="transparent")
        logo_frame.pack(side="left", fill="y")
        
        dot = StatusDot(logo_frame, status="active", size=10)
        dot.pack(side="left", padx=(0, 10), pady=20)
        
        ctk.CTkLabel(
            logo_frame,
            text="INTELLIBIN",
            font=FONTS["logo"],
            text_color=COLORS["accent_primary"]
        ).pack(side="left", pady=20)
        
        ctk.CTkLabel(
            logo_frame,
            text="  WASTE DISPOSAL SYSTEM",
            font=FONTS["tiny"],
            text_color=COLORS["text_secondary"]
        ).pack(side="left", pady=20)
        
        # Signature line
        line_frame = ctk.CTkFrame(inner, fg_color="transparent")
        line_frame.place(x=35, y=55)
        SignatureLine(line_frame, width=140).pack()
        
        # Status
        status_frame = ctk.CTkFrame(inner, fg_color="transparent")
        status_frame.pack(side="right", fill="y")
        
        ctk.CTkLabel(
            status_frame,
            text="SYS_ONLINE",
            font=FONTS["small"],
            text_color=COLORS["status_success"]
        ).pack(pady=25)
    
    def _create_left_column(self):
        """Create left column with input form and model"""
        column = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Input card
        input_card = GlassCard(column)
        input_card.pack(fill="x", pady=(0, 10))
        
        # Title
        header = ctk.CTkFrame(input_card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 8))
        
        StatusDot(header, status="active", size=8).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            header,
            text="DISPOSE_ITEM",
            font=FONTS["subheading"],
            text_color=COLORS["accent_primary"]
        ).pack(side="left")
        
        SignatureLine(input_card, width=80).pack(anchor="w", padx=16, pady=(0, 16))
        
        # Item dropdown label
        ctk.CTkLabel(
            input_card,
            text="SELECT ITEM",
            font=FONTS["tiny"],
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=16, pady=(0, 6))
        
        # Dropdown list (just item names, no tags)
        item_names = [item["name"] for item in DISPOSABLES]
        
        self.selected_item = ctk.StringVar(value=item_names[0])
        self.item_dropdown = ctk.CTkComboBox(
            input_card,
            values=item_names,
            variable=self.selected_item,
            font=FONTS["body"],
            dropdown_font=FONTS["small"],
            height=44,
            corner_radius=8,
            border_color=COLORS["border_glass"],
            fg_color=COLORS["bg_elevated"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_elevated"],
            text_color=COLORS["text_main"],
            state="readonly"
        )
        self.item_dropdown.pack(fill="x", padx=16, pady=(0, 20))
        
        # Dispose button
        self.dispose_btn = ctk.CTkButton(
            input_card,
            text="DISPOSE",
            font=FONTS["button"],
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            corner_radius=8,
            height=44,
            command=self._dispose_item
        )
        self.dispose_btn.pack(fill="x", padx=16, pady=(0, 16))
        
        # Model illustration
        model_card = GlassCard(column)
        model_card.pack(fill="both", expand=True)
        
        self._create_model_illustration(model_card)
    
    def _create_model_illustration(self, parent):
        """Create bin illustration with actual image"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(12, 4))
        
        StatusDot(header, status="active", size=8).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            header,
            text="INTELLIBIN",
            font=FONTS["subheading"],
            text_color=COLORS["accent_primary"]
        ).pack(side="left")
        
        SignatureLine(parent, width=60).pack(anchor="w", padx=12, pady=(0, 8))
        
        # Load and display actual bin image
        image_path = Path(__file__).parent / "bin_image.png"
        
        try:
            # Load image and resize to fit
            pil_image = Image.open(image_path)
            
            # Resize maintaining aspect ratio
            max_size = (200, 200)
            pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Create CTkImage for display
            self.bin_image = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=pil_image.size
            )
            
            # Image label
            image_label = ctk.CTkLabel(
                parent,
                image=self.bin_image,
                text=""
            )
            image_label.pack(pady=10)
            
        except Exception as e:
            # Fallback to text if image fails
            ctk.CTkLabel(
                parent,
                text="[BIN IMAGE]",
                font=FONTS["body"],
                text_color=COLORS["text_muted"]
            ).pack(pady=20)
        
        # Status indicator below image
        status_frame = ctk.CTkFrame(parent, fg_color="transparent")
        status_frame.pack(pady=(0, 12))
        
        StatusDot(status_frame, status="active", size=8).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(
            status_frame,
            text="SYSTEM ONLINE",
            font=FONTS["tiny"],
            text_color=COLORS["status_success"]
        ).pack(side="left")
    
    def _create_right_column(self):
        """Create right column with containers and log"""
        column = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Containers section
        containers_card = GlassCard(column)
        containers_card.pack(fill="x", pady=(0, 10))
        
        # Containers header
        header = ctk.CTkFrame(containers_card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 8))
        
        StatusDot(header, status="active", size=8).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            header,
            text="CONTAINERS",
            font=FONTS["subheading"],
            text_color=COLORS["accent_primary"]
        ).pack(side="left")
        
        SignatureLine(containers_card, width=80).pack(anchor="w", padx=16, pady=(0, 12))
        
        # Container grid - 2 rows
        self.containers_frame = ctk.CTkFrame(containers_card, fg_color="transparent")
        self.containers_frame.pack(fill="x", padx=16, pady=(0, 16))
        
        # Row 1: Non-dangerous (full width)
        self.nondanger_row = ctk.CTkFrame(self.containers_frame, fg_color="transparent")
        self.nondanger_row.pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(
            self.nondanger_row,
            text="NON-DANGEROUS",
            font=FONTS["tiny"],
            text_color=COLORS["safe"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.nondanger_container_frame = ctk.CTkFrame(self.nondanger_row, fg_color="transparent")
        self.nondanger_container_frame.pack(fill="x")
        
        self.container_widgets = {}
        self.container_widgets["NON-DANGEROUS"] = CompactContainerCard(
            self.nondanger_container_frame, self.containers["NON-DANGEROUS"]
        )
        self.container_widgets["NON-DANGEROUS"].pack(fill="x")
        
        # Row 2: Dangerous containers (grid)
        ctk.CTkLabel(
            self.containers_frame,
            text="DANGEROUS",
            font=FONTS["tiny"],
            text_color=COLORS["danger"]
        ).pack(anchor="w", pady=(8, 4))
        
        self.danger_frame = ctk.CTkFrame(self.containers_frame, fg_color="transparent")
        self.danger_frame.pack(fill="x")
        
        danger_containers = ["GLASS", "MICROBIO", "ALUMINIUM", "METALS", "SHARPS"]
        
        for i, key in enumerate(danger_containers):
            col = i % 3
            
            if col == 0:
                row_frame = ctk.CTkFrame(self.danger_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
            
            widget = CompactContainerCard(row_frame, self.containers[key])
            widget.pack(side="left", fill="x", expand=True, padx=(0 if col == 0 else 4, 0))
            self.container_widgets[key] = widget
        
        # Disposal Log section
        log_card = GlassCard(column)
        log_card.pack(fill="both", expand=True)
        
        # Log header
        log_header = ctk.CTkFrame(log_card, fg_color="transparent")
        log_header.pack(fill="x", padx=16, pady=(16, 8))
        
        StatusDot(log_header, status="active", size=8).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            log_header,
            text="DISPOSAL_LOG",
            font=FONTS["subheading"],
            text_color=COLORS["accent_primary"]
        ).pack(side="left")
        
        self.log_count_label = ctk.CTkLabel(
            log_header,
            text="[0 entries]",
            font=FONTS["tiny"],
            text_color=COLORS["text_muted"]
        )
        self.log_count_label.pack(side="left", padx=(10, 0))
        
        SignatureLine(log_card, width=100).pack(anchor="w", padx=16, pady=(0, 8))
        
        # Log text
        self.log_text = ctk.CTkTextbox(
            log_card,
            font=FONTS["small"],
            fg_color=COLORS["bg_elevated"],
            text_color=COLORS["text_secondary"],
            corner_radius=8,
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.log_text.insert("1.0", "// No disposals yet\n// Select an item and click DISPOSE")
        self.log_text.configure(state="disabled")
    
    def _dispose_item(self):
        """Handle disposal"""
        item_name = self.selected_item.get()
        if not item_name:
            return
        
        # Find item
        item = next((i for i in DISPOSABLES if i["name"] == item_name), None)
        if not item:
            return
        
        # Find target container
        if item["dangerous"]:
            category = item["category"]
            container_map = {
                "glass": "GLASS",
                "microbio": "MICROBIO",
                "aluminium": "ALUMINIUM",
                "metals": "METALS",
                "sharps": "SHARPS",
            }
            container_key = container_map.get(category)
        else:
            container_key = "NON-DANGEROUS"
        
        if not container_key or container_key not in self.containers:
            return
        
        # Update container fill
        container = self.containers[container_key]
        fill_amount = 50  # Each item adds 50 units
        
        if container["current_fill"] + fill_amount <= container["capacity"]:
            container["current_fill"] += fill_amount
            
            # Log entry
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = {
                "time": timestamp,
                "item": item_name,
                "dangerous": item["dangerous"],
                "container": container["id"],
            }
            self.disposal_log.insert(0, log_entry)
            
            # Update UI
            self._refresh_containers()
            self._refresh_log()
            
            # Show popup
            self._show_disposal_popup(item, container)
        else:
            # Container full
            self._show_error_popup(f"Container {container['id']} is full!")
        
        # Reset dropdown to first item
        item_names = [item["name"] for item in DISPOSABLES]
        self.selected_item.set(item_names[0])
    
    def _refresh_containers(self):
        """Refresh container displays"""
        # Destroy old widgets
        for key, widget in self.container_widgets.items():
            widget.destroy()
        
        self.container_widgets = {}
        
        # Recreate non-dangerous
        self.container_widgets["NON-DANGEROUS"] = CompactContainerCard(
            self.nondanger_container_frame, self.containers["NON-DANGEROUS"]
        )
        self.container_widgets["NON-DANGEROUS"].pack(fill="x")
        
        # Clear and recreate dangerous
        for child in self.danger_frame.winfo_children():
            child.destroy()
        
        danger_containers = ["GLASS", "MICROBIO", "ALUMINIUM", "METALS", "SHARPS"]
        row_frame = None
        
        for i, key in enumerate(danger_containers):
            col = i % 3
            
            if col == 0:
                row_frame = ctk.CTkFrame(self.danger_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
            
            widget = CompactContainerCard(row_frame, self.containers[key])
            widget.pack(side="left", fill="x", expand=True, padx=(0 if col == 0 else 4, 0))
            self.container_widgets[key] = widget
    
    def _refresh_log(self):
        """Refresh disposal log"""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        
        if not self.disposal_log:
            self.log_text.insert("1.0", "// No disposals yet\n// Select an item and click DISPOSE")
        else:
            for entry in self.disposal_log[:20]:  # Show last 20
                danger_tag = "⚠" if entry["dangerous"] else "✓"
                line = f"[{entry['time']}] {danger_tag} {entry['item']} → {entry['container']}\n"
                self.log_text.insert("end", line)
        
        self.log_text.configure(state="disabled")
        self.log_count_label.configure(text=f"[{len(self.disposal_log)} entries]")
    
    def _show_disposal_popup(self, item, container):
        """Show disposal confirmation popup"""
        popup = ctk.CTkToplevel(self)
        popup.title("Disposal Confirmed")
        popup.geometry("350x280")
        popup.configure(fg_color=COLORS["bg_pure"])
        popup.transient(self)
        popup.grab_set()
        
        # Center
        popup.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 175
        y = self.winfo_y() + (self.winfo_height() // 2) - 140
        popup.geometry(f"+{x}+{y}")
        
        # Content
        card = GlassCard(popup, highlight=True)
        card.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 8))
        
        ctk.CTkLabel(
            header,
            text="✓",
            font=(_FONT, 24, "bold"),
            text_color=COLORS["status_success"]
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            header,
            text="DISPOSED",
            font=FONTS["subheading"],
            text_color=COLORS["accent_primary"]
        ).pack(side="left")
        
        SignatureLine(card, width=80).pack(anchor="w", padx=16, pady=(0, 12))
        
        # Info
        info_frame = ctk.CTkFrame(card, fg_color=COLORS["bg_elevated"], corner_radius=8)
        info_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        for label, value in [
            ("ITEM", item["name"]),
            ("TYPE", "⚠ DANGEROUS" if item["dangerous"] else "✓ SAFE"),
            ("CONTAINER", container["id"]),
            ("FILL", f"{container['current_fill']}/{container['capacity']}"),
        ]:
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=6)
            ctk.CTkLabel(row, text=label, font=FONTS["tiny"],
                text_color=COLORS["text_muted"], width=80, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=value, font=FONTS["small"],
                text_color=COLORS["text_main"], anchor="w").pack(side="left")
        
        # Close button
        ctk.CTkButton(
            card,
            text="CLOSE",
            font=FONTS["button"],
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            corner_radius=8,
            height=36,
            command=popup.destroy
        ).pack(fill="x", padx=16, pady=(0, 16))
    
    def _show_error_popup(self, message):
        """Show error popup"""
        popup = ctk.CTkToplevel(self)
        popup.title("Error")
        popup.geometry("300x150")
        popup.configure(fg_color=COLORS["bg_pure"])
        popup.transient(self)
        popup.grab_set()
        
        popup.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 150
        y = self.winfo_y() + (self.winfo_height() // 2) - 75
        popup.geometry(f"+{x}+{y}")
        
        card = GlassCard(popup)
        card.pack(fill="both", expand=True, padx=16, pady=16)
        
        ctk.CTkLabel(
            card,
            text="⚠ ERROR",
            font=FONTS["subheading"],
            text_color=COLORS["alert_error"]
        ).pack(pady=(16, 8))
        
        ctk.CTkLabel(
            card,
            text=message,
            font=FONTS["small"],
            text_color=COLORS["text_main"]
        ).pack(pady=(0, 12))
        
        ctk.CTkButton(
            card,
            text="OK",
            font=FONTS["button"],
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            corner_radius=8,
            width=80,
            command=popup.destroy
        ).pack(pady=(0, 16))


# ============================================
# MAIN
# ============================================

def main():
    print()
    print("  INTELLIBIN v2.0 - Starting...")
    print()
    
    app = IntelliBinSimulator()
    app.mainloop()


if __name__ == "__main__":
    main()
