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


def test_run_with_strings():
    from parquet_to_root import parquet_to_root
    ROOT = pytest.importorskip("ROOT")
    parquet_to_root('tests/samples/exoplanets.parquet', 'exoplanets.root', treename='stars')
    rf = ROOT.TFile.Open('exoplanets.root')
    t = rf.Get('stars')
    t.GetEntry(8)
    assert t.name == '24 Sex'
    assert list(t.planet_name) == ['b', 'c']
    return True


def test_run_with_fileobj():
    from parquet_to_root import parquet_to_root
    ROOT = pytest.importorskip("ROOT")
    inf = open('tests/samples/HZZ.parquet', 'rb')
    outf = ROOT.TFile.Open('HZZ.root', 'RECREATE')
    parquet_to_root(inf, outf, verbose=True)
    outf.Close()
    rdf = ROOT.RDataFrame('parquettree', 'HZZ.root')
    assert rdf.Count().GetValue() == 2421
    return True


def test_run_with_existing_rootfile():
    from parquet_to_root import parquet_to_root
    ROOT = pytest.importorskip("ROOT")
    parquet_to_root('tests/samples/HZZ.parquet', 'combined.root', treename='HZZ', verbose=True)
    outf = ROOT.TFile.Open('combined.root', 'UPDATE')
    parquet_to_root('tests/samples/exoplanets.parquet', outf, treename='stars', verbose=True)
    outf.Close()
    rf = ROOT.TFile.Open('combined.root')
    t1 = rf.Get('HZZ')
    assert t1.GetEntries() == 2421
    t2 = rf.Get('stars')
    assert t2.GetEntries() == 2935
    return True


def test_run_with_multiple_inputs():
    from parquet_to_root import parquet_to_root
    ROOT = pytest.importorskip("ROOT")
    parquet_to_root(['tests/samples/HZZ.parquet','tests/samples/HZZ.parquet'],
                     'HZZ.root', verbose=True)
    rdf = ROOT.RDataFrame('parquettree', 'HZZ.root')
    assert rdf.Count().GetValue() == 4842
    assert rdf.GetColumnNames().size() == 74
    assert rdf.Mean("Muon_Px").GetValue() == -0.6551689155476192
    assert rdf.Mean("MET_px").GetValue() == 0.23863275654291605
    return True


def test_fail_on_incompatible_inputs():
    from parquet_to_root import parquet_to_root
    ROOT = pytest.importorskip("ROOT")
    with pytest.raises(ValueError):
        parquet_to_root(['tests/samples/HZZ.parquet','tests/samples/exoplanets.parquet'], 
                         'HZZ.root', verbose=True)


def test_cmdline_multiple_inputs():
    ROOT = pytest.importorskip("ROOT")
    import subprocess
    chk = subprocess.run("python3 -m parquet_to_root tests/samples/HZZ.parquet tests/samples/HZZ.parquet HZZ.root -t newtree",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()

    rf = ROOT.TFile.Open('HZZ.root')
    t = rf.Get('newtree')
    assert t.GetEntries() == 4842
    return True


def test_cmdline_incompatible_inputs():
    ROOT = pytest.importorskip("ROOT")
    import subprocess
    chk = subprocess.run("python3 -m parquet_to_root tests/samples/HZZ.parquet tests/samples/exoplanets.parquet HZZ.root -t newtree",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    with pytest.raises(subprocess.CalledProcessError):
        chk.check_returncode()

    return True
