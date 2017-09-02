#!/bin/bash

rm -r ./klbc_result
sudo service mongod start
scrapy crawl klbc

rm -r *.json
rm -r *.tsv
mongoexport --db klbc --collection laws --out ./laws.json
# cat ./laws.json | jq -r '[.item_id,.full_text,.so_ki_hieu,.ngay_ban_hanh,.ngay_cong_bao,.loai,.loai_van_ban,.nguon_thu_thap,.pham_vi,.ngay_co_hieu_luc] | @tsv' > ./laws.tsv
# cat ./laws.json | jq -r '[.item_id,.full_text,.full_html] | @tsv' > ./laws.tsv
# cat ./laws.json | jq -r '[.item_id,.full_text,.full_html,.mo_ta,.ten_vb] | @tsv' > ./laws.tsv
cat ./laws.json | jq -r '[.item_id,.co_quan_ban_hanh,.nguoi_ki,.chuc_danh] | @tsv' > ./laws.tsv


# thuoc tinh

# item_id
# ten_vb
# mo_ta
# full_text
# full_html
# loai
# so_ki_hieu
# ngay_ban_hanh
# loai_van_ban
# ngay_co_hieu_luc
# nguon_thu_thap
# ngay_cong_bao
# nganh
# linh_vuc
# tong_so_co_quan
# co_quan_ban_hanh,co_quan_ban_hanh_%i
# chuc_danh,chuc_danh_%i
# nguoi_ki,nguoi_ki_%i
# pham_vi
# tinh_trang_hieu_luc

# vb_can_cu
# vb_dan_chieu
# vb_bi_het_hieu_luc
# vb_sua_doi_bo_sung
# vb_bi_thay_the
# vb_bi_bo_mot_phan
# vb_duoc_huong_dan
# vb_duoc_quy_dinh_chi_tiet
# vb_het_hieu_luc
# vb_bi_het_hieu_luc_1_phan
# vb_bi_dinh_chi
# vb_bi_dinh_chi_1_phan
# vb_duoc_bo_sung
# vb_duoc_sua_doi
# vb_hien_thoi
# vb_lien_quan_khac
# vb_huong_dan
# vb_quy_dinh_chi_tiet
# vb_quy_dinh_het_hieu_luc
# vb_quy_dinh_het_hieu_luc_1_phan
# vb_dinh_chi
# vb_dinh_chi_1_phan
# vb_bo_sung
# vb_sua_doi