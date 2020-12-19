def test_run():
    try:
        import ROOT  # noqa: F401
    except ImportError:
        print("ROOT not available, aborting test")
        return True

    return True
