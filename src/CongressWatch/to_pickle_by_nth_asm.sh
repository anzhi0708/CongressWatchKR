#!/usr/bin/env bash


ASM_START=$1
ASM_END=$2
SCRIPT="./_paper_get_confdesc_by_nth.py"

if [[ $# -lt 2 ]]
then
	echo "$0: Need enough arguments!"
	exit -1
fi

echo -e "$0: Running bash script...\n"
echo "$0: Will get these Asm' conf descs:"

for nth in `seq $ASM_START $ASM_END`
do
	echo -ne "\t$nth"
done

sleep 3
echo -e "\n"


for nth in `seq $ASM_START $ASM_END`
do
	echo -e "$0: Getting confdesc of year $nth\n"
	time python3 $SCRIPT $nth
	echo -e "$0: Done getting confdesc of $nth asm\n"
	echo -e "$0: Moving on...\n"
done

