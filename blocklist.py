"""
    - this file contains blocked JWT tokens
    - it will be imported by the app and the logout resource so that tokens
    can be added to the blocklist when the user logs out
"""

# instead of set(), db should be user for storage of JWTs, like Redis
BLOCKLIST = set()