from helpers.config import Config
import logging

logger = logging.getLogger("Rodam")

class SearchModalHelper:
    """
    Helper class to process data from the Search Modal and update the Config.
    """

    @staticmethod
    def process_form_data(data: dict, config: Config):
        """
        Updates the config object with values from the data dictionary.
        Handles type conversion based on Config attributes.
        """
        logger.info("Processing search form data...")
        
        # Mapping of expected fields types based on Config defaults
        # We manually map mostly because form data is all strings (or booleans from JSON)
        
        # 1. Query
        if "query" in data:
            config.query = data["query"]

        # 2. Enums / Integers
        if "LanguageIdToSearch" in data:
            try:
                config.LanguageIdToSearch = int(data["LanguageIdToSearch"])
            except ValueError:
                pass

        if "SearchResultsOrder" in data:
            try:
                config.SearchResultsOrder = int(data["SearchResultsOrder"])
            except ValueError:
                pass
                
        if "SearchMaxResults" in data:
            try:
                config.SearchMaxResults = int(data["SearchMaxResults"])
            except ValueError:
                pass

        if "SearchItemsToShow" in data:
            try:
                config.SearchItemsToShow = int(data["SearchItemsToShow"])
            except ValueError:
                pass


        # 3. Scope Logic (Radio Button 'scopeType')
        # The form sends 'scopeType': 'parts' or 'docs'
        # based on this we set SearchParts and SearchDocuments
        if "scopeType" in data:
            scope = data["scopeType"]
            if scope == "parts":
                config.SearchParts = True
                config.SearchDocuments = False
            elif scope == "docs":
                config.SearchParts = False
                config.SearchDocuments = True

        # 4. Booleans (Checkboxes)
        # In JSON payload from JS, these will be true/false booleans.
        # If we were using standard form submit, they would be 'on' or missing.
        # But our JS refactor will use JSON.
        
        # Helper to safely get bool
        def get_bool(key):
            val = data.get(key)
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.lower() in ('true', '1', 'on', 'yes')
            return False

        if config.SearchParts:
            config.SearchIntroduction = get_bool("SearchIntroduction")
            config.SearchPartI = get_bool("SearchPartI")
            config.SearchPartII = get_bool("SearchPartII")
            config.SearchPartIII = get_bool("SearchPartIII")
            config.SearchPartIV = get_bool("SearchPartIV")

        # 5. Strings
        if config.SearchDocuments:
            if "SearchDocumentsList" in data:
                config.SearchDocumentsList = data["SearchDocumentsList"]

        # Save immediately
        config.save()
        logger.info("Search config updated and saved.")
