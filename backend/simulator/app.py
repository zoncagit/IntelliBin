"""
IntelliBin Simulator - Clean Desktop UI
A modern interface for the waste routing simulation.
"""

import customtkinter as ctk
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services import state_manager, routing_service, classification_service
from app.models.responses import RouteRequest, RiskLevel


# ============================================
# THEME CONFIGURATION
# ============================================

COLORS = {
    "bg_primary": "#F5F5F7",
    "bg_secondary": "#FFFFFF",
    "bg_tertiary": "#E8E8ED",
    "text_primary": "#1D1D1F",
    "text_secondary": "#86868B",
    "text_tertiary": "#6E6E73",
    "accent_blue": "#007AFF",
    "accent_green": "#34C759",
    "accent_yellow": "#FF9500",
    "accent_red": "#FF3B30",
    "border": "#D2D2D7",
}

FONTS = {
    "logo": ("JetBrains Mono", 32, "bold"),
    "heading": ("JetBrains Mono", 20, "bold"),
    "subheading": ("JetBrains Mono", 16, "bold"),
    "body": ("JetBrains Mono", 14),
    "body_bold": ("JetBrains Mono", 14, "bold"),
    "small": ("JetBrains Mono", 12),
    "tiny": ("JetBrains Mono", 10),
    "mono": ("monospace", 12),
}

# Predefined substances list
SUBSTANCES_LIST = [
    "Hydrochloric Acid (dilute)",
    "Hydrochloric Acid (concentrated)",
    "Sulfuric Acid (dilute)",
    "Nitric Acid",
    "Sodium Hydroxide",
    "Potassium Hydroxide",
    "Ammonia Solution",
    "Sodium Metal",
    "Potassium Metal",
    "Lithium Metal",
    "Acetone",
    "Ethanol",
    "Methanol",
    "Isopropanol",
    "Hexane",
    "Toluene",
    "Chloroform",
    "Dichloromethane",
    "Carbon Tetrachloride",
    "Hydrogen Peroxide (30%)",
    "Potassium Permanganate",
    "Sodium Hypochlorite",
    "Mercury Solution",
    "Lead Solution",
    "Cadmium Solution",
]

QUANTITY_OPTIONS = ["50", "100", "150", "200", "250", "300", "400", "500"]


# ============================================
# CUSTOM WIDGETS
# ============================================

class Card(ctk.CTkFrame):
    """A card-style container"""
    
    def __init__(self, master, fg_color=None, **kwargs):
        color = fg_color if fg_color is not None else COLORS["bg_secondary"]
        super().__init__(
            master,
            fg_color=color,
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs
        )


class ContainerCard(Card):
    """A card displaying container status"""
    
    def __init__(self, master, container: dict, **kwargs):
        super().__init__(master, **kwargs)
        self.container = container
        self._create_widgets()
    
    def _create_widgets(self):
        # Container ID
        id_label = ctk.CTkLabel(
            self,
            text=self.container["container_id"],
            font=FONTS["subheading"],
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        id_label.pack(fill="x", padx=16, pady=(16, 4))
        
        # Waste stream
        stream_label = ctk.CTkLabel(
            self,
            text=self.container["waste_stream"],
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        stream_label.pack(fill="x", padx=16, pady=(0, 8))
        
        # Fill level progress bar
        fill_percent = (self.container["current_fill_ml"] / self.container["capacity_ml"]) * 100
        
        # Determine color based on fill level
        if fill_percent >= 90:
            progress_color = COLORS["accent_red"]
        elif fill_percent >= 70:
            progress_color = COLORS["accent_yellow"]
        else:
            progress_color = COLORS["accent_green"]
        
        self.progress = ctk.CTkProgressBar(
            self,
            progress_color=progress_color,
            fg_color=COLORS["bg_tertiary"],
            height=8,
            corner_radius=4
        )
        self.progress.set(fill_percent / 100)
        self.progress.pack(fill="x", padx=16, pady=(0, 4))
        
        # Fill level text
        fill_text = f"{fill_percent:.0f}% ({self.container['current_fill_ml']:.0f}/{self.container['capacity_ml']:.0f} mL)"
        fill_label = ctk.CTkLabel(
            self,
            text=fill_text,
            font=FONTS["tiny"],
            text_color=COLORS["text_tertiary"],
            anchor="w"
        )
        fill_label.pack(fill="x", padx=16, pady=(0, 8))
        
        # Location
        loc_label = ctk.CTkLabel(
            self,
            text=self.container['location'],
            font=FONTS["tiny"],
            text_color=COLORS["text_tertiary"],
            anchor="w"
        )
        loc_label.pack(fill="x", padx=16, pady=(0, 16))
    
    def update_container(self, container: dict):
        """Update the container display"""
        self.container = container
        for widget in self.winfo_children():
            widget.destroy()
        self._create_widgets()


# ============================================
# 3D MODEL DISPLAY (Canvas Placeholder)
# ============================================

class Model3DView(ctk.CTkFrame):
    """A frame to display 3D model information"""
    
    def __init__(self, master, model_path: str = None, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_tertiary"], corner_radius=12, **kwargs)
        self.model_path = model_path
        self._create_widgets()
    
    def _create_widgets(self):
        # Title
        title = ctk.CTkLabel(
            self,
            text="IntelliBin 3D Model",
            font=FONTS["subheading"],
            text_color=COLORS["text_primary"]
        )
        title.pack(pady=(20, 10))
        
        # Canvas for visual representation
        self.canvas = ctk.CTkCanvas(
            self,
            width=200,
            height=200,
            bg=COLORS["bg_tertiary"],
            highlightthickness=0
        )
        self.canvas.pack(pady=10)
        
        # Draw a stylized bin representation
        self._draw_bin()
        
        # Model info
        if self.model_path and Path(self.model_path).exists():
            file_size = Path(self.model_path).stat().st_size / 1024
            info_text = f"Model: intelligent+bin+3d+model.glb\nSize: {file_size:.1f} KB"
        else:
            info_text = "3D Model Preview"
        
        info_label = ctk.CTkLabel(
            self,
            text=info_text,
            font=FONTS["tiny"],
            text_color=COLORS["text_secondary"]
        )
        info_label.pack(pady=(5, 20))
    
    def _draw_bin(self):
        """Draw a stylized bin representation"""
        cx, cy = 100, 100
        
        # Bin body (trapezoid)
        self.canvas.create_polygon(
            60, 50,    # top left
            140, 50,   # top right
            150, 170,  # bottom right
            50, 170,   # bottom left
            fill=COLORS["accent_blue"],
            outline=COLORS["text_primary"],
            width=2
        )
        
        # Bin lid
        self.canvas.create_rectangle(
            55, 40, 145, 55,
            fill=COLORS["bg_secondary"],
            outline=COLORS["text_primary"],
            width=2
        )
        
        # Bin label
        self.canvas.create_text(
            cx, 110,
            text="WASTE",
            font=("JetBrains Mono", 12, "bold"),
            fill="white"
        )
        
        # Hazard symbol (simplified)
        self.canvas.create_polygon(
            100, 130,
            85, 155,
            115, 155,
            fill=COLORS["accent_yellow"],
            outline=COLORS["text_primary"],
            width=1
        )
        self.canvas.create_text(
            100, 145,
            text="!",
            font=("JetBrains Mono", 14, "bold"),
            fill=COLORS["text_primary"]
        )


# ============================================
# MAIN APPLICATION
# ============================================

class IntelliBinSimulator(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("IntelliBin Simulator")
        self.geometry("1400x850")
        self.minsize(1200, 700)
        
        # Set appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.configure(fg_color=COLORS["bg_primary"])
        
        # GLB model path
        self.model_path = Path(__file__).parent.parent.parent / "intelligent+bin+3d+model.glb"
        
        # Create layout
        self._create_layout()
        
        # Load initial data
        self._refresh_containers()
        self._refresh_log()
        self._refresh_alerts()
    
    def _create_layout(self):
        """Create the main application layout"""
        
        # Header
        self._create_header()
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        
        # Configure grid - 3 columns
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_columnconfigure(2, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Create columns
        self._create_input_column()
        self._create_containers_column()
        self._create_info_column()
    
    def _create_header(self):
        """Create the application header"""
        header = ctk.CTkFrame(self, fg_color="transparent", height=80)
        header.pack(fill="x", padx=24, pady=(24, 16))
        header.pack_propagate(False)
        
        # Logo
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="y")
        
        logo = ctk.CTkLabel(
            title_frame,
            text="INTELLIBIN",
            font=FONTS["logo"],
            text_color=COLORS["text_primary"]
        )
        logo.pack(side="left", pady=16)
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="  Laboratory Waste Routing Simulator",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        subtitle.pack(side="left", pady=16, padx=(8, 0))
        
        # Controls
        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.pack(side="right", fill="y")
        
        # Time display
        self.time_label = ctk.CTkLabel(
            controls,
            text=f"Date: {state_manager.simulated_time.strftime('%Y-%m-%d')}",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        self.time_label.pack(side="left", padx=(0, 16), pady=24)
        
        # Advance time button
        advance_btn = ctk.CTkButton(
            controls,
            text="+7 Days",
            font=FONTS["small"],
            fg_color=COLORS["bg_tertiary"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["border"],
            corner_radius=8,
            width=80,
            height=32,
            command=self._advance_time
        )
        advance_btn.pack(side="left", padx=(0, 8), pady=24)
        
        # Reset button
        reset_btn = ctk.CTkButton(
            controls,
            text="Reset",
            font=FONTS["small"],
            fg_color=COLORS["bg_tertiary"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["border"],
            corner_radius=8,
            width=70,
            height=32,
            command=self._reset_simulation
        )
        reset_btn.pack(side="left", pady=24)
    
    def _create_input_column(self):
        """Create the left column with input form"""
        column = Card(self.main_frame)
        column.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=0)
        
        # Title
        title = ctk.CTkLabel(
            column,
            text="Dispose Waste",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        title.pack(fill="x", padx=20, pady=(20, 4))
        
        subtitle = ctk.CTkLabel(
            column,
            text="Select substance and quantity",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        subtitle.pack(fill="x", padx=20, pady=(0, 20))
        
        # Substance dropdown
        sub_label = ctk.CTkLabel(
            column,
            text="Substance",
            font=FONTS["body_bold"],
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        sub_label.pack(fill="x", padx=20, pady=(0, 4))
        
        self.substance_var = ctk.StringVar(value=SUBSTANCES_LIST[0])
        self.substance_dropdown = ctk.CTkComboBox(
            column,
            values=SUBSTANCES_LIST,
            variable=self.substance_var,
            font=FONTS["body"],
            height=40,
            corner_radius=8,
            border_color=COLORS["border"],
            fg_color=COLORS["bg_primary"],
            button_color=COLORS["accent_blue"],
            dropdown_font=FONTS["small"],
            state="readonly"
        )
        self.substance_dropdown.pack(fill="x", padx=20, pady=(0, 16))
        
        # Quantity dropdown
        qty_label = ctk.CTkLabel(
            column,
            text="Quantity (mL)",
            font=FONTS["body_bold"],
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        qty_label.pack(fill="x", padx=20, pady=(0, 4))
        
        self.quantity_var = ctk.StringVar(value="100")
        self.quantity_dropdown = ctk.CTkComboBox(
            column,
            values=QUANTITY_OPTIONS,
            variable=self.quantity_var,
            font=FONTS["body"],
            height=40,
            corner_radius=8,
            border_color=COLORS["border"],
            fg_color=COLORS["bg_primary"],
            button_color=COLORS["accent_blue"],
            dropdown_font=FONTS["small"],
            state="readonly"
        )
        self.quantity_dropdown.pack(fill="x", padx=20, pady=(0, 24))
        
        # Route button
        self.route_btn = ctk.CTkButton(
            column,
            text="Check Routing",
            font=FONTS["body_bold"],
            fg_color=COLORS["accent_blue"],
            hover_color="#0056b3",
            corner_radius=8,
            height=44,
            command=self._route_substance
        )
        self.route_btn.pack(fill="x", padx=20, pady=(0, 16))
        
        # Result display
        self.result_frame = Card(column, fg_color=COLORS["bg_primary"])
        self.result_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.result_text = ctk.CTkTextbox(
            self.result_frame,
            font=FONTS["small"],
            fg_color="transparent",
            text_color=COLORS["text_primary"],
            wrap="word",
            height=150
        )
        self.result_text.pack(fill="both", expand=True, padx=12, pady=12)
        self.result_text.insert("1.0", "Select a substance and click 'Check Routing' to see the result.")
        self.result_text.configure(state="disabled")
        
        # Confirm disposal button
        self.confirm_btn = ctk.CTkButton(
            column,
            text="Confirm Disposal",
            font=FONTS["body_bold"],
            fg_color=COLORS["accent_green"],
            hover_color="#2da44e",
            corner_radius=8,
            height=44,
            command=self._confirm_disposal
        )
        
        self.current_route_result = None
    
    def _create_containers_column(self):
        """Create the middle column with container status"""
        column = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        column.grid(row=0, column=1, sticky="nsew", padx=12, pady=0)
        
        # Title
        title_frame = ctk.CTkFrame(column, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 12))
        
        title = ctk.CTkLabel(
            title_frame,
            text="Container Status",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        title.pack(side="left")
        
        # Container grid
        self.containers_frame = ctk.CTkFrame(column, fg_color="transparent")
        self.containers_frame.pack(fill="both", expand=True)
        
        # Configure 2x3 grid
        for i in range(3):
            self.containers_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            self.containers_frame.grid_rowconfigure(i, weight=1)
        
        self.container_cards = {}
    
    def _create_info_column(self):
        """Create the right column with 3D model and log"""
        column = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        column.grid(row=0, column=2, sticky="nsew", padx=(12, 0), pady=0)
        
        # 3D Model view
        model_card = Card(column)
        model_card.pack(fill="x", pady=(0, 12))
        
        self.model_view = Model3DView(model_card, model_path=str(self.model_path))
        self.model_view.pack(fill="x", padx=12, pady=12)
        
        # Alerts section
        alerts_card = Card(column)
        alerts_card.pack(fill="x", pady=(0, 12))
        
        alerts_title = ctk.CTkLabel(
            alerts_card,
            text="Alerts",
            font=FONTS["subheading"],
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        alerts_title.pack(fill="x", padx=16, pady=(16, 8))
        
        self.alerts_frame = ctk.CTkFrame(alerts_card, fg_color="transparent")
        self.alerts_frame.pack(fill="x", padx=16, pady=(0, 16))
        
        # Log section
        log_card = Card(column)
        log_card.pack(fill="both", expand=True)
        
        log_title = ctk.CTkLabel(
            log_card,
            text="Disposal Log",
            font=FONTS["subheading"],
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        log_title.pack(fill="x", padx=16, pady=(16, 8))
        
        self.log_text = ctk.CTkTextbox(
            log_card,
            font=FONTS["tiny"],
            fg_color=COLORS["bg_primary"],
            text_color=COLORS["text_primary"],
            corner_radius=8,
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=16, pady=(0, 16))
    
    def _refresh_containers(self):
        """Refresh the container display"""
        # Clear existing cards
        for widget in self.containers_frame.winfo_children():
            widget.destroy()
        self.container_cards.clear()
        
        # Get containers (limited to 6)
        containers = state_manager.get_all_containers()[:6]
        
        # Create cards in 2x3 grid
        for i, container in enumerate(containers):
            row = i // 3
            col = i % 3
            
            card = ContainerCard(self.containers_frame, container)
            card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
            self.container_cards[container["container_id"]] = card
    
    def _refresh_log(self):
        """Refresh the disposal log"""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        
        log_entries = state_manager.get_disposal_log(limit=15)
        
        if not log_entries:
            self.log_text.insert("1.0", "No disposals yet.")
        else:
            for entry in log_entries:
                timestamp = entry["timestamp"][:10]
                text = f"[{timestamp}]\n"
                text += f"  {entry['substance']}\n"
                text += f"  -> {entry['container_id']} ({entry['quantity_ml']}mL)\n\n"
                self.log_text.insert("end", text)
        
        self.log_text.configure(state="disabled")
    
    def _refresh_alerts(self):
        """Refresh the alerts display"""
        for widget in self.alerts_frame.winfo_children():
            widget.destroy()
        
        alerts = state_manager.get_alerts(include_acknowledged=False)
        
        if not alerts:
            no_alerts = ctk.CTkLabel(
                self.alerts_frame,
                text="No active alerts",
                font=FONTS["small"],
                text_color=COLORS["text_secondary"]
            )
            no_alerts.pack(anchor="w")
        else:
            for alert in alerts[:5]:
                severity = alert["severity"].lower()
                color = {
                    "danger": COLORS["accent_red"],
                    "caution": COLORS["accent_yellow"],
                }.get(severity, COLORS["text_secondary"])
                
                alert_frame = ctk.CTkFrame(self.alerts_frame, fg_color="transparent")
                alert_frame.pack(fill="x", pady=2)
                
                dot = ctk.CTkLabel(
                    alert_frame,
                    text="*",
                    font=FONTS["body_bold"],
                    text_color=color
                )
                dot.pack(side="left", padx=(0, 8))
                
                text = ctk.CTkLabel(
                    alert_frame,
                    text=alert['title'],
                    font=FONTS["tiny"],
                    text_color=COLORS["text_primary"],
                    anchor="w"
                )
                text.pack(side="left", fill="x", expand=True)
    
    def _route_substance(self):
        """Handle the route button click"""
        substance = self.substance_var.get()
        quantity_str = self.quantity_var.get()
        
        try:
            quantity = float(quantity_str)
        except ValueError:
            self._show_result("Please select a valid quantity.")
            return
        
        # Create request and route
        request = RouteRequest(
            substance=substance,
            quantity_ml=quantity,
            concentration="Standard"
        )
        
        result = routing_service.route(request)
        self.current_route_result = result
        
        # Build result text
        text = f"Substance: {result.substance}\n"
        text += f"Category: {result.classified_as.category}\n"
        text += f"Waste Stream: {result.classified_as.waste_stream}\n\n"
        
        if result.success:
            routed = result.routed_to
            text += f"ROUTE TO: {routed.container_id}\n"
            text += f"Location: {routed.location}\n"
            text += f"Fill: {routed.current_fill_percent:.0f}% -> {routed.after_fill_percent:.0f}%\n"
            
            if result.warnings:
                text += f"\nWarnings:\n"
                for warning in result.warnings:
                    text += f"  - {warning}\n"
            
            # Show confirm button
            self.confirm_btn.pack(fill="x", padx=20, pady=(0, 20))
        else:
            text += f"ERROR: {result.message}\n"
            self.confirm_btn.pack_forget()
        
        self._show_result(text)
    
    def _show_result(self, text: str):
        """Show result text"""
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.configure(state="disabled")
    
    def _confirm_disposal(self):
        """Handle the confirm disposal button click"""
        if not self.current_route_result or not self.current_route_result.success:
            return
        
        result = self.current_route_result
        quantity = float(self.quantity_var.get())
        
        try:
            disposal = routing_service.dispose(
                container_id=result.routed_to.container_id,
                substance_name=result.substance,
                quantity_ml=quantity,
                concentration="Standard"
            )
            
            # Update UI
            self._show_result(
                f"Disposal confirmed!\n\n"
                f"Container: {disposal.container_id}\n"
                f"New fill level: {disposal.fill_percent:.0f}%\n"
                f"Logged at: {disposal.logged_at[:16].replace('T', ' ')}"
            )
            
            # Hide confirm button
            self.confirm_btn.pack_forget()
            self.current_route_result = None
            
            # Refresh displays
            self._refresh_containers()
            self._refresh_log()
            self._refresh_alerts()
            
        except Exception as e:
            self._show_result(f"Error: {str(e)}")
    
    def _advance_time(self):
        """Advance simulated time by 7 days"""
        new_alerts = state_manager.advance_time(7)
        self.time_label.configure(
            text=f"Date: {state_manager.simulated_time.strftime('%Y-%m-%d')}"
        )
        self._refresh_alerts()
        self._refresh_containers()
        
        if new_alerts > 0:
            self._show_result(f"Time advanced by 7 days\n{new_alerts} new alert(s) generated.")
        else:
            self._show_result("Time advanced by 7 days.")
    
    def _reset_simulation(self):
        """Reset the simulation to initial state"""
        state_manager.reset()
        self.time_label.configure(
            text=f"Date: {state_manager.simulated_time.strftime('%Y-%m-%d')}"
        )
        self._refresh_containers()
        self._refresh_log()
        self._refresh_alerts()
        
        self.confirm_btn.pack_forget()
        self.current_route_result = None
        
        self._show_result("Simulation reset to initial state.")


# ============================================
# MAIN ENTRY POINT
# ============================================

def main():
    """Run the IntelliBin Simulator"""
    print("=" * 50)
    print("  INTELLIBIN Simulator")
    print("  Laboratory Waste Routing System")
    print("=" * 50)
    print()
    
    app = IntelliBinSimulator()
    app.mainloop()


if __name__ == "__main__":
    main()
