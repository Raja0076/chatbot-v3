import os
import sys

# Get backend directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)

# Add backend directory to path so Python can access data folder
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from data.responses import responses


def get_response(intent):
    """
    Return response text based on predicted intent.
    """

    if intent in responses:
        return responses[intent]

    return responses["default"]