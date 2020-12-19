# parquet_to_root
Simple translator from Parquet to ROOT TTree

Install: `pip3 install parquet_to_root`

Requires `PyROOT` and `pyarrow`. The latter can be installed via `pip`; the former is more complicated, but if you're reading this you probably know how to get it.  (The tests in this package use miniconda: `conda install -c conda-forge root`.)

To run from the command line:

`python3 -m parquet_to_root infile.parquet outfile.root [-t TREENAME] [--verbose]`

To run from your script,
```
    from parquet_to_root import parquet_to_root
    parquet_to_root(parquetfile, rootfile, treename='parquettree', verbose=False)
```
where the default values are shown for the optional arguments.
