#!/usr/bin/env bash

# Point to config file and data directory
export FLASK_APP=bravo_api
export BRAVO_API_CONFIG_FILE='/mnt/bravo/instance/config.py'
BASE_DIR='/mnt/bravo/data'
METRICS_FILE="${BASE_DIR}/basis/qc_metrics/metrics.json.gz"

# Order of basis files matters as it matches the args of 
#  load_genes(canonical_transcripts_file, omim_file, genenames_file, gencode_file)
BASIS_FILES=(\
  "${BASE_DIR}/basis/reference/canonical_transcripts.tsv.gz" \
  "${BASE_DIR}/basis/reference/omim_ensembl_refs.tsv.gz" \
  "${BASE_DIR}/basis/reference/hgcn_genenames.tsv.gz" \
  "${BASE_DIR}/basis/reference/gencode.v38.annotation.gtf.gz" )

########################################################
# Verify Exists: Config, References, VCFs, and Metrics #
########################################################
if [ ! -f "${BRAVO_API_CONFIG_FILE}" ]; then
  echo "BRAVO config not found at: ${BRAVO_API_CONFIG_FILE}"
  exit 1
fi

for FILE in ${BASIS_FILES[@]}; do
  if [ ! -f ${FILE} ]; then
    echo "Basis reference: ${FILE} not found. Exiting."
    exit 1
  fi
done

VCF_COUNT=$(ls -A ${BASE_DIR}/basis/vcfs/*.vcf.gz | wc -l)
if [ $VCF_COUNT -lt 1 ]; then
  echo "Found ${VCF_COUNT} VCFS at ${BASE_DIR}/basis/vcfs. Exiting."
  exit 1
fi

if [ ! -f "${METRICS_FILE}" ]; then
    echo "Metrics: ${METRICS_FILE} not found. Exiting."
    exit 1
fi

#############
# Load Data #
#############
echo "flask load-genes ${BASIS_FILES[@]}"
flask load-genes ${BASIS_FILES[@]}
 
flask load-snv 2 ${BASE_DIR}/basis/vcfs/*.vcf.gz

echo "flask load-qc-metrics ${METRICS_FILE}"
flask load-qc-metrics "${METRICS_FILE}"
