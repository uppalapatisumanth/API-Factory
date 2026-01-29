try:
    from services import pytest_generator
    print("SUCCESS: pytest_generator imported")
except Exception as e:
    import traceback
    print("FAILURE: Could not import pytest_generator")
    traceback.print_exc()
