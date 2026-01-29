"""
Compatibility Service for IntelliBin.
Checks chemical compatibility and identifies hazardous combinations.
"""

from typing import Optional, Tuple
from .state import state_manager


class CompatibilityService:
    """
    Checks compatibility between substances and container contents.
    Uses rule-based logic derived from chemical safety data.
    """
    
    def __init__(self):
        self.state = state_manager
    
    def check_compatibility(self, substance: dict, container: dict) -> Tuple[bool, Optional[dict]]:
        """
        Check if a substance is compatible with container contents.
        
        Args:
            substance: The substance to be disposed
            container: The target container
            
        Returns:
            Tuple of (is_compatible, incompatibility_info)
            - is_compatible: True if safe to add
            - incompatibility_info: Dict with details if incompatible, None otherwise
        """
        substance_category = substance.get("category", "Unknown")
        incompatible_categories = substance.get("incompatible_with", [])
        
        # Check against each item in container
        for content in container.get("contents", []):
            content_category = content.get("category", "Unknown")
            
            # Check if new substance is incompatible with existing content
            if content_category in incompatible_categories:
                rule = self._get_rule(substance_category, content_category)
                return False, {
                    "new_substance": substance["name"],
                    "new_category": substance_category,
                    "conflicting_substance": content["substance"],
                    "conflicting_category": content_category,
                    "rule": rule
                }
            
            # Check reverse - if existing content is incompatible with new substance
            # (Some incompatibilities are bidirectional)
            existing_substance = self._find_substance_by_name(content["substance"])
            if existing_substance:
                existing_incompatible = existing_substance.get("incompatible_with", [])
                if substance_category in existing_incompatible:
                    rule = self._get_rule(content_category, substance_category)
                    return False, {
                        "new_substance": substance["name"],
                        "new_category": substance_category,
                        "conflicting_substance": content["substance"],
                        "conflicting_category": content_category,
                        "rule": rule
                    }
        
        return True, None
    
    def _get_rule(self, category1: str, category2: str) -> dict:
        """Get the incompatibility rule for two categories"""
        rules = self.state.rules.get("incompatibility_rules", [])
        
        for rule in rules:
            pair = rule.get("category_pair", [])
            if category1 in pair and category2 in pair:
                return rule
        
        # Return default rule if no specific rule found
        return {
            "risk_level": "Danger",
            "hazard_type": "Chemical Incompatibility",
            "explanation": f"{category1} and {category2} are chemically incompatible and should not be mixed."
        }
    
    def _find_substance_by_name(self, name: str) -> Optional[dict]:
        """Find substance profile by name"""
        name_lower = name.lower()
        for substance in self.state.substances.values():
            if substance["name"].lower() == name_lower:
                return substance
            for alias in substance.get("aliases", []):
                if alias.lower() == name_lower:
                    return substance
        return None
    
    def _find_substance_by_category(self, category: str) -> Optional[dict]:
        """Find any substance with the given category (for rule lookup)"""
        for substance in self.state.substances.values():
            if substance.get("category") == category:
                return substance
        return None
    
    def get_compatible_streams(self, substance: dict) -> list[str]:
        """Get list of waste streams that could accept this substance"""
        category = substance.get("category", "Unknown")
        compatible = []
        
        stream_rules = self.state.rules.get("waste_stream_rules", {})
        
        for stream_name, stream_rule in stream_rules.items():
            accepted = stream_rule.get("accepts_categories", [])
            if category in accepted:
                compatible.append(stream_name)
        
        return compatible
    
    def get_all_incompatibility_rules(self) -> list[dict]:
        """Get all incompatibility rules"""
        return self.state.rules.get("incompatibility_rules", [])
    
    def check_category_pair(self, cat1: str, cat2: str) -> Optional[dict]:
        """Check if two categories are incompatible"""
        rules = self.state.rules.get("incompatibility_rules", [])
        
        for rule in rules:
            pair = rule.get("category_pair", [])
            if cat1 in pair and cat2 in pair:
                return rule
        
        return None


# Singleton instance
compatibility_service = CompatibilityService()
