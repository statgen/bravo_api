# Script to query GA4 for active users per day for BRAVO

# Configure application default credentials:
#  https://cloud.google.com/docs/authentication/provide-credentials-adc
#  https://developers.google.com/analytics/devguides/reporting/data/v1/quickstart-cli
#
# Use the credentials of Oauth Client "GA Reports CLI" 
#
#  gcloud auth application-default login \
#      --scopes=https://www.googleapis.com/auth/analytics.readonly \
#      --client-id-file=/PATH/TO/credentials.json

# Default to freeze8 property id
GA4_PROPERTY_ID=${GA4_PROPERTY_ID:-361544710}

# Date calculation adapted from https://unix.stackexchange.com/a/249794
# First day of current month
THIS_MONTH=$(date +%Y%m01)
# Report start day is one month prior to THIS_MONTH
START_DATE=$(date -d "${THIS_MONTH} -1 month" +%Y-%m-%d)
# Report end day is one day prior to THIS_MONTH
END_DATE=$(date -d "${THIS_MONTH} -1 day" +%Y-%m-%d)

# Interpolate dates into analytics query
read -r -d '' QUERY <<-GA_EOF
	{
		"dimensions":[{"name":"nthDay"}],
		"metrics":[{"name":"active1DayUsers"}],
		"dateRanges":[{"startDate":"${START_DATE}",
                   "endDate":"${END_DATE}"}]
	}
GA_EOF

# Make request to analytics api
# JQ to parse and process resulting json
GA_ACCESS_TOKEN=$(gcloud auth application-default print-access-token)

curl -X POST \
	-H "Authorization: Bearer ${GA_ACCESS_TOKEN}" \
	-H "Content-Type: application/json; charset=utf-8" \
	https://analyticsdata.googleapis.com/v1beta/properties/$GA4_PROPERTY_ID:runReport \
	-d "${QUERY}" | \
jq --arg start_dt $START_DATE --arg end_dt $END_DATE \
  '.rows |
  map_values(.metricValues[0]) | 
  map_values(.value | tonumber) | 
  {"project": "BRAVO Freeze 8",
   "metric": "Active Users Per Day",
   "start": $start_dt,
   "end": $end_dt,
   "mean": (add / length), 
   "min": min, 
   "max": max}'
