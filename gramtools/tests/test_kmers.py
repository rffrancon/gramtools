import unittest

from . import common
from .. import parse_prg
from .. import kmers


class TestDirectionalRegionRange(unittest.TestCase):
    def _analyse_case(self, start_region_idx, max_base_distance,
                      prg_structure, expected, reverse):
        prg = common.compose_prg(prg_structure)
        regions = parse_prg.parse(prg)
        start_region = regions[start_region_idx]
        region_range = kmers._directional_region_range(max_base_distance,
                                                       start_region,
                                                       regions,
                                                       reverse=reverse)
        result = [region.alleles for region in region_range]
        self.assertEqual(result, expected)

    def test_rightEdgeStartingRegion_noForwardRegions(self):
        prg_structure = [
            ['C'],
            ['G', 'T'],
            ['A'],
            ['TC', 'A'],
        ]
        expected = []
        start_region_idx = -1
        max_base_distance = 100
        reverse = False
        self._analyse_case(start_region_idx, max_base_distance,
                           prg_structure, expected, reverse)

    def test_leftEdgeStartingRegion_noReverseRegions(self):
        prg_structure = [
            ['G', 'T'],
            ['A'],
            ['TC', 'A'],
            ['C'],
        ]
        expected = []
        start_region_idx = 0
        max_base_distance = 100
        reverse = True
        self._analyse_case(start_region_idx, max_base_distance,
                           prg_structure, expected, reverse)

    def test_populatedRevRegion_revRegionCorrectlyOrdered(self):
        prg_structure = [
            ['C', 'G'],
            ['G'],
            ['A', 'T'],
            ['CCCCCCCC'],
            ['GC', 'TC'],
        ]
        expected = [
            ['C', 'G'],
            ['G'],
        ]
        start_region_idx = 2
        max_base_distance = 2
        reverse = True
        self._analyse_case(start_region_idx, max_base_distance,
                           prg_structure, expected, reverse)

    def test_populatedFwdRegion_fwdRegionCorrectlyOrdered(self):
        prg_structure = [
            ['G'],
            ['GC', 'TC'],
            ['C'],
            ['A', 'T'],
            ['G'],
            ['C', 'G'],
        ]
        expected = [
            ['G'],
            ['C', 'G'],
        ]
        start_region_idx = 3
        max_base_distance = 2
        reverse = False
        self._analyse_case(start_region_idx, max_base_distance,
                           prg_structure, expected, reverse)


class TestRegionsWithinDistance(unittest.TestCase):
    def _analyse_case(self, start_region_idx, max_base_distance,
                      prg_structure, expected):
        prg = common.compose_prg(prg_structure)
        regions = parse_prg.parse(prg)
        start_region = regions[start_region_idx]
        region_range = kmers._regions_within_distance(max_base_distance,
                                                      start_region,
                                                      regions)
        result = [region.alleles for region in region_range]
        self.assertEqual(result, expected)

    def test_distanceExcludesRegion_lastRegionExcluded(self):
        prg_structure = [
            ['A', 'C'],
            ['CC'],
            ['G', 'T'],
        ]
        expected = [
            ['A', 'C'],
            ['CC'],
        ]
        start_region_idx = 0
        max_base_distance = 1
        self._analyse_case(start_region_idx,
                           max_base_distance,
                           prg_structure,
                           expected)

    def test_thresholdMaxDistance_startingRegionDistanceIgnored(self):
        prg_structure = [
            ['AAAAAAA', 'CCCCC'],
            ['CC'],
            ['G', 'T'],
        ]
        expected = [
            ['AAAAAAA', 'CCCCC'],
            ['CC'],
        ]
        start_region_idx = 0
        max_base_distance = 2
        self._analyse_case(start_region_idx,
                           max_base_distance,
                           prg_structure,
                           expected)

    def test_distanceEdgeIncludeLargeRegion_largeRegionInRange(self):
        prg_structure = [
            ['G'],
            ['A', 'T'],
            ['CC'],
            ['GGGGGGGG', 'T'],
        ]
        expected = [
            ['G'],
            ['A', 'T'],
            ['CC'],
            ['GGGGGGGG', 'T'],
        ]
        start_region_idx = 1
        max_base_distance = 3
        self._analyse_case(start_region_idx,
                           max_base_distance,
                           prg_structure,
                           expected)

    def test_shortDistance_excludesFwdRevRegions(self):
        prg_structure = [
            ['C', 'G'],
            ['G'],
            ['A', 'T'],
            ['CC'],
            ['GC', 'TC'],
        ]
        expected = [
            ['G'],
            ['A', 'T'],
            ['CC'],
        ]
        start_region_idx = 2
        max_base_distance = 1
        self._analyse_case(start_region_idx,
                           max_base_distance,
                           prg_structure,
                           expected)

    def test_largeFwdRegion_postFwdRegionsExcluded(self):
        prg_structure = [
            ['C', 'G'],
            ['G'],
            ['A', 'T'],
            ['CCCCCCCC'],
            ['GC', 'TC'],
        ]
        expected = [
            ['C', 'G'],
            ['G'],
            ['A', 'T'],
            ['CCCCCCCC'],
        ]
        start_region_idx = 2
        max_base_distance = 2
        self._analyse_case(start_region_idx,
                           max_base_distance,
                           prg_structure,
                           expected)

    def test_largeRevRegion_preRevRegionsExcluded(self):
        prg_structure = [
            ['T', 'A'],
            ['CCCCCCCC'],
            ['C', 'G'],
            ['G'],
            ['A', 'T'],
            ['GGGGGGG'],
        ]
        expected = [
            ['C', 'G'],
            ['G'],
            ['A', 'T'],
            ['GGGGGGG'],
        ]
        start_region_idx = 4
        max_base_distance = 2
        self._analyse_case(start_region_idx,
                           max_base_distance,
                           prg_structure,
                           expected)


class TestGenomePaths(unittest.TestCase):
    def _analyse_case(self, start_region_idx, max_base_distance,
                      prg_structure, expected):
        prg = common.compose_prg(prg_structure)
        regions = parse_prg.parse(prg)
        start_region = regions[start_region_idx]
        region_range = kmers._regions_within_distance(max_base_distance,
                                                      start_region,
                                                      regions)
        genome_paths = [path for path in
                        kmers._genome_paths(region_range)]
        self.assertEqual(genome_paths, expected)

    def test_twoVariantRegionsInRange_pathsIncludeAllAlleles(self):
        prg_structure = [
            ['AC'],
            ['T', 'G'],
            ['C'],
            ['A', 'T'],
        ]
        expected = [
            'ACTCA',
            'ACTCT',
            'ACGCA',
            'ACGCT',
        ]
        start_region_idx = 1
        max_base_distance = 3
        self._analyse_case(start_region_idx, max_base_distance,
                           prg_structure, expected)

    def test_manyAllelesInVarRegion_pathsIncludeAllAlleles(self):
        prg_structure = [
            ['AC'],
            ['T', 'G', 'C', 'AAA'],
            ['GT'],
        ]
        expected = [
            'ACTGT',
            'ACGGT',
            'ACCGT',
            'ACAAAGT',
        ]
        start_region_idx = 1
        max_base_distance = 3
        self._analyse_case(start_region_idx, max_base_distance,
                           prg_structure, expected)


class TestKmersFromGenomePaths(unittest.TestCase):
    def _analyse_case(self, genome_paths, kmer_size, expected):
        kmers_result = [kmer for kmer in
                        kmers._kmers_from_genome_paths(genome_paths, kmer_size)]
        self.assertEqual(kmers_result, expected)

    def test_singleGenomePath_allKmersGenerated(self):
        genome_paths = [
            'ACTGT',
        ]
        expected = [
            'ACT',
            'CTG',
            'TGT',
        ]
        kmer_size = 3
        self._analyse_case(genome_paths, kmer_size, expected)

    def test_multipleGenomePaths_allKmersGenerated(self):
        genome_paths = [
            'ACTGT',
            'TATC',
        ]
        expected = [
            'ACT',
            'CTG',
            'TGT',
            'TAT',
            'ATC',
        ]
        kmer_size = 3
        self._analyse_case(genome_paths, kmer_size, expected)

    def test_repeatedBases_duplicateKmersExcluded(self):
        genome_paths = [
            'TTTTTTTTTTT',
        ]
        expected = [
            'TTT',
        ]
        kmer_size = 3
        self._analyse_case(genome_paths, kmer_size, expected)


class TestGenerate(unittest.TestCase):
    def test_complexPrgStructure_allKmersGenerated(self):
        prg_structure = [
            ['TC', 'A'],
            ['CTTTGAC'],
            ['AGC', 'TCA'],
            ['AGATCTGG'],
            ['TC', 'A'],
        ]
        prg = common.compose_prg(prg_structure)
        regions = parse_prg.parse(prg)
        kmer_size = 3
        max_base_distance = 5
        nonvariant_kmers = False

        all_expected = [
            'TCC',  # first variant region, first allele
            'CCT',

            'CTT',  # first non-variant region
            'TTT',
            'TTG',
            'TGA',
            'GAC',

            'ACT',  # first variant region, second allele

            'ACA',  # first non-variant region
            'CAG',

            'AGC',  # second variant region, first allele
            'GCA',

            'AGA',  # second non-variant region
            'GAT',
            'ATC',
            'TCT',
            'CTG',
            'TGG',

            'CTC',  # first non-variant region

            'TCA',  # second variant region, second allele
            'CAA',
            'AAG',

            'GGT',  # second non-variant region
            'GTC',
            'GGA',
        ]

        generated_kmers = kmers._generate(max_base_distance, kmer_size, regions, nonvariant_kmers)
        for kmer, expected in zip(generated_kmers, all_expected):
            self.assertEqual(kmer, expected)
