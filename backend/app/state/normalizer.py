class EntityNormalizer:
    def __init__(self):
        self.product_aliases = {
            "novabook": "NovaBook Pro",
            "nova book": "NovaBook Pro",
            "novaphone": "NovaPhone X",
            "nova phone": "NovaPhone X",
            "novagame": "NovaGame System",
            "nova game": "NovaGame System"
        }
        
    def normalize(self, entities: dict) -> dict:
        """Canonicalize extracted values."""
        normalized = entities.copy()
        
        if "current_product" in normalized:
            raw_product = normalized["current_product"].lower()
            normalized["current_product"] = self.product_aliases.get(raw_product, raw_product.title())
            
        return normalized
