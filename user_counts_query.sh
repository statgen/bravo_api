#!/usr/bin/env bash

# Monthly estimate of users report for BRAVO
# Query the mongo database of bravo installations for user counts
# Requires jq and mongo cli
# 
# To avoid having this script live on the prod machine,
# use ssh tunneling to forward ports to local machine then run this script.
#   ssh -fN -L 29019:localhost:27017 bravo-prod
#
# Alternatively, if run from the prod machine, set the port back 
# to the default mongo port.
#   REPORT_PORT=27017; ./user_counts_query.sh

REPORT_PORT="${REPORT_PORT:-29019}"

# Define mongo commands to run queries
F5_MONGO_CMD="mongo --port ${REPORT_PORT} topmed_freeze5_hg38 --quiet --eval"
F8_MONGO_CMD="mongo --port ${REPORT_PORT} topmed_freeze8_hg38_browser --quiet --eval"

# Calculate start and end dates for previous month
CURR_MONTH_START=$(date +%Y-%m)-01
PREV_MONTH_START=$(date --date="${CURR_MONTH_START} - 1 month" +%Y-%m-%d)

##################
# Define Queries #
##################
# Uses datetime component of BSON _id creation to determine when user created.

# Count new users in previous month
read -r -d '' NEW_COUNT_Q <<- EOF
db.users.find(
  {_id: { \$lt: ObjectId.fromDate(ISODate('${CURR_MONTH_START}')),
          \$gte: ObjectId.fromDate(ISODate('${PREV_MONTH_START}')) }
  }
).count()
EOF

# Count total users at beginning of current month
read -r -d '' ALL_COUNT_Q <<- EOF
db.users.find(
  {_id: {\$lt: ObjectId.fromDate(ISODate('${CURR_MONTH_START}'))}}
).count()
EOF

# List of all user ids
read -r -d '' ALL_IDS <<- EOF
db.users.find(
  {_id: {\$lt: ObjectId.fromDate(ISODate('${CURR_MONTH_START}'))} },
  {user_id: 1, _id: 0}
).toArray()
EOF

######################
# Check Dependencies #
######################

# Verify jq is installed.
command -v jq 1> /dev/null 2>&1 || \
  { echo >&2 "jq required but it's not installed.  Aborting."; exit 1; }

# Verify jq is installed.
command -v mongo --version 1> /dev/null 2>&1 || \
  { echo >&2 "mongo required but it's not installed.  Aborting."; exit 1; }

# Check if mongo is reachable
${F8_MONGO_CMD} "db.version()" > /dev/null
if [ $? -ne 0 ]
then
  echo "Mongodb not reacahble on port $REPORT_PORT"
  exit 1
fi

###############
# Run Queries #
###############
# Run new user in prev month queries
F5_NEW_CNT=$(${F5_MONGO_CMD} "$NEW_COUNT_Q")
F8_NEW_CNT=$(${F8_MONGO_CMD} "$NEW_COUNT_Q")

# Get list of user ids from both freeze 5 & 8
readarray -t F5_USERS < <(
  ${F5_MONGO_CMD} "$ALL_IDS" |\
  jq -c -r '[.[] | .user_id] | .[]'
)

readarray -t F8_USERS < <(
  ${F8_MONGO_CMD} "$ALL_IDS" |\
  jq -c -r '[.[] | .user_id] | .[]'
)

ALL_USERS=(${F5_USERS[@]} ${F8_USERS[@]})
UNIQUE_IDS=($(echo "${ALL_USERS[@]}" | tr ' ' '\n' | sort -u))

# Get counts
F5_USER_CNT="${#F5_USERS[@]}"
F8_USER_CNT="${#F8_USERS[@]}"
UNIQUE_CNT="${#UNIQUE_IDS[@]}"

##########
# Report #
##########
echo "----------------------"
echo "Between ${PREV_MONTH_START} and ${CURR_MONTH_START}"
echo "----------------------"
echo "BRAVO Freeze5 Instance"
echo "----------------------"
echo "New Users:   ${F5_NEW_CNT}"
echo "Total Users: ${F5_USER_CNT}" 
echo "----------------------"
echo "BRAVO Freeze8 Instance"
echo "----------------------"
echo "New Users:   ${F8_NEW_CNT}"
echo "Total Users: ${F8_USER_CNT}" 
echo "----------------------------------"
echo "BRAVO Freeze 5 & 8 Unique Combined"
echo "----------------------------------"
echo "Unique Users: ${UNIQUE_CNT}" 
