#!/usr/bin/env bash


YEAR_START=$1
YEAR_END=$2
SCRIPT="./_paper_get_confdesc_by_year.py"

if [[ $# -lt 2 ]]
then
	echo "$0: Need enough arguments!"
	exit -1
fi

echo -e "$0: Running bash script...\n"
echo "$0: Will get these years' conf descs:"

for year in `seq $YEAR_START $YEAR_END`
do
	echo -ne "\t$year"
done

sleep 3
echo -e "\n"


for year in `seq $YEAR_START $YEAR_END`
do
	echo -e "$0: Getting confdesc of year $year\n"
	time python3 $SCRIPT $year
	echo -e "$0: Done getting confdesc of year $year\n"
	echo -e "$0: Moving on...\n"
done

