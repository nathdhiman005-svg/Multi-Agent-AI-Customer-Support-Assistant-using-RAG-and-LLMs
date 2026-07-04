import re

class EntityExtractor:
    def extract(self, text: str) -> dict:
        """Deterministic extraction of objective data."""
        entities = {}
        
        # Extract emails
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            entities["email_address"] = email_match.group(0)
            
        # Extract order IDs (e.g., ORD-12345 or #12345)
        order_match = re.search(r'(?:ORD-|#)(\d+)', text, re.IGNORECASE)
        if order_match:
            entities["order_id"] = order_match.group(1)
            
        # Extract product names via simple keyword matching
        text_lower = text.lower()
        if "novabook" in text_lower or "nova book" in text_lower:
            entities["current_product"] = "novabook"
        elif "novaphone" in text_lower or "nova phone" in text_lower:
            entities["current_product"] = "novaphone"
        elif "novagame" in text_lower or "nova game" in text_lower:
            entities["current_product"] = "novagame"
            
        # Extract payment method
        if "visa" in text_lower:
            entities["payment_method"] = "Visa"
        elif "mastercard" in text_lower:
            entities["payment_method"] = "Mastercard"
        elif "paypal" in text_lower:
            entities["payment_method"] = "PayPal"
            
        return entities
