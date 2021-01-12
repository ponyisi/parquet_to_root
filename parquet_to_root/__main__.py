from . import parquet_to_root
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('infile', nargs='+', help='Input Parquet file')
parser.add_argument('outfile', help='Output ROOT file')
parser.add_argument('--treename', '-t', default='parquettree',
                    help='Name of TTree')
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Verbose output')
opts = parser.parse_args()

try:
    parquet_to_root(opts.infile, opts.outfile,
                    opts.treename,
                    opts.verbose)
except Exception as e:
    print('Failure...')
    print(e)
    sys.exit(1)
