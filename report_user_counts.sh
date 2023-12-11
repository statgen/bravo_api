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
#   REPORT_PORT=27017; ./report_user_counts.sh

REPORT_PORT="${REPORT_PORT:-29019}"

# Define mongo commands to run queries
F5_MONGO_CMD="mongosh --port ${REPORT_PORT} topmed_freeze5_hg38 --quiet --eval"
F8_MONGO_CMD="mongosh --port ${REPORT_PORT} topmed_freeze8_hg38_browser --quiet --eval"

# Calculate start and end dates for previous month
CURR_MONTH_START=$(date +%Y-%m)-01
PREV_MONTH_START=$(date --date="${CURR_MONTH_START} - 1 month" +%Y-%m-%d)

# ObjectId.fromDate() is no longer available.  Calc the ObjectId in bash.
# Taken from https://ervinbarta.com/2019/04/08/mongodb-magic/

# Convert dates to seconds
CURR_MONTH_SEC=$(date --date=${CURR_MONTH_START} +%s)
PREV_MONTH_SEC=$(date --date=${PREV_MONTH_START} +%s)

# Convert seconds to hex
CURR_MONTH_HEX=$(printf "%x" ${CURR_MONTH_SEC})
PREV_MONTH_HEX=$(printf "%x" ${PREV_MONTH_SEC})

# Append 0's to make ObjectId
CURR_MONTH_OBJID="${CURR_MONTH_HEX}0000000000000000"
PREV_MONTH_OBJID="${PREV_MONTH_HEX}0000000000000000"


##################
# Define Queries #
##################
# Uses datetime component of BSON _id creation to determine when user created.
# Count new users in previous month
read -r -d '' NEW_COUNT_Q <<- EOF
db.users.find(
  {_id: { \$lt: ObjectId('${CURR_MONTH_OBJID}'),
          \$gte: ObjectId('${PREV_MONTH_OBJID}') }
  }
).count()
EOF

# Count total users at beginning of current month
read -r -d '' ALL_COUNT_Q <<- EOF
db.users.find(
  {_id: {\$lt: ObjectId('${CURR_MONTH_OBJID}')}}
).count()
EOF

# List of all user ids
# Stringify to avoid util.inspect max array length truncating output
read -r -d '' ALL_IDS <<- EOF
let result = db.users.find(
  {_id: {\$lt: ObjectId("${CURR_MONTH_OBJID}")} },
  {user_id: true, _id: false}
).toArray()
JSON.stringify(result)
EOF


######################
# Check Dependencies #
######################

# Verify jq is installed.
command -v jq 1> /dev/null 2>&1 || \
  { echo >&2 "jq required but it's not installed.  Aborting."; exit 1; }

# Verify jq is installed.
command -v mongosh --version 1> /dev/null 2>&1 || \
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
