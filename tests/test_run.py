import pytest


def test_run():
    from parquet_to_root import parquet_to_root
    ROOT = pytest.importorskip("ROOT")
    parquet_to_root('tests/samples/HZZ.parquet', 'HZZ.root', verbose=True)
    rdf = ROOT.RDataFrame('parquettree', 'HZZ.root')
    assert rdf.Count().GetValue() == 2421
    assert rdf.GetColumnNames().size() == 74
    assert rdf.Mean("Muon_Px").GetValue() == -0.6551689155476192
    assert rdf.Mean("MET_px").GetValue() == 0.23863275654291605
    return True


def test_cmdline():
    ROOT = pytest.importorskip("ROOT")
    import subprocess
    chk = subprocess.run("python3 -m parquet_to_root tests/samples/HZZ.parquet HZZ.root -t newtree",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()

    rf = ROOT.TFile.Open('HZZ.root')
    t = rf.Get('newtree')
    assert t.GetEntries() == 2421
    return True
