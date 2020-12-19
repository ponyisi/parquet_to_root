import pytest
ROOT = pytest.importorskip("ROOT")

def test_run():
    ROOT.TFile
    return True

def test_dummy():
    return True