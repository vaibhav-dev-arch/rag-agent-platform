"""
RAG Agent Platform - A comprehensive RAG system with agent architecture.
"""

__version__ = "1.0.0"
__author__ = "RAG Agent Platform Team"
__description__ = "A comprehensive RAG (Retrieval-Augmented Generation) platform with agent architecture"

from .rag_agent import *
from .shared import *

__all__ = [
    "rag_agent",
    "shared"
]
