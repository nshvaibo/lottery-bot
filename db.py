"""Database"""
import os

from google.cloud import firestore

import config

# Setup Google Cloud service account credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GOOGLE_APPLICATION_CREDENTIALS

# The `project` parameter is optional and represents which project the client
# will act on behalf of. If not supplied, the client falls back to the default
# project inferred from the environment.
db = firestore.Client(project="lottery-bot-366521")
