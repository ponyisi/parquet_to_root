def _get_outfile(outfile):
    import ROOT
    if isinstance(outfile, ROOT.TFile):
        outfile.cd()
        return outfile, False
    else:
        fout = ROOT.TFile.Open(outfile, 'RECREATE')
        return fout, True


def _printout(verbose, msg):
    if verbose:
        print(msg)


_dtypemap = {'int8': 'B',
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


def _check_type_in_map(dtype, msg):
    if dtype not in _dtypemap:
        raise ValueError(msg)


def _setup_branch_scalar(field, tree, numpybufs, stringvars):
    import numpy
    import ROOT
    if field.type == 'string':
        stringvars.add(field.name)
        # dummy string
        s0 = ROOT.std.string()
        tree.Branch(field.name, s0)
    else:
        _check_type_in_map(field.type,
                           f'Field {field.name} has type "{field.type}" that is not supported')
        numpybufs[field.name] = numpy.zeros(shape=[1], dtype=field.type.to_pandas_dtype())
        tree.Branch(field.name, numpybufs[field.name], field.name+'/'+_dtypemap[field.type])


def _setup_branch_list(field, tree, vectorlens, stringarrs):
    import numpy
    import ROOT
    if field.type.value_type == 'string':
        # vector of strings
        sv0 = ROOT.std.vector(ROOT.std.string)()
        stringarrs[field.name] = sv0
        tree.Branch(field.name, sv0)
    else:
        _check_type_in_map(field.type.value_type,
                           f'Field {field.name} is array of type "{field.type.value_type}" that is not supported')
        # Apache Arrow spec allows array lengths to be *signed* 64 bit integers,
        # but ROOT tends to complain (e.g. RDataFrame) if array lengths are longer than 32 bits
        vectorlens[field.name] = numpy.zeros(shape=[1], dtype='int32')
        tree.Branch(f'{field.name}_parquet_n', vectorlens[field.name], f'{field.name}_parquet_n/I')
        # temp array for initialization
        v0 = numpy.zeros(shape=[1], dtype=field.type.value_type.to_pandas_dtype())
        tree.Branch(field.name, v0,
                    f'{field.name}[{field.name}_parquet_n]/{_dtypemap[field.type.value_type]}')


def _do_fill(tree, entry, table, numpybufs, stringvars, vectorlens, stringarrs):
    import ROOT
    ptrs = []
    for branch in numpybufs:
        numpybufs[branch][0] = table[branch][entry].as_py()
    for branch in stringvars:
        s0 = ROOT.std.string(table[branch][entry].as_py())
        tree.SetBranchAddress(branch, s0)
        ptrs.append(s0)
    for branch in vectorlens:
        values_arrow = table[branch][entry]
        vectorlens[branch][0] = len(values_arrow)
        # Booleans don't work with zero copy but everything else should
        values = values_arrow.values.to_numpy(zero_copy_only=False)
        ptrs.append(values)
        tree.SetBranchAddress(branch, values)
    for branch, vec in stringarrs.items():
        vec.clear()
        for string in table[branch][entry].as_py():
            vec.push_back(string)
    tree.Fill()


def normalize_parquet(infiles):
    '''Convert infiles argument to list; verify schema match across all files'''
    import pyarrow.parquet as pq
    import io

    # convert to a list
    if isinstance(infiles, str) or isinstance(infiles, io.IOBase):
        lfiles = [infiles]
    else:
        try:
            lfiles = list(infiles)
        except TypeError:
            # This really shouldn't be hit, but maybe there's an edge case
            lfiles = [infiles]

    schema = pq.read_schema(lfiles[0])
    for f in lfiles[1:]:
        schema2 = pq.read_schema(f)
        if schema != schema2:
            raise ValueError(f"Mismatched Parquet schemas between {infiles[0]} and {f}")

    return lfiles, schema    


def parquet_to_root_pyroot(infiles, outfile, treename='parquettree',
                           verbose=False):
    import pyarrow.parquet as pq
    import pyarrow
    import ROOT

    # Interpret files
    infiles, schema = normalize_parquet(infiles)

    fout, local_root_file_creation = _get_outfile(outfile)
    tree = ROOT.TTree(treename, 'Parquet tree')

    # Buffers for primitive types
    numpybufs = {}
    # Buffers for lengths of list types
    vectorlens = {}

    # Strings need to be treated differently due to memory layout
    # These variables are strings
    stringvars = set()
    # Vectors of strings
    stringarrs = {}

    _printout(verbose, 'Translating branches:')
    for branch in schema.names:
        field = schema.field(branch)
        _printout(verbose, f'{field.name}, {field.type}')
        if field.type.num_fields == 0:
            # primitive types
            _setup_branch_scalar(field, tree, numpybufs, stringvars)
        elif field.type.num_fields == 1 and isinstance(field.type, pyarrow.lib.ListType):
            # lists of a single type
            _setup_branch_list(field, tree, vectorlens, stringarrs)
        else:
            raise ValueError(f'Cannot translate field "{branch}" of input Parquet schema. Field is described as {field.type}')

    # Fill loop
    for infile in infiles:
        table = pq.read_table(infile)
        for entry in range(len(table)):
            # trash on every pass through loop; just here to make sure nothing gets garbage collected early
            _do_fill(tree, entry, table, numpybufs, stringvars, vectorlens, stringarrs)

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
