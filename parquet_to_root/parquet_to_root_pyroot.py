def _get_outfile(outfile):
    if isinstance(outfile, ROOT.TFile):
        outfile.cd()
        return outfile, False
    else:
        fout = ROOT.TFile.Open(outfile, 'RECREATE')
        return fout, True


def parquet_to_root_pyroot(infile, outfile, treename='parquettree',
                           verbose=False):
    import pyarrow.parquet as pq
    import pyarrow
    import ROOT
    import numpy

    # Use parquet metadata for schema
    table = pq.read_table(infile)
    schema = table.schema

    fout, local_root_file_creation = _get_outfile(outfile)
    tree = ROOT.TTree(treename, 'Parquet tree')

    dtypemap = {'int8': 'B',
                'uint8': 'b',
                'int16': 'S',
                'uint16': 's',
                'int32': 'I',
                'uint32': 'i',
                'float': 'F',
                'halffloat': 'f',
                'double': 'D',
                'int64': 'L',
                'uint64': 'l',
                'bool': 'O'}

    # Buffers for primitive types
    numpybufs = {}
    # Buffers for lengths of list types
    vectorlens = {}

    if verbose:
        print('Translating branches:')
    for branch in schema.names:
        field = schema.field(branch)
        if verbose:
            print(field.name, field.type)
        if field.type.num_fields == 0:
            # primitive types
            if field.type not in dtypemap:
                raise ValueError(f'Field {field.name} has type "{field.type}" that is not supported')
            numpybufs[branch] = numpy.zeros(shape=[1], dtype=field.type.to_pandas_dtype())
            tree.Branch(branch, numpybufs[branch], branch+'/'+dtypemap[field.type])
        elif field.type.num_fields == 1 and isinstance(field.type, pyarrow.lib.ListType):
            # lists of a single type
            if field.type.value_type not in dtypemap:
                raise ValueError(f'Field {field.name} is array of type "{field.type.value_type}" that is not supported')
            # Apache Arrow spec allows array lengths to be *signed* 64 bit integers
            vectorlens[branch] = numpy.zeros(shape=[1], dtype='int64')
            tree.Branch(f'{branch}_parquet_n', vectorlens[branch], f'{branch}_parquet_n/L')
            # temp array for initialization
            v0 = numpy.zeros(shape=[1], dtype=field.type.value_type.to_pandas_dtype())
            tree.Branch(branch, v0,
                        f'{branch}[{branch}_parquet_n]/{dtypemap[field.type.value_type]}')
        else:
            raise ValueError(f'Cannot translate field "{branch}" of input Parquet schema. Field is described as {field.type}')

    # Fill loop
    for entry in range(len(table)):
        for branch in numpybufs:
            numpybufs[branch][0] = table[branch][entry].as_py()
        for branch in vectorlens:
            values_arrow = table[branch][entry]
            vectorlens[branch][0] = len(values_arrow)
            # Booleans don't work with zero copy but everything else should
            values = values_arrow.values.to_numpy(zero_copy_only=False)
            tree.SetBranchAddress(branch, values)

        tree.Fill()

    tree.Write()
    if local_root_file_creation:
        fout.Close()


if __name__ == '__main__':
    import sys
    import os
    foutname = os.path.basename(os.path.splitext(sys.argv[1])[0])+'.root'

    parquet_to_root_pyroot(sys.argv[1], foutname,
                           'parquettree' if len(sys.argv) < 3 else sys.argv[2],
                           True)
