"""Tests for Chonkie Chef base classes."""

import os
import pytest
from pathlib import Path

from chonkie.chefs import (
    BaseChef,
    PDFProcessingChef,
    ProcessingResult,
    ProcessingStatus,
    BaseChefConfig,
    PDFChefConfig,
    ValidationError,
)
from chonkie.types import Document, PDFDocument


class TestChef(PDFProcessingChef):
    """Test implementation of PDFProcessingChef."""
    
    def process(self, file_path: str, **kwargs) -> ProcessingResult:
        """Test implementation of process."""
        return ProcessingResult(
            status=ProcessingStatus.SUCCESS,
            document=PDFDocument(text="Test document"),
            metadata={"test": True}
        )


def test_chef_initialization():
    """Test Chef initialization."""
    config = PDFChefConfig(ocr_enabled=False)
    chef = TestChef("test", "1.0.0", config)
    
    assert chef.name == "test"
    assert chef.version == "1.0.0"
    assert not chef.config.ocr_enabled
    assert chef.supported_formats == ["pdf"]


def test_chef_metadata():
    """Test Chef metadata retrieval."""
    chef = TestChef("test", "1.0.0")
    metadata = chef.get_metadata()
    
    assert metadata["name"] == "test"
    assert metadata["version"] == "1.0.0"
    assert "config" in metadata


def test_file_validation(tmp_path):
    """Test file validation."""
    chef = TestChef("test", "1.0.0")
    
    # Test non-existent file
    with pytest.raises(ValidationError):
        chef.validate_file("nonexistent.pdf")
    
    # Test non-PDF file
    non_pdf = tmp_path / "test.txt"
    non_pdf.touch()
    with pytest.raises(ValidationError):
        chef.validate_file(str(non_pdf))
    
    # Create a test PDF file
    test_pdf = tmp_path / "test.pdf"
    test_pdf.touch()
    
    try:
        assert chef.validate_file(str(test_pdf))
    finally:
        # No need to manually clean up when using tmp_path
        pass


def test_processing_result():
    """Test ProcessingResult creation and access."""
    doc = PDFDocument(text="Test")
    result = ProcessingResult(
        status=ProcessingStatus.SUCCESS,
        document=doc,
        metadata={"test": True}
    )
    
    assert result.status == ProcessingStatus.SUCCESS
    assert result.document == doc
    assert result.metadata["test"]
    assert result.error is None


def test_base_config():
    """Test BaseChefConfig functionality."""
    config = BaseChefConfig()
    
    # Test default values
    assert config.timeout == 300
    assert config.max_file_size is None
    
    # Test update
    config.update(timeout=600, custom_setting="test")
    assert config.timeout == 600
    assert config.additional_settings["custom_setting"] == "test"
    
    # Test to_dict
    config_dict = config.to_dict()
    assert "timeout" in config_dict
    assert "custom_setting" in config_dict


def test_pdf_config():
    """Test PDFChefConfig functionality."""
    config = PDFChefConfig()
    
    # Test default values
    assert config.ocr_enabled
    assert config.extract_images
    assert config.language == "eng"
    
    # Test update
    config.update(ocr_enabled=False, custom_setting="test")
    assert not config.ocr_enabled
    assert config.additional_settings["custom_setting"] == "test"
    
    # Test to_dict
    config_dict = config.to_dict()
    assert "ocr_enabled" in config_dict
    assert "custom_setting" in config_dict 