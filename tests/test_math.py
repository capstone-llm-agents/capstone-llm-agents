"""Test math example for pytest."""


class TestMath:
    """Test math operations."""

    def test_addition(self) -> None:
        """Test addition operation."""
        assert 1 + 1 == 2, "Addition test failed"

    def test_subtraction(self) -> None:
        """Test subtraction operation."""
        assert 5 - 3 == 2, "Subtraction test failed"

    def test_multiplication(self) -> None:
        """Test multiplication operation."""
        assert 3 * 4 == 12, "Multiplication test failed"

    def test_division(self) -> None:
        """Test division operation."""
        assert 10 / 2 == 5, "Division test failed"
