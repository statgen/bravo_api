import pytest
from unittest import TestCase
from bravo_api.models import utils


def test_numeral_chrom_make_xpos():
    input_chr = "2"
    input_pos = 555

    expected = 2_000_000_555
    result = utils.make_xpos(input_chr, input_pos)

    assert expected == result


def test_prefixed_chrom_make_xpos():
    input_chr = "chr2"
    input_pos = 555

    expected = 2_000_000_555
    result = utils.make_xpos(input_chr, input_pos)

    assert expected == result


def test_prefixed_bad_chrom_make_xpos():
    input_chr = "chr33"
    input_pos = 777

    expected = -1
    result = utils.make_xpos(input_chr, input_pos)

    assert expected == result


def test_numeral_bad_chrom_make_xpos():
    input_chr = "33"
    input_pos = 777

    expected = -1
    result = utils.make_xpos(input_chr, input_pos)

    assert expected == result
