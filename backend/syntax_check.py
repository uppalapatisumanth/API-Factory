try:
    from services import pytest_generator
    print("Syntax OK")
except Exception as e:
    import traceback
    traceback.print_exc()
