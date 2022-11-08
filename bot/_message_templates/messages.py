"""Class that handles template messages and language selection"""

import json

class Messages:
    def __init__(self, language_files: dict) -> None:
        # Templated messages holder for different languages
        self.language_templates = {}

        # Read templated messages into holder from language files
        for lang, file_name in language_files.items():
            with open(file_name) as f:
                templates = json.load(f)
                self.language_templates[lang] = templates
    
    def __getitem__(self, lang):
        # If language present in templates
        if lang in self.language_templates:
            return self.language_templates[lang]
        
        # By default use English messages
        return self.language_templates["en"]

language_files = {
    "en": "bot/_message_templates/general_template.json"
}

message_templates = Messages(language_files)