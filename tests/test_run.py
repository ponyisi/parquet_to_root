import pytest

def test_run():
    from parquet_to_root import parquet_to_root
    ROOT = pytest.importorskip("ROOT")
    parquet_to_root('tests/samples/HZZ.parquet', 'HZZ.root', verbose=True)
    rf = ROOT.TFile.Open('HZZ.root')
    t = rf.Get('parquettree')
    assert t.GetEntries() == 2421
    return True

