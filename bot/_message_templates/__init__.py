"""Templates for messages in different languages"""
# To add a new language populate a copy of the general_template.json file

import json

# Templated messages for different languages
with open("bot/_message_templates/general_template.json") as f:
    general = json.load(f)
    message_templates = {"en": general, "ru": general}
