"""
Routing Service for IntelliBin.
Main orchestration service that routes substances to appropriate containers.
"""

from typing import Optional, Tuple
from datetime import datetime

from .state import state_manager
from .classification import classification_service
from .compatibility import compatibility_service
from ..models.responses import (
    RouteRequest, RouteResponse, RiskLevel,
    ClassificationResult, RoutedContainer, DisposalResponse
)


class RoutingService:
    """
    Routes substances to appropriate containers.
    This is the main orchestration service that brings together
    classification, compatibility checking, and container management.
    """
    
    def __init__(self):
        self.state = state_manager
        self.classifier = classification_service
        self.compatibility = compatibility_service
    
    def route(self, request: RouteRequest) -> RouteResponse:
        """
        Main routing method.
        Takes a substance and finds the appropriate container.
        
        Process:
        1. Classify the substance
        2. Determine target waste stream
        3. Find compatible container with capacity
        4. Return routing instructions or error
        """
        # Step 1: Classify the substance
        substance = self.classifier.classify(request.substance)
        
        if not substance:
            return RouteResponse(
                success=False,
                substance=request.substance,
                classified_as=ClassificationResult(
                    category="Unknown",
                    waste_stream="Unknown"
                ),
                routed_to=None,
                safety_status=RiskLevel.DANGER,
                message=f"Unknown substance: '{request.substance}'. Please verify the chemical name or contact your supervisor.",
                warnings=["Substance not found in database"]
            )
        
        # Step 2: Get target waste stream and category
        waste_stream = self.classifier.get_waste_stream(substance)
        category = self.classifier.get_category(substance)
        
        # Step 3: Find compatible container
        container, compatibility_issue = self._find_best_container(
            substance, 
            waste_stream, 
            request.quantity_ml
        )
        
        if not container:
            return RouteResponse(
                success=False,
                substance=request.substance,
                classified_as=ClassificationResult(
                    category=category,
                    waste_stream=waste_stream
                ),
                routed_to=None,
                safety_status=RiskLevel.DANGER,
                message=self._build_no_container_message(waste_stream, compatibility_issue),
                warnings=self._build_warnings(None, compatibility_issue)
            )
        
        # Step 4: Build successful response
        return self._build_success_response(
            request, substance, container, category, waste_stream
        )
    
    def _find_best_container(self, substance: dict, waste_stream: str, 
                             quantity_ml: float) -> Tuple[Optional[dict], Optional[dict]]:
        """
        Find the best container for a substance.
        
        Selection criteria:
        1. Correct waste stream
        2. Has capacity for the quantity
        3. Compatible with existing contents
        4. Prefer containers with more available space
        
        Returns:
            Tuple of (container, compatibility_issue)
        """
        containers = self.state.get_containers_by_stream(waste_stream)
        compatibility_issue = None
        
        # Sort by fill level (prefer less full containers)
        containers.sort(key=lambda c: c["current_fill_ml"])
        
        for container in containers:
            # Check capacity
            if container["current_fill_ml"] + quantity_ml > container["capacity_ml"]:
                continue
            
            # Check compatibility
            is_compatible, issue = self.compatibility.check_compatibility(
                substance, container
            )
            
            if is_compatible:
                return container, None
            else:
                # Save the issue for error reporting
                if compatibility_issue is None:
                    compatibility_issue = issue
        
        return None, compatibility_issue
    
    def _build_success_response(self, request: RouteRequest, substance: dict,
                                container: dict, category: str, 
                                waste_stream: str) -> RouteResponse:
        """Build a successful routing response"""
        
        fill_before = container["current_fill_ml"]
        fill_after = fill_before + request.quantity_ml
        capacity = container["capacity_ml"]
        fill_percent_before = (fill_before / capacity) * 100
        fill_percent_after = (fill_after / capacity) * 100
        
        # Calculate days until deadline
        days_until = None
        if container.get("pickup_deadline"):
            try:
                deadline = datetime.fromisoformat(
                    container["pickup_deadline"].replace("Z", "")
                )
                days_until = (deadline - self.state.simulated_time).days
            except (ValueError, TypeError):
                pass
        
        # Determine safety status and warnings
        warnings = []
        safety_status = RiskLevel.SAFE
        
        if fill_percent_after > 90:
            warnings.append(f"Container will be at {fill_percent_after:.0f}% capacity - nearly full")
            safety_status = RiskLevel.CAUTION
        elif fill_percent_after > 75:
            warnings.append(f"Container will be at {fill_percent_after:.0f}% capacity")
        
        if days_until is not None and days_until < 14:
            warnings.append(f"Pickup deadline in {days_until} days")
            if safety_status == RiskLevel.SAFE:
                safety_status = RiskLevel.CAUTION
        
        # Check for flammability warnings
        if substance.get("properties", {}).get("flammable"):
            warnings.append("Flammable substance - ensure proper storage")
        
        # Check for toxicity warnings  
        toxicity = substance.get("properties", {}).get("toxicity", "Low")
        if toxicity == "High":
            warnings.append("High toxicity - handle with appropriate PPE")
        
        return RouteResponse(
            success=True,
            substance=request.substance,
            classified_as=ClassificationResult(
                category=category,
                waste_stream=waste_stream
            ),
            routed_to=RoutedContainer(
                container_id=container["container_id"],
                location=container["location"],
                current_fill_percent=round(fill_percent_before, 1),
                after_fill_percent=round(fill_percent_after, 1),
                days_until_deadline=days_until
            ),
            safety_status=safety_status,
            message=f"Route to {container['container_id']} at {container['location']}. Safe to dispose.",
            warnings=warnings
        )
    
    def _build_no_container_message(self, waste_stream: str, 
                                    compatibility_issue: Optional[dict]) -> str:
        """Build error message when no container available"""
        if compatibility_issue:
            rule = compatibility_issue.get("rule", {})
            hazard = rule.get("hazard_type", "Incompatibility")
            explanation = rule.get("explanation", "Chemical incompatibility detected.")
            conflicting = compatibility_issue.get("conflicting_substance", "existing contents")
            return (
                f"Cannot route: {hazard}. "
                f"Incompatible with {conflicting} in available containers. "
                f"{explanation}"
            )
        
        return (
            f"No container available for {waste_stream} waste stream. "
            f"All containers are either full or at capacity. "
            f"Please request a new container or schedule pickup for existing ones."
        )
    
    def _build_warnings(self, container: Optional[dict], 
                        compatibility_issue: Optional[dict]) -> list[str]:
        """Build list of warnings"""
        warnings = []
        
        if compatibility_issue:
            conflicting = compatibility_issue.get("conflicting_substance", "existing contents")
            warnings.append(f"Incompatible with {conflicting}")
            
            rule = compatibility_issue.get("rule", {})
            hazard = rule.get("hazard_type")
            if hazard:
                warnings.append(f"Hazard: {hazard}")
        
        if not container:
            warnings.append("No suitable container found")
        
        return warnings
    
    def dispose(self, container_id: str, substance_name: str,
                quantity_ml: float, concentration: str) -> DisposalResponse:
        """
        Confirm and log a disposal.
        Should be called after route() returns success.
        """
        # Verify container exists
        container = self.state.get_container(container_id)
        if not container:
            raise ValueError(f"Container not found: {container_id}")
        
        # Classify substance
        substance = self.classifier.classify(substance_name)
        if not substance:
            raise ValueError(f"Unknown substance: {substance_name}")
        
        # Verify capacity
        new_fill = container["current_fill_ml"] + quantity_ml
        if new_fill > container["capacity_ml"]:
            raise ValueError("Disposal would exceed container capacity")
        
        # Update state
        updated = self.state.update_container(
            container_id=container_id,
            substance_name=substance["name"],
            category=substance["category"],
            quantity_ml=quantity_ml,
            concentration=concentration
        )
        
        fill_percent = (updated["current_fill_ml"] / updated["capacity_ml"]) * 100
        
        # Check if we need to create capacity alert
        if fill_percent >= 90:
            severity = "Danger" if fill_percent >= 95 else "Caution"
            self.state.add_alert(
                container_id=container_id,
                alert_type="Capacity",
                severity=severity,
                title="Container nearly full",
                message=f"Container {container_id} is at {fill_percent:.0f}% capacity. Schedule pickup soon."
            )
        
        return DisposalResponse(
            success=True,
            container_id=container_id,
            new_fill_ml=updated["current_fill_ml"],
            fill_percent=round(fill_percent, 1),
            logged_at=self.state.simulated_time.isoformat() + "Z"
        )


# Singleton instance
routing_service = RoutingService()
