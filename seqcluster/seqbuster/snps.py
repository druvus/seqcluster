import sys

STDOUT = sys.stdout

def _parse_mut(mut):
    """
    Parse mutation field to get position and nts.
    """
    multiplier = 1
    if mut.startswith("-"):
        mut = mut[1:]
        multiplier = -1
    nt = mut.strip('0123456789')
    pos = int(mut[:1]) * multiplier
    return nt, pos

def _get_reference_position(isomir):
    """
    Liftover from mature to reference position
    """
    mut = isomir.split(":")[1]
    if mut == "0":
        return mut
    nt, pos = _parse_mut(mut)
    trim5 = isomir.split(":")[-2]
    off = -1 * len(trim5)
    if trim5.isupper():
        off = len(trim5)
    return "%s%s" % (pos + off, nt)

def _get_pct(isomirs, mirna):
    """
    Get pct of variants respect to the reference
    using reads and different sequences
    """
    pass_pos = []
    for isomir in isomirs.iterrows():
        mir = isomir[1]["chrom"]
        mut = isomir[1]["sv"]
        total = mirna.loc[mir, "counts"] * 1.0
        mut_counts = isomir[1]["counts"]
        mut_diff = isomir[1]["diff"]
        ratio = mut_counts / total
        if mut_counts > 10 and ratio  > 0.4 and mut != "0" and mut_diff > 1:
            isomir[1]["ratio"] = ratio
            pass_pos.append(isomir[1])
    return pass_pos

def _genotype(data):
    """Simple decision about genotype."""
    if  data['ratio'] > 0.9:
        return "1/1"
    return "1/0"

def _print_header(data):
    """
    Create vcf header to make
    a valid vcf.
    """
    print >>STDOUT, "##fileformat=VCFv4.2"
    print >>STDOUT, "##source=seqbuster2.3"
    print >>STDOUT, "##reference=mirbase"
    for pos in data:
        print >>STDOUT, "##contig=<ID=%s>" % pos["chrom"]
    print >>STDOUT, '##INFO=<ID=ID,Number=1,Type=String,Description="miRNA name">'
    print >>STDOUT, '##FORMAT=<ID=GT,Number=1,Type=Integer,Description="Genotype">'
    print >>STDOUT, '##FORMAT=<ID=NR,Number=A,Type=Integer,Description="Total reads supporting the variant">'
    print >>STDOUT, '##FORMAT=<ID=NS,Number=A,Type=Float,Description="Total number of different sequences supporting the variant">'
    print >>STDOUT, "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMP001"

def print_vcf(data):
    """Print vcf line following rules."""
    id_name = "."
    qual = "."
    chrom = data['chrom']
    pos = data['pre_pos']
    nt_ref = data['nt'][1]
    nt_snp = data['nt'][0]
    flt = "PASS"
    info = "ID=%s" % data['mature']
    frmt = "GT:NR:NS"
    gntp = "%s:%s:%s" % (_genotype(data), data["counts"], data["diff"])
    print >>STDOUT, "\t".join(map(str, [chrom, pos, id_name, nt_ref, nt_snp, qual, flt, info, frmt, gntp]))

def _make_header():
    """
    Make vcf header for SNPs in miRs
    """

def liftover(pass_pos, matures):
    """Make position at precursor"""
    fixed_pos = []
    _print_header(pass_pos)
    for pos in pass_pos:
        mir = pos["mature"]
        db_pos = matures[pos["chrom"]]
        mut = _parse_mut(pos["sv"])
        pos['pre_pos'] =  db_pos[mir][0] + mut[1]
        pos['nt'] = list(mut[0])
        fixed_pos.append(pos)
        print_vcf(pos)
    return fixed_pos

def create_vcf(isomirs, matures, stdout=None):
    """
    Create vcf file of changes for all samples.
    PASS will be ones with > 3 isomiRs supporting the position
         and > 30% of reads, otherwise LOW
    """
    isomirs['sv'] = [_get_reference_position(m) for m in isomirs["isomir"]]
    mirna = isomirs.groupby(['chrom']).sum()
    sv = isomirs.groupby(['chrom', 'mature', 'sv'], as_index=False).sum()
    sv["diff"] = isomirs.groupby(['chrom', 'mature', 'sv'], as_index=False).size().reset_index().loc[:,0]
    pass_pos = _get_pct(sv, mirna)
    if stdout: #if file
        STDOUT = stdout
    pass_pos = liftover(pass_pos, matures)