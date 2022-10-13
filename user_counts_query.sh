#!/usr/bin/env bash

# Monthly estimate of users report for BRAVO
# Query the mongo database of bravo installations for user counts
# 
# To avoid having this script live on the prod machine,
# use ssh tunneling to forward ports to local machine then run this script.
#   ssh -fN -L 29019:localhost:27017 bravo-prod
#
# Alternatively, if run from the prod machine, set the port back 
# to the default mongo port.
#   REPORT_PORT=27017; ./user_counts_query.sh


REPORT_PORT="${REPORT_PORT:-29019}"

F5_MONGO_CMD="mongo --port ${REPORT_PORT} topmed_freeze5_hg38 --quiet --eval"
F8_MONGO_CMD="mongo --port ${REPORT_PORT} topmed_freeze8_hg38_browser --quiet --eval"

# Check if mongo is reachable
${F8_MONGO_CMD} "db.version()" > /dev/null

if [ $? -ne 0 ]
then
  echo "Mongodb not reacahble on port $REPORT_PORT"
  exit 1
fi

# Calculate start and end dates for last three months
CURR_MONTH_START=$(date +%Y-%m)-01
PREV_MONTH_START=$(date --date="${CURR_MONTH_START} - 1 month" +%Y-%m-%d)

END_DATES=()
for i in 0 1 2
do
  END_DATES+=( $(date --date="${CURR_MONTH_START} - $i month" +%Y-%m-%d) )
done

START_DATES=()
for i in 1 2 3
do
  START_DATES+=( $(date --date="${CURR_MONTH_START} - $i month" +%Y-%m-%d) )
done

# Run query on freeze 5 db for the three intervals.
echo "----------------------"
echo "BRAVO Freeze5 Instance"
for i in 0 1 2
do
  # Use datetime component of BSON _id creation as when user joined.
  NEW_USERS_Q="db.users.find({_id: "
  NEW_USERS_Q+="{\$lt: ObjectId.fromDate(ISODate('${END_DATES[$i]}')),"
  NEW_USERS_Q+="\$gte: ObjectId.fromDate(ISODate('${START_DATES[$i]}')) "
  NEW_USERS_Q+="}}).count()"

  ALL_USERS_Q="db.users.find({_id: "
  ALL_USERS_Q+="{\$lt: ObjectId.fromDate(ISODate('${END_DATES[$i]}'))"
  ALL_USERS_Q+="}}).count()"

  NEW_USER_CNT=$(mongo --port ${REPORT_PORT} topmed_freeze5_hg38 --quiet --eval "$NEW_USERS_Q")
  ALL_USER_CNT=$(mongo --port ${REPORT_PORT} topmed_freeze5_hg38 --quiet --eval "$ALL_USERS_Q")

  echo "-----"
  echo "Between ${START_DATES[$i]} and ${END_DATES[$i]}"
  echo "New Users:   ${NEW_USER_CNT}"
  echo "Total Users: ${ALL_USER_CNT}" 
done

# Run query on freeze 8 db for the three intervals.
echo "----------------------"
echo "BRAVO Freeze8 Instance"
for i in 0 1 2
do
  # Use datetime component of BSON _id creation as when user joined.

read -r -d '' NEW_USERS_Q <<- EOF
db.users.find(
  {_id: { \$lt: ObjectId.fromDate(ISODate('${END_DATES[$i]}')),
          \$gte: ObjectId.fromDate(ISODate('${START_DATES[$i]}')) }
  }
).count()
EOF

read -r -d '' ALL_USERS_Q <<- EOF
db.users.find(
  {_id: {\$lt: ObjectId.fromDate(ISODate('${END_DATES[$i]}'))}}
).count()
EOF

  NEW_USER_CNT=$(${F8_MONGO_CMD} "$NEW_USERS_Q")
  ALL_USER_CNT=$(${F8_MONGO_CMD} "$ALL_USERS_Q")

  echo "-----"
  echo "Between ${START_DATES[$i]} and ${END_DATES[$i]}"
  echo "New Users:   ${NEW_USER_CNT}"
  echo "Total Users: ${ALL_USER_CNT}" 
done

read -r -d '' ALL_IDS <<- EOF
db.users.find(
  {_id: {\$lt: ObjectId.fromDate(ISODate('${CURR_MONTH_START}'))} },
  {user_id: 1, _id: 0}
).toArray()
EOF
