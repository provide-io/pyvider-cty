try:
    import pytest_mock
    print("pytest-mock successfully imported")
except ImportError:
    print("Error: pytest-mock could not be imported")
    import sys
    sys.exit(1)
