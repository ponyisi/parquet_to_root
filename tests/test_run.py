import pytest

def test_run():
    ROOT = pytest.importorskip("ROOT")
    from parquet_to_root import parquet_to_root
    parquet_to_root('tests/samples/HZZ.parquet', 'HZZ.root', verbose=True)
    rf = ROOT.TFile.Open('HZZ.root')
    t = rf.Get('parquettree')
    assert t.GetEntries() == 2421
    return True

