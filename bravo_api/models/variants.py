from bravo_api.models.database import mongo
from bravo_api.models.utils import make_xpos
from flask import current_app
import pymongo
from bson.objectid import ObjectId
from bson.regex import Regex
import functools
from intervaltree import Interval, IntervalTree
from collections import Counter

import pprint # for debugging
import time # for debugging


new_filter_field_api2mongo = {
   'annotation.gene.lof': 'annotation.genes.lof',
   'annotation.gene.consequence': 'annotation.genes.consequence' 
}


field_mongo2api = {
   'xpos': 'pos',
   'xstop': 'stop',
   'annotation.region._lof': 'annotation.region.lof',
   'annotation.region._consequence': 'annotation.region.consequence',
   'annotation.genes._lof': 'annotation.gene.lof',
   'annotation.genes._consequence': 'annotation.gene.consequence' 
}


field_api2mongo = {
   'pos': 'xpos',
   'stop': 'xstop',
   'annotation.region.lof': 'annotation.region._lof',
   'annotation.region.consequence': 'annotation.region._consequence',
   'annotation.gene.lof': 'annotation.genes._lof',
   'annotation.gene.consequence': 'annotation.genes._consequence'
}


filter_values = [ 
   { 'value': 'PASS' }, 
   { 'value': 'SVM' },
   { 'value': 'DISC' }, 
   { 'value': 'EXHET'}
]


lof_values = [
   { 'value': 'HC' },
   { 'value': 'LC' }
]


consequence_values = [
   { 'value': 'transcript_ablation' },
   { 'value': 'splice_acceptor_variant' },
   { 'value': 'splice_donor_variant' },
   { 'value': 'stop_gained' },
   { 'value': 'frameshift_variant' },
   { 'value': 'stop_lost' },
   { 'value': 'start_lost' },
   { 'value': 'transcript_amplification' },
   { 'value': 'inframe_insertion' },
   { 'value': 'inframe_deletion' },
   { 'value': 'missense_variant' },
   { 'value': 'protein_altering_variant' },
   { 'value': 'splice_region_variant' },
   { 'value': 'incomplete_terminal_codon_variant' },
   { 'value': 'start_retained_variant' },
   { 'value': 'stop_retained_variant' },
   { 'value': 'synonymous_variant' },
   { 'value': 'coding_sequence_variant' },
   { 'value': 'mature_miRNA_variant' },
   { 'value': '5_prime_UTR_variant' },
   { 'value': '3_prime_UTR_variant' },
   { 'value': 'non_coding_transcript_exon_variant' },
   { 'value': 'intron_variant' },
   { 'value': 'NMD_transcript_variant' },
   { 'value': 'non_coding_transcript_variant' },
   { 'value': 'upstream_gene_variant' },
   { 'value': 'downstream_gene_variant' },
   { 'value': 'TFBS_ablation' },
   { 'value': 'TFBS_amplification' },
   { 'value': 'TF_binding_site_variant' },
   { 'value': 'regulatory_region_ablation' },
   { 'value': 'regulatory_region_amplification' },
   { 'value': 'feature_elongation' },
   { 'value': 'regulatory_region_variant' },
   { 'value': 'feature_truncation' },
   { 'value': 'intergenic_variant' }
]


def build_mongo_filter(user_filter): 
   def expand_and_condition(field, condition):
      # field, { '$eq': [1, 2], '$ne': [3] } => { $and: [ {field: { $eq: 1}}, {field: {$eq: 2}}, {field: {$neq: 3}} ] }
      expressions = []
      for operator, values in condition.items():
         for value in values:
            expressions.append({ field: { operator : value }})
      return { '$and': expressions }

   def flatten(names, field):
      if isinstance(field, dict):
         if field:
            for key, field in field.items():
               flatten(names + [key], field)
         else:
            flatten.result.append(('.'.join(names), []))
      else:
         flatten.result.append(('.'.join(names), field))

   mongo_filter = []
   for field, values in user_filter.items():
      flatten.result = []
      flatten([field], values)
      for field, values in flatten.result:
         if len(values) == 0:
            continue
         print('--> ', field, values)
         mongo_filter.append({'$or': [ expand_and_condition(new_filter_field_api2mongo.get(field, field), v) for v in values ]})
   return mongo_filter


def adjust_mongo_filter(mongo_filter, mongo_sort, last):
   mongo_last_filter = [ { '_id': {'$gt': ObjectId(last['_id'])}} ]
   for key, direction in mongo_sort:
      if direction == pymongo.ASCENDING or direction == 'asc':
         mongo_filter.append({key: {'$gte': last[key]}})
         mongo_last_filter.append({key: {'$gt': last[key]}})
      else:
         mongo_filter.append({key: {'$lte': last[key]}})
         mongo_last_filter.append({key: {'$lt': last[key]}})
   mongo_filter.append({'$or': mongo_last_filter})


def adjust_mongo_filter2(mongo_filter, mongo_sort, last, gene_name):
   mongo_last_filter = [ { '_id': {'$gt': ObjectId(last['_id'])}} ]
   for key, direction in mongo_sort:
      if direction == pymongo.ASCENDING or direction == 'asc':
         if key.startswith('annotation.genes.'):
            mongo_filter.append({'annotation.genes':{'$elemMatch':
               {'$and': [{'name':{'$eq':gene_name}},{key.split('.')[-1]:{'$gte': last[key]}}]}
            }})
            mongo_last_filter.append({'annotation.genes':{'$elemMatch':
               {'$and': [{'name':{'$eq':gene_name}},{key.split('.')[-1]:{'$gt': last[key]}}]}
            }})
         else:
            mongo_filter.append({key: {'$gte': last[key]}})
            mongo_last_filter.append({key: {'$gt': last[key]}})
      else:
         if key.startswith('annotation.genes.'):
            mongo_filter.append({'annotation.genes':{'$elemMatch':
               {'$and': [{'name':{'$eq':gene_name}},{key.split('.')[-1]:{'$lte': last[key]}}]}
            }})
            mongo_last_filter.append({'annotation.genes':{'$elemMatch':
               {'$and': [{'name':{'$eq':gene_name}},{key.split('.')[-1]:{'$lt': last[key]}}]}
            }})
         else:
            mongo_filter.append({key: {'$lte': last[key]}})
            mongo_last_filter.append({key: {'$lt': last[key]}})
   mongo_filter.append({'$or': mongo_last_filter})


def get_snv(variant_id, chrom, position):   
   result = {
      'limit': None,
      'total': 0,
      'data': [],
      'sort': None,
      'last': None
   }

   if variant_id is not None:
      mongo_filter = [ { 'variant_id': variant_id } ]
   elif chrom is not None and position is not None:
      xpos = make_xpos(chrom, position)
      mongo_filter = [ {'xpos': xpos} ]
   else:
      return result

   projection = {
      '_id': False,
      'variant_id': True,
      'rsids': True,
      'chrom': True, 'pos': True, 'stop': True,
      'ref': True, 'alt': True,
      'site_quality': True, 'filter': True,
      'cadd_phred': True,
      'allele_num': True, 'allele_count': True, 'allele_freq': True,
      'hom_count': True, 'het_count': True,
      'annotation': True,
      'qc_metrics': True,
      'avg_dp': True, 'avg_dp_alt': True,
      'avg_gq': True, 'avg_gq_alt': True,
      'dp_hist': True, 'dp_hist_alt': True,
      'gq_hist': True, 'gq_hist_alt': True,
      'pub_freq': True
   }

   pipeline = [
      { '$match': { '$and': mongo_filter }},
      { '$project': projection }
   ]

   #pprint.PrettyPrinter(indent=1).pprint(mongo.db.command('aggregate', 'snv', pipeline = pipeline, explain = True))

   #st = time.time()
   cursor = mongo.db.snv.aggregate(pipeline)
   #print(time.time() - st)
   for entry in cursor:
      result['data'].append(entry)
   result['total'] = len(result['data'])
   return result


def get_region(chrom, start, stop, filter, sort, last, limit):
   xstart = make_xpos(chrom, start)
   xstop = make_xpos(chrom, stop)

   # prepare user-specified filter conditions in mongo format 
   mongo_filter = [ {'xpos': { '$lte': xstop }}, {'xstop': {'$gte': xstart}} ]
   mongo_filter.extend(build_mongo_filter(filter))
  
   n_total_documents = mongo.db.sv.count_documents({ '$and': mongo_filter })

   # prepare sort conditions in mongo format
   mongo_sort = [('x' + key if key in {'pos', 'stop'} else key, pymongo.ASCENDING if direction == 'asc' else pymongo.DESCENDING) for key, direction in sort]
   if len(mongo_sort) == 0: # xpos sorted by default if nothing else is specified
      mongo_sort = [ ('xpos', pymongo.ASCENDING) ]
   
   # adjust filter if auto-generated 'last' field is present.
   # mongodb optimizer will take care of overlapping conditions
   if last:
      adjust_mongo_filter(mongo_filter, mongo_sort, last)

   result = { 
      'limit': limit, 
      'total': n_total_documents, 
      'data': [],
      'sort': [('pos', 'asc')] if len(sort) == 0 else sort[:],
      'last': None
   }
   cursor = mongo.db.sv.find({ '$and': mongo_filter }).sort(mongo_sort + [('_id', pymongo.ASCENDING)]).limit(limit)
   for entry in cursor:
      last_object_id = entry.pop('_id')
      last_variant = entry
      entry.pop('xpos')
      entry.pop('xstop')
      result['data'].append(entry)

   if len(result['data']) == limit:
      result['last'] = ''
      for key, direction in mongo_sort:
         key = field_mongo2api.get(key, key)
         if key == 'pos' or key == 'stop':
            result['last'] += f'{key}:{str(make_xpos(last_variant["chrom"], last_variant[key]))},'
         else:
            result['last'] += f'{key}:{last_variant[key]},'
         result['last'] += f'_id:{last_object_id}'
      
   return result


def get_region_snv(chrom, start, stop, filter, sort, last, limit):
   xstart = make_xpos(chrom, start)
   xstop = make_xpos(chrom, stop)

   # prepare user-specified filter conditions in mongo format
   # query optimizer didn't work well on Mongo 3.4 and {'xpos': { '$lte': xstop }}, {'xstop': {'$gte': xstart}} filter wasn't performing well
   # since here we work with short variants, to improve performance we add additional limits to xpos and xstop 
   mongo_filter = [ {'xpos': {'$gte': xstart - 1000}}, {'xpos': { '$lte': xstop }}, {'xstop': {'$gte': xstart}}, {'xstop': {'$lte': xstop + 1000}} ]
   mongo_filter.extend(build_mongo_filter(filter))

   #print('mongo_filter = ', mongo_filter)
 
   st = time.time()
   n_total_documents = mongo.db.snv.count_documents({ '$and': mongo_filter })
   print('n_total_documents = ', n_total_documents, time.time() - st)

   mongo_sort = []
   for key, direction in sort:
      mongo_key = field_api2mongo.get(key, key)
      mongo_direction = pymongo.ASCENDING if direction == 'asc' else pymongo.DESCENDING
      mongo_sort.append((mongo_key, mongo_direction))         
   if len(mongo_sort) == 0: # xpos sorted by default if nothing else is specified
      mongo_sort = [ ('xpos', pymongo.ASCENDING) ]

   # adjust filter if auto-generated 'last' field is present
   # mongodb optimizer will take care of overlapping conditions
   if last:
      adjust_mongo_filter(mongo_filter, mongo_sort, last)

   #print('adj mongo_filter = ', mongo_filter)

   result = { 
      'limit': limit, 
      'total': n_total_documents, 
      'data': [],
      'sort': [('pos', 'asc')] if len(sort) == 0 else sort[:],
      'last': None
   }
 
   projection = {
      '_id': True, 
      'variant_id': True,
      'chrom': True, 'pos': True, 'stop': True, 
      'ref': True, 'alt': True,
      'site_quality': True, 'filter': True,
      'cadd_phred': True,
      'allele_num': True, 'allele_count': True, 'allele_freq': True,
      'hom_count': True, 'het_count': True,
      'annotation': True
   }
  
   pipeline = [
      { '$match': { '$and': mongo_filter }},
      { '$sort': { key: value for  key, value in mongo_sort + [('_id', pymongo.ASCENDING)] }},
      { '$project': projection },
      { '$limit': limit }
   ]

   #print("mongo_filter = ", mongo_filter)
   #pprint.PrettyPrinter(indent=1).pprint(mongo.db.command('aggregate', 'snv', pipeline = pipeline, explain = True))

   st = time.time()
   cursor = mongo.db.snv.aggregate(pipeline, allowDiskUse = True, hint = 'xpos_1_xstop_1')
   print('Query time = ', time.time() - st)
   for entry in cursor:
      last_object_id = entry.pop('_id')
      last_variant = entry
      result['data'].append(entry)
   if len(result['data']) == limit:
      result['last'] = { '_id': f'{last_object_id}'  }
      for key, direction in mongo_sort:
         if key == 'xpos' or key == 'xstop':
            result['last'][key] = make_xpos(last_variant['chrom'], last_variant[key[1:]])
         else:
            result['last'][key] = functools.reduce(lambda d, v: d.get(v, None), key.split('.'), last_variant)
   return result


def get_snv_filters():
   # this should be stored somewhere in database and generated during the data import step
   return {
      'filter': filter_values, 
      'lof': lof_values,
      'consequence': consequence_values    
   }


def get_genes(name, full):
   #TODO: add other_names (need to use aggregae https://stackoverflow.com/questions/28889240/mongodb-sort-documents-by-array-elements
   pattern = Regex('^' + name, 'i')
   if name.startswith('ENSG'):
      mongo_filter = { 'gene_id': pattern }
      mongo_sort = { 'gene_id': pymongo.ASCENDING }
   else:
      mongo_filter = { 'gene_name': pattern }
      mongo_sort = { 'gene_name': pymongo.ASCENDING }
   pipeline = [
      { '$match': mongo_filter },
      { '$project': {'_id': 0, 'xstart': 0, 'xstop': 0} },
      { '$sort': mongo_sort },
      { '$limit': 10 }
   ]
   if full:
      pipeline.append({'$lookup': {
         'from': 'transcripts',
         'localField': 'gene_id',
         'foreignField': 'gene_id',
         'as': 'transcripts'
      }})
      pipeline.append({'$project': {'transcripts._id': 0, 'transcripts.chrom': 0, 'transcripts.xstart': 0, 'transcripts.xstop': 0, 'transcripts.gene_id': 0 }})
      pipeline.append({'$lookup': { 
         'from': 'exons',
         'localField': 'gene_id',
         'foreignField': 'gene_id',
         'as': 'features'
      }})
      pipeline.append({'$project': {'features._id': 0, 'features.chrom': 0, 'features.xstart': 0, 'features.xstop': 0, 'features.gene_id': 0 }})
   cursor = mongo.db.genes.aggregate(pipeline) 
   for entry in cursor:
      yield entry


def get_genes_in_region(chrom, start, stop, full = False):
   xstart = make_xpos(chrom, start)
   xstop = make_xpos(chrom, stop)
   pipeline = []
   pipeline.append({'$match': {'$and': [{'xstart': { '$lte': xstop }}, {'xstop': {'$gte': xstart}}]}})
   pipeline.append({'$project': {'_id': 0, 'xstart': 0, 'xstop': 0, 'transcripts._id': 0}}) 
   if full:
      pipeline.append({'$lookup': {
         'from': 'transcripts',
         'localField': 'gene_id',
         'foreignField': 'gene_id',
         'as': 'transcripts'
      }})
      pipeline.append({'$project': {'transcripts._id': 0, 'transcripts.chrom': 0, 'transcripts.xstart': 0, 'transcripts.xstop': 0, 'transcripts.gene_id': 0 }})
      pipeline.append({'$lookup': { 
         'from': 'exons',
         'localField': 'gene_id',
         'foreignField': 'gene_id',
         'as': 'features'
      }})
      pipeline.append({'$project': {'features._id': 0, 'features.chrom': 0, 'features.xstart': 0, 'features.xstop': 0, 'features.gene_id': 0 }})
   cursor = mongo.db.genes.aggregate(pipeline)
   for entry in cursor:
      yield entry


def get_gene(name, full):
   for entry in get_genes(name, full):
      if name.startswith('ENSG'):
         if name == entry['gene_id']:
            return entry
      elif name == entry['gene_name']:
         return entry


def get_gene_snv(name, filter, sort, last, limit, introns):
   gene = None
   result = { 
      'limit': limit, 
      'total': 0, 
      'data': [],
      'sort': [('pos', 'asc')] if len(sort) == 0 else sort[:],
      'last': None
   }
   gene = get_gene(name, not introns)
   if gene is None:
      return result        

   if not introns:
      exons = IntervalTree()
      for feature in gene['features']:
         if feature['feature_type'] == 'exon':
            exons.addi(feature['start'], feature['stop'] + 1)
      mongo_exons_filter = []
      exons.merge_overlaps()
      for exon in exons:
         mongo_exons_filter.append({'pos': {'$gte': exon.begin, '$lt': exon.end}})

   gene_id = gene['gene_id']
   xstart = make_xpos(gene['chrom'], gene['start'])
   xstop = make_xpos(gene['chrom'], gene['stop'])

   # prepare user-specified filter conditions in mongo format
   # query optimizer didn't work well on Mongo 3.4 and {'xpos': { '$lte': xstop }}, {'xstop': {'$gte': xstart}} filter wasn't performing well
   # since here we work with short variants, to improve performance we add additional limits to xpos and xstop 
   mongo_filter = [ {'xpos': {'$gte': xstart - 1000}}, {'xpos': { '$lte': xstop }}, {'xstop': {'$gte': xstart}}, {'xstop': {'$lte': xstop + 1000}} ]
   mongo_filter.extend(build_mongo_filter(filter))
   
   for f in mongo_filter:
      for condition in f.get('$or', []):
         if all('annotation.genes.lof' in x for x in condition['$and']):
            new_expression = {'annotation.genes': {'$elemMatch': { '$and': [ {'name': {'$eq': gene_id}} ]}}}
            for item in condition['$and']:
               new_expression['annotation.genes']['$elemMatch']['$and'].append({ 'lof': item['annotation.genes.lof'] }) 
            condition.pop('$and')
            condition.update(new_expression)
         elif all('annotation.genes.consequence' in x for x in condition['$and']):
            new_expression = {'annotation.genes': {'$elemMatch': { '$and': [ {'name': {'$eq': gene_id}} ]}}}
            for item in condition['$and']:
               new_expression['annotation.genes']['$elemMatch']['$and'].append({ 'consequence': item['annotation.genes.consequence'] }) 
            condition.pop('$and')
            condition.update(new_expression) 

   
   st = time.time()
   result['total'] = mongo.db.snv.count_documents({ '$and': mongo_filter } if introns else { '$and': mongo_filter, '$or': mongo_exons_filter })
   print('n_total_documents = ', result['total'], time.time() - st)

   mongo_sort = []
   for key, direction in sort:
      mongo_key = field_api2mongo.get(key, key)
      mongo_direction = pymongo.ASCENDING if direction == 'asc' else pymongo.DESCENDING
      mongo_sort.append((mongo_key, mongo_direction))         
   if len(mongo_sort) == 0: # xpos sorted by default if nothing else is specified
      mongo_sort = [ ('xpos', pymongo.ASCENDING) ]

   # adjust filter if auto-generated 'last' field is present
   # mongodb optimizer will take care of overlapping conditions
   if last:
      adjust_mongo_filter2(mongo_filter, mongo_sort, last, gene_id)
 
   projection = {
      '_id': True, 
      'xpos': True, # need this here, because can't move sort before projection
      'xstop': True, # need this here, because can't move sort before projection
      'variant_id': True,
      'chrom': True, 'pos': True, 'stop': True, 
      'ref': True, 'alt': True,
      'site_quality': True, 'filter': True,
      'cadd_phred': True,
      'allele_num': True, 'allele_count': True, 'allele_freq': True,
      'hom_count': True, 'het_count': True,
      #'annotation.genes': True
      'annotation.genes': {
         '$filter': {
            'input': '$annotation.genes',
            'cond': { '$eq': ( '$$this.name', gene_id ) }
         }
      }
   }

   pipeline = [
      #{ '$unwind': '$annotation.genes' },
      { '$match': { '$and': mongo_filter }} 
   ]
   if not introns:
      pipeline.extend([
         { '$match': { '$or': mongo_exons_filter }}
      ])
   pipeline.extend([
      { '$project': projection },
      { '$sort': { key: value for  key, value in mongo_sort + [('_id', pymongo.ASCENDING)] }},
      { '$limit': limit }
   ])

   #pprint.PrettyPrinter(indent=1).pprint(mongo.db.command('aggregate', 'snv', pipeline = pipeline, explain = True))

   st = time.time()
   cursor = mongo.db.snv.aggregate(pipeline, allowDiskUse = True, hint = 'xpos_1_xstop_1')
   print('Query time = ', time.time() - st)
   for i, entry in enumerate(cursor, 1):
      if i == limit:
         result['last'] = {'_id': f'{entry["_id"]}'}
         for key, direction in mongo_sort:
            if key == 'xpos' or key == 'xstop':
               result['last'][key] = make_xpos(entry['chrom'], entry[key[1:]])
            else:
               result['last'][key] = functools.reduce(lambda d, v: d[0].get(v, None) if isinstance(d, list) else d.get(v, None), key.split('.'), entry)
               #result['last'][key] = functools.reduce(lambda d, v: d.get(v, None), key.split('.'), entry)
      entry.pop('_id')
      entry.pop('xpos')
      entry.pop('xstop')
      genes = entry['annotation'].pop('genes') # array to single element. alternative - use unwind in mongo pipeline 
      entry['annotation']['gene'] = genes[0]
      result['data'].append(entry)   
   return result


def get_region_snv_histogram(chrom, start, stop, filter, windows):
   xstart = make_xpos(chrom, start)
   xstop = make_xpos(chrom, stop)

   window_size = (stop - start + 1) // windows
   window_size += min((stop - start + 1) % windows, 1)

   # prepare user-specified filter conditions in mongo format
   # query optimizer didn't work well on Mongo 3.4 and {'xpos': { '$lte': xstop }}, {'xstop': {'$gte': xstart}} filter wasn't performing well
   # since here we work with short variants, to improve performance we add additional limits to xpos and xstop 
   mongo_filter = [ {'xpos': {'$gte': xstart - 1000}}, {'xpos': { '$lte': xstop }}, {'xstop': {'$gte': xstart}}, {'xstop': {'$lte': xstop + 1000}} ]
   mongo_filter.extend(build_mongo_filter(filter))

   pipeline = [
      { '$match': { '$and': mongo_filter }},
      { '$project': { 'pos': True }},
      { '$group' : {  '_id': { '$floor': { '$divide': [ '$pos', window_size ] }}, 'count': { '$sum': 1  }   } },
      { '$project' : { '_id': False, 'start': {'$trunc': { '$multiply': [ '$_id', window_size ] }}, 'count': True  }}
   ]

   #pprint.PrettyPrinter(indent=1).pprint(mongo.db.command('aggregate', 'snv', pipeline = pipeline, explain = True))

   data = {
      'chrom': chrom,
      'window-size': window_size,
      'windows': []
   }
   st = time.time()
   cursor = mongo.db.snv.aggregate(pipeline, hint = 'xpos_1_xstop_1')
   print('Histogram query time = ', time.time() - st)
   for entry in cursor:
      data['windows'].append(entry)
   return data


def get_region_snv_summary(chrom, start, stop):
   xstart = make_xpos(chrom, start)
   xstop = make_xpos(chrom, stop)

   # prepare user-specified filter conditions in mongo format
   # query optimizer didn't work well on Mongo 3.4 and {'xpos': { '$lte': xstop }}, {'xstop': {'$gte': xstart}} filter wasn't performing well
   # since here we work with short variants, to improve performance we add additional limits to xpos and xstop 
   mongo_filter = [ {'xpos': {'$gte': xstart - 1000}}, {'xpos': { '$lte': xstop }}, {'xstop': {'$gte': xstart}}, {'xstop': {'$lte': xstop + 1000}} ]

   pipeline = [
      { '$match': { '$and': mongo_filter }},
      { '$project': { '_id': False, 'variant_id': True, 'filter': True, 'annotation.region.consequence': True, 'annotation.region.lof': True }}
   ]   
   data = {
      'all': Counter(),
      'passed': Counter(),
      'failed': Counter()
   }
   cursor = mongo.db.snv.aggregate(pipeline, hint = 'xpos_1_xstop_1')
   for entry in cursor:
      chrom, position, ref, alt = entry['variant_id'].split('-')
      data['all']['total'] += 1
      if 'PASS' in entry['filter']:
         filter = 'passed'
      else:
         filter = 'failed'
      data[filter]['total'] += 1
      if len(ref) == 1 and len(alt) == 1:
         data['all']['snv'] += 1
         data[filter]['snv'] += 1
      elif len(ref) != len(alt):
         data['all']['indels'] += 1
         data[filter]['indels'] += 1
      if 'lof' in entry['annotation']['region']:
         data['all'][f'LoF ({entry["annotation"]["region"]["lof"][0]})'] += 1
         data[filter][f'LoF ({entry["annotation"]["region"]["lof"][0]})'] += 1
      if entry['annotation']['region']['consequence']:
         data['all'][entry['annotation']['region']['consequence'][0]] += 1
         data[filter][entry['annotation']['region']['consequence'][0]] += 1
   return data


def get_gene_snv_summary(name):
   gene = None
   data = {
      'all': Counter(),
      'passed': Counter(),
      'failed': Counter()
   }
   gene = get_gene(name, True)
   if gene is None:
      return data
   gene_id = gene['gene_id']
   xstart = make_xpos(gene['chrom'], gene['start'])
   xstop = make_xpos(gene['chrom'], gene['stop'])

   mongo_filter = [ {'xpos': {'$gte': xstart - 1000}}, {'xpos': { '$lte': xstop }}, {'xstop': {'$gte': xstart}}, {'xstop': {'$lte': xstop + 1000}} ]
   projection = {
      '_id': False, 
      'variant_id': True,
      'filter': True,
      'annotation.genes': {
         '$filter': {
            'input': '$annotation.genes',
            'cond': { '$eq': ( '$$this.name', gene_id ) }
         }
      }
   }

   pipeline = [
      { '$match': { '$and': mongo_filter }},
      { '$project': projection }
   ]

   cursor = mongo.db.snv.aggregate(pipeline, hint = 'xpos_1_xstop_1')
   for entry in cursor:
      chrom, position, ref, alt = entry['variant_id'].split('-')
      data['all']['total'] += 1
      if 'PASS' in entry['filter']:
         filter = 'passed'
      else:
         filter = 'failed'
      data[filter]['total'] += 1
      if len(ref) == 1 and len(alt) == 1:
         data['all']['snv'] += 1
         data[filter]['snv'] += 1
      elif len(ref) != len(alt):
         data['all']['indels'] += 1
         data[filter]['indels'] += 1
      if 'lof' in entry['annotation']['genes'][0]:
         data['all'][f'LoF ({entry["annotation"]["genes"][0]["lof"][0]})'] += 1
         data[filter][f'LoF ({entry["annotation"]["genes"][0]["lof"][0]})'] += 1
      if entry['annotation']['genes'][0]['consequence']:
         data['all'][entry['annotation']['genes'][0]['consequence'][0]] += 1
         data[filter][entry['annotation']['genes'][0]['consequence'][0]] += 1
   return data


def get_gene_snv_histogram(name, filter, windows, introns):
   gene = None
   result = { 
      'gene_id': None,
      'window-size': None,
      'windows': []
   }
   gene = get_gene(name, not introns)
   if gene is None:
      return result        

   if not introns:
      exons = IntervalTree()
      for feature in gene['features']:
         if feature['feature_type'] == 'exon':
            exons.addi(feature['start'], feature['stop'] + 1)
      mongo_exons_filter = []
      exon_length = 0
      exons.merge_overlaps()
      for exon in exons:
         mongo_exons_filter.append({'pos': {'$gte': exon.begin, '$lt': exon.end}})
         exon_length += exon.end - exon.begin

   gene_id = gene['gene_id']
   xstart = make_xpos(gene['chrom'], gene['start'])
   xstop = make_xpos(gene['chrom'], gene['stop'])

   if not introns:
      window_size = exon_length // windows
      window_size += min(exon_length % windows, 1)
   else:
      window_size = (xstop - xstart + 1) // windows
      window_size += min((xstop - xstart + 1) % windows, 1)

   # prepare user-specified filter conditions in mongo format
   # query optimizer didn't work well on Mongo 3.4 and {'xpos': { '$lte': xstop }}, {'xstop': {'$gte': xstart}} filter wasn't performing well
   # since here we work with short variants, to improve performance we add additional limits to xpos and xstop 
   mongo_filter = [ {'xpos': {'$gte': xstart - 1000}}, {'xpos': { '$lte': xstop }}, {'xstop': {'$gte': xstart}}, {'xstop': {'$lte': xstop + 1000}} ]
   mongo_filter.extend(build_mongo_filter(filter))
   
   for f in mongo_filter:
      for condition in f.get('$or', []):
         if all('annotation.genes.lof' in x for x in condition['$and']):
            new_expression = {'annotation.genes': {'$elemMatch': { '$and': [ {'name': {'$eq': gene_id}} ]}}}
            for item in condition['$and']:
               new_expression['annotation.genes']['$elemMatch']['$and'].append({ 'lof': item['annotation.genes.lof'] }) 
            condition.pop('$and')
            condition.update(new_expression)
         elif all('annotation.genes.consequence' in x for x in condition['$and']):
            new_expression = {'annotation.genes': {'$elemMatch': { '$and': [ {'name': {'$eq': gene_id}} ]}}}
            for item in condition['$and']:
               new_expression['annotation.genes']['$elemMatch']['$and'].append({ 'consequence': item['annotation.genes.consequence'] }) 
            condition.pop('$and')
            condition.update(new_expression) 

   pipeline = [
      { '$match': { '$and': mongo_filter }}
   ]
   if not introns:
      pipeline.extend([{ '$match': { '$or': mongo_exons_filter}}])
   pipeline.extend([
      { '$project': { 'pos': True }},
      { '$group' : {  '_id': { '$floor': { '$divide': [ '$pos', window_size ] }}, 'count': { '$sum': 1  }   } },
      { '$project' : { '_id': False, 'start': {'$trunc': { '$multiply': [ '$_id', window_size ] }}, 'count': True  }}
   ])
 
   result['gene_id'] = gene_id
   result['window-size'] = window_size

   st = time.time()
   cursor = mongo.db.snv.aggregate(pipeline, hint = 'xpos_1_xstop_1')
   print('Histogram query time = ', time.time() - st)
   for entry in cursor:
      result['windows'].append(entry)
   return result 
