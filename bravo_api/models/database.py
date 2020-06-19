from flask_pymongo import PyMongo
import pymongo
import click
from flask.cli import with_appcontext
from flask import current_app
import sys
from bravo_api.models.readers import read_canonical_transcripts, read_omim, read_hgnc, read_gencode, read_snv, read_qc_metrics
from itertools import chain, islice
from multiprocessing import Pool


mongo = PyMongo()


@click.command('create-users')
@with_appcontext
def create_users():
   """
   Creates empty 'users' collection.
   """
   mongo.db.users.drop()
   mongo.db.users.create_index('user_id')
   sys.stdout.write("Created empty 'users' collection.\n")


@click.command('load-genes')
@click.argument('canonical_transcripts_file', type = click.Path(exists = True))
@click.argument('omim_file', type = click.Path(exists = True))
@click.argument('genenames_file', type = click.Path(exists = True))
@click.argument('gencode_file', type = click.Path(exists = True))
@with_appcontext
def load_genes(canonical_transcripts_file, omim_file, genenames_file, gencode_file):
   """ 
   Creates and populates the following collections: 'genes', 'transcripts', 'exons'.
   
   ARGUMENTS:

   canonical_transcripts_file -- file with a list of canonical transcripts. No header. Two columns: Ensebl gene ID, Ensembl transcript ID.

   omim_file -- file with genes descriptions from OMIM. Required columns separated by tab: Gene stable ID, Transcript stable ID, MIM gene accession, MIM gene description.

   genenames_file -- file with gene names from HGNC. Required columns separated by tab: symbol, name, alias_symbol, prev_name, ensembl_gene_id.

   gencode_file -- file from GENCODE in compressed GTF format.
   """
   mongo.db.genes.drop()
   mongo.db.transcripts.drop()
   mongo.db.exons.drop()
   
   canonical_transcripts = {read_canonical_transcripts(canonical_transcripts_file)}
   omim_annotations = {gene_id: (accession, description) for gene_id, transcrip_id, accession, description in read_omim(omim_file)}
   genenames = {gene_id: (gene_symbol, name, other_names) for gene_symbol, gene_id, name, other_names in read_hgnc(genenames_file)}
   for gene in read_gencode(gencode_file, ['gene']):
      gene_id = gene['gene_id']
      if gene_id in canonical_transcripts:
         gene['canonical_transcripts'] = canonical_transcripts[gene_id]
      if gene_id in omim_annotations:
         gene['omim_accession'] = omim_annotations[gene_id][0]
         gene['omim_description'] = omim_annotations[gene_id][1]
      if gene_id in genenames:
         gene['gene_name'] = genenames[gene_id][0]
         gene['full_gene_name'] = genenames[gene_id][1]
         gene['other_names'] = genenames[gene_id][2]
      mongo.db.genes.insert_one(gene)
   mongo.db.genes.create_indexes([pymongo.operations.IndexModel(key) for key in ['gene_id', 'gene_name', 'other_names', 'xstart', 'xstop']])
   sys.stdout.write(f"Created 'genes' collection and inserted {mongo.db.genes.count_documents({})} gene(s).\n")
   
   mongo.db.transcripts.insert_many(read_gencode(gencode_file, ['transcript']))
   mongo.db.transcripts.create_indexes([pymongo.operations.IndexModel(key) for key in ['transcript_id', 'gene_id']])
   sys.stdout.write(f"Created 'transcripts' collection and inserted {mongo.db.transcripts.count_documents({})} transcript(s).\n")
   
   mongo.db.exons.insert_many(read_gencode(gencode_file, ['exon', 'CDS', 'UTR']))
   mongo.db.exons.create_indexes([pymongo.operations.IndexModel(key) for key in ['exon_id', 'transcript_id', 'gene_id']])
   sys.stdout.write(f"Created 'exons' collection and inserted {mongo.db.exons.count_documents({})} exon(s).\n")


@click.command('load-sv')
@click.argument('variants_file', type = click.Path(exists = True))
@with_appcontext
def load_sv(variants_file):
   """ 
   Creates and populates 'sv' collection of structural variants.

   ARGUMENTS:   

   variants_file -- VCF/BCF file with structural variants.\n
   """
   mongo.db.sv.drop()
   for variant in read_sv(variants_file):
      mongo.db.sv.insert(variant)
   mongo.db.sv.create_indexes([pymongo.operations.IndexModel(key) for key in [ 'xpos', 'xstop' ]])
   sys.stdout.write(f"Created 'sv' collection and inserted {mongo.db.sv.count_documents({})} structural variant(s).\n")


def _load_snv(variants_file):
   _mongo = PyMongo(current_app) # for multiprocessing each thread needs its own client
   variants = read_snv(variants_file)
   for variant in variants:
      _mongo.db.snv.insert_many(chain([variant], islice(variants, 99999))) # insert in chunks of 100,000 variants


@click.command('load-snv')
@click.argument('threads', required = True, type = int)
@click.argument('variants_files', nargs = -1, required = True, type = click.Path(exists = True))
@with_appcontext
def load_snv(threads, variants_files):
   """ 
   Creates and populates 'snv' collection of single nucleotide variants and short indels.

   ARGUMENTS:   

   threads -- number of parallel threads to use.\n   

   variants_files -- one or several VCF/BCF files with single nucleotide variants and short indels.\n
   """

   mongo.db.snv.drop()
   with Pool(threads) as p:
      p.map(_load_snv, variants_files)
   mongo.db.snv.create_index([('xpos', pymongo.ASCENDING), ('xstop', pymongo.ASCENDING)])
   mongo.db.snv.create_index([('variant_id', pymongo.ASCENDING)])
   mongo.db.snv.create_index([('rsids', pymongo.ASCENDING)])
   sys.stdout.write(f"Created 'snv' collection and inserted {mongo.db.snv.count_documents({})} variant(s).\n")


@click.command('load-qc-metrics')
@click.argument('metrics_file', type = click.Path(exists = True))
def load_qc_metrics(metrics_file):
   """
   Creates and populates 'qc_metrics' collection of QC metrics caclulated across all variants.

   ARGUMENTS:

   metrics_file -- file with metrics. One metric per line in JSON format.
   """
   mongo.db.qc_metrics.drop()
   for metric in read_qc_metrics(metrics_file):
      mongo.db.qc_metrics.insert(metric)
   mongo.db.qc_metrics.create_index([('metric', pymongo.ASCENDING)])
   sys.stdout.write(f"Created 'qc_metrics' collection and inserted {mongo.db.qc_metrics.count_documents({})} QC metric(s).\n")
