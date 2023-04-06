#!/usr/bin/env bash

DEARAJ_ROOT=$(pwd)/..
TESTS=$(pwd)
TOOLS_DIR=$DEARAJ_ROOT/src
PDF_FILE=~/Desktop/.test1.pdf
OUTPUT=test1.json
ARG_YEAR=$1

if [[ $ARG_YEAR == "" ]]; then
	echo "Invalid argc"
	exit 1
fi

function pdf_to_json {
	echo "Entering $TOOLS_DIR" && cd $TOOLS_DIR && echo "PDF => JSON" && python3 ./ajpdf.py ${PDF_FILE} > $TESTS/${OUTPUT} && echo "Done."
}

function analyze {
	json_dir="${ARG_YEAR}_json"
	echo "Entering $TOOLS_DIR" && cd $TOOLS_DIR && echo "Analyzing ${ARG_YEAR}..." && echo "$(ls $json_dir | wc -l) JSON records found."
	for single_json_file in $(ls $json_dir); do
		echo " "
		python3 ./ajFemaleMPAnalyzer.py --file=$json_dir/$single_json_file describe
		echo " "
	done
}

analyze

