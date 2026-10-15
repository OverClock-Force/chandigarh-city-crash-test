"""
C3T AI Intake Module
Extracts structured civic incident attributes from citizen natural language text.
Strict ethical rule: Always requires human-in-the-loop confirmation. Never guesses locations.
"""

from .extractor import ComplaintExtractor, ExtractedComplaint

__all__ = ["ComplaintExtractor", "ExtractedComplaint"]
