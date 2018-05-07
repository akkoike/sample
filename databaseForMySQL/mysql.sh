#!/bin/sh

# check jq(OSS)
if [ ! -x /usr/bin/jq ]
then
    exit
fi

JSON_OBJ=`/usr/bin/curl http://169.254.169.254/metadata/scheduledevents?api-version=2017-08-01`
FLG=`echo ${JSON_OBJ} | /usr/bin/jq ".Event"`
DocNum=`echo ${JSON_OBJ} | /usr/bin/jq ".DocumentIncarnation"`
TIMESTAMPDATE=`date +%Y-%m-%d' '%H:%M:%S`
YOURNODENAME=`/usr/bin/hostname`

# checking the .Event is null or not
if [ "${FLG}" = "null" ]
then
    /usr/bin/mysql -h metatestmysql.mysql.database.azure.com -u azure01@metatestmysql -pAkiraKoike7! --ssl-ca=/var/tmp/BaltimoreCyberTrustRoot.crt.pem instancemeta -e "insert into instancemetadata(targetnode,timestamp,documentincarnation) values('${YOURNODENAME}', '${TIMESTAMPDATE}', ${DocNum});"

else
    EVID=`echo ${JSON_OBJ} | /usr/bin/jq ".Events[].EventId" | cut -f2 -d"\""`
    EVSTATUS=`echo ${JSON_OBJ} | /usr/bin/jq ".Events[].EventStatus" | cut -f2 -d"\""`
    EVTYPE=`echo ${JSON_OBJ} | /usr/bin/jq ".Events[].EventType" | cut -f2 -d"\""`
    RSTYPE=`echo ${JSON_OBJ} | /usr/bin/jq ".Events[].ResourceType" | cut -f2 -d"\""`
    RSOURCE=`echo ${JSON_OBJ} | /usr/bin/jq ".Events[].Resources[]" | cut -f2 -d"\""`
    NOTBEFORE=`echo ${JSON_OBJ} | /usr/bin/jq ".Events[].NotBefore" | cut -f2 -d"\""`
    /usr/bin/mysql -h metatestmysql.mysql.database.azure.com -u azure01@metatestmysql -pAkiraKoike7! --ssl-ca=/var/tmp/BaltimoreCyberTrustRoot.crt.pem instancemeta -e "insert into instancemetadata(targetnode,timestamp,documentincarnation,eventid,eventstatus,eventtype,resourcetype,resources,notbefore) values('$YOURNODENAME', '${TIMESTAMPDATE}', ${DocNum}, '${EVID}', '${EVSTATUS}', '${EVTYPE}', '${RSTYPE}', '${RSOURCE}', '${NOTBEFORE}');"
fi