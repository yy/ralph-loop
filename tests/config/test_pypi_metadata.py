"""Tests for PyPI metadata in pyproject.toml."""

import tomllib
from pathlib import Path


def get_pyproject():
    """Load pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        return tomllib.load(f)


class TestPyPIMetadata:
    """Tests for PyPI package metadata."""

    def test_has_keywords(self):
        """Package should have keywords for discoverability."""
        pyproject = get_pyproject()
        keywords = pyproject["project"].get("keywords", [])
        assert len(keywords) >= 3, "Should have at least 3 keywords"
        assert any("agent" in k.lower() for k in keywords), "Should mention agents"

    def test_has_classifiers(self):
        """Package should have PyPI classifiers."""
        pyproject = get_pyproject()
        classifiers = pyproject["project"].get("classifiers", [])
        assert len(classifiers) >= 3, "Should have at least 3 classifiers"

    def test_has_development_status_classifier(self):
        """Package should declare development status."""
        pyproject = get_pyproject()
        classifiers = pyproject["project"].get("classifiers", [])
        has_dev_status = any(c.startswith("Development Status") for c in classifiers)
        assert has_dev_status, "Should have Development Status classifier"

    def test_has_python_version_classifier(self):
        """Package should declare Python version support."""
        pyproject = get_pyproject()
        classifiers = pyproject["project"].get("classifiers", [])
        has_python = any("Python :: 3" in c for c in classifiers)
        assert has_python, "Should have Python version classifier"

    def test_has_license_classifier(self):
        """Package should declare license."""
        pyproject = get_pyproject()
        classifiers = pyproject["project"].get("classifiers", [])
        has_license = any(c.startswith("License ::") for c in classifiers)
        assert has_license, "Should have License classifier"

    def test_has_project_urls(self):
        """Package should have project URLs."""
        pyproject = get_pyproject()
        urls = pyproject["project"].get("urls", {})
        assert "Homepage" in urls or "Repository" in urls, (
            "Should have Homepage or Repository URL"
        )

    def test_has_repository_url(self):
        """Package should have repository URL."""
        pyproject = get_pyproject()
        urls = pyproject["project"].get("urls", {})
        assert "Repository" in urls, "Should have Repository URL"
        assert "github.com" in urls["Repository"], "Repository should be on GitHub"
