"""
Classification Service for IntelliBin.
Handles substance identification and categorization.
"""

from typing import Optional
from .state import state_manager


class ClassificationService:
    """
    Classifies substances by name lookup and alias resolution.
    """
    
    def __init__(self):
        self.state = state_manager
        self._build_lookup_index()
    
    def _build_lookup_index(self):
        """Build reverse lookup index for aliases"""
        self.name_index: dict = {}  # lowercase name -> substance
        self.alias_index: dict = {}  # lowercase alias -> substance
        
        for substance in self.state.substances.values():
            # Index by name
            self.name_index[substance["name"].lower()] = substance
            
            # Index by aliases
            for alias in substance.get("aliases", []):
                self.alias_index[alias.lower()] = substance
    
    def classify(self, substance_name: str) -> Optional[dict]:
        """
        Classify a substance by name.
        Returns substance profile or None if not found.
        
        Tries matching in order:
        1. Exact name match
        2. Exact alias match
        3. Partial name match
        4. Partial alias match
        """
        name_lower = substance_name.lower().strip()
        
        # Try exact name match
        if name_lower in self.name_index:
            return self.name_index[name_lower]
        
        # Try exact alias match
        if name_lower in self.alias_index:
            return self.alias_index[name_lower]
        
        # Try partial match on names
        for name, substance in self.name_index.items():
            if name_lower in name or name in name_lower:
                return substance
        
        # Try partial match on aliases
        for alias, substance in self.alias_index.items():
            if name_lower in alias or alias in name_lower:
                return substance
        
        return None
    
    def get_waste_stream(self, substance: dict) -> str:
        """Get the default waste stream for a substance"""
        return substance.get("default_waste_stream", "GeneralChemical")
    
    def get_category(self, substance: dict) -> str:
        """Get the category for a substance"""
        return substance.get("category", "Unknown")
    
    def get_incompatibilities(self, substance: dict) -> list[str]:
        """Get list of incompatible categories for a substance"""
        return substance.get("incompatible_with", [])
    
    def search_substances(self, query: str) -> list[dict]:
        """Search for substances matching query"""
        query_lower = query.lower().strip()
        results = []
        seen_ids = set()
        
        for substance in self.state.substances.values():
            if substance["id"] in seen_ids:
                continue
                
            # Check name
            if query_lower in substance["name"].lower():
                results.append(substance)
                seen_ids.add(substance["id"])
                continue
            
            # Check aliases
            for alias in substance.get("aliases", []):
                if query_lower in alias.lower():
                    results.append(substance)
                    seen_ids.add(substance["id"])
                    break
            
            # Check category
            if query_lower in substance.get("category", "").lower():
                if substance["id"] not in seen_ids:
                    results.append(substance)
                    seen_ids.add(substance["id"])
        
        return results
    
    def get_all_categories(self) -> list[str]:
        """Get list of all unique categories"""
        categories = set()
        for substance in self.state.substances.values():
            categories.add(substance.get("category", "Unknown"))
        return sorted(list(categories))
    
    def get_substances_by_category(self, category: str) -> list[dict]:
        """Get all substances in a category"""
        return [
            s for s in self.state.substances.values()
            if s.get("category", "").lower() == category.lower()
        ]


# Singleton instance
classification_service = ClassificationService()
