"""Safe environment defaults for the isolated backend test suite."""

import os

os.environ["ENVIRONMENT"] = "test"
os.environ["SECRET_KEY"] = "salesia-test-secret-key-with-at-least-32-characters"
