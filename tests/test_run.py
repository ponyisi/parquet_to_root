import pytest

def test_run():
    ROOT = pytest.importorskip("ROOT")
    ROOT.TFile
    return True


# def test_dummy():
#     return True
