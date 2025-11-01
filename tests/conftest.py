"""
Test configuration and fixtures.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_generation.core.config_manager import VideoConfig, ConfigManager
from video_generation.generators.rag_platform_generator import RAGPlatformVideoGenerator


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_config(temp_dir):
    """Create sample video configuration."""
    return VideoConfig(
        project_name="Test Project",
        project_description="Test description",
        tech_stack=["Python", "Test"],
        output_dir=str(temp_dir / "output"),
        temp_dir=str(temp_dir / "temp"),
        voice_name="en-US-AriaNeural",
        voice_speed=1.0,
        video_resolution="1920x1080",
        video_quality="high",
        slide_duration=5.0
    )


@pytest.fixture
def config_manager(temp_dir):
    """Create config manager with temporary directory."""
    config_dir = temp_dir / "config"
    config_dir.mkdir()
    return ConfigManager(config_dir)


@pytest.fixture
def mock_generator(sample_config):
    """Create mock video generator."""
    with patch('src.video_generation.generators.rag_platform_generator.subprocess.run') as mock_subprocess:
        mock_subprocess.return_value.returncode = 0
        generator = RAGPlatformVideoGenerator(sample_config)
        yield generator


@pytest.fixture
def sample_slides():
    """Sample slide data for testing."""
    return [
        {
            "title": "Test Slide 1",
            "subtitle": "Introduction",
            "content": "This is a test slide",
            "background": "gradient-blue"
        },
        {
            "title": "Test Slide 2",
            "subtitle": "Features",
            "content": "• Feature 1\n• Feature 2",
            "background": "gradient-purple"
        }
    ]


@pytest.fixture
def sample_script():
    """Sample script for testing."""
    return """
    Welcome to the Test Project!
    
    This project demonstrates the RAG Agent Platform capabilities.
    
    Key features include:
    • RAG System
    • Video Generation
    • Agent Architecture
    
    Thank you for watching!
    """.strip()
