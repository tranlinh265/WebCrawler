#!/bin/bash

rm -r ./klbc_result
sudo service mongod start
scrapy crawl klbc

rm -r *.json
rm -r *.tsv
mongoexport --db klbc --collection laws --out ./laws.json
# cat ./laws.json | jq -r '[.item_id,.full_text,.so_ki_hieu,.ngay_ban_hanh,.ngay_cong_bao,.loai,.loai_van_ban,.nguon_thu_thap,.pham_vi,.ngay_co_hieu_luc] | @tsv' > ./laws.tsv
cat ./laws.json | jq -r '[.item_id,.full_text] | @tsv' > ./laws.tsv