# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class KlbcItem(Item):
	item_id = Field()
	full_text= Field()
	full_html = Field()
	loai = Field()
	so_ki_hieu = Field()
	ngay_ban_hanh = Field()
	loai_van_ban = Field()
	ngay_co_hieu_luc = Field()
	nguon_thu_thap = Field()
	ngay_cong_bao = Field()
	nganh = Field()
	linh_vuc = Field()
	co_quan_ban_hanh = Field()
	chuc_danh =Field()
	nguoi_ki = Field()
	tong_so_co_quan =Field()
	pham_vi = Field()
	thong_tin_ap_dung = Field()
	tinh_trang_hieu_luc = Field()

	vb_can_cu = Field()
	vb_dan_chieu = Field()
	vb_bi_het_hieu_luc = Field()
	vb_sua_doi_bo_sung = Field()
	vb_bi_thay_the = Field()
	vb_bi_bo_mot_phan = Field()
	vb_duoc_huong_dan = Field()
	vb_duoc_quy_dinh_chi_tiet = Field()
	vb_het_hieu_luc = Field()
	vb_bi_het_hieu_luc_1_phan = Field()
	vb_bi_dinh_chi = Field()
	vb_bi_dinh_chi_1_phan = Field()
	vb_duoc_bo_sung = Field()
	vb_duoc_sua_doi = Field()
	vb_hien_thoi = Field()
	vb_lien_quan_khac =Field()
	vb_huong_dan = Field()
	vb_quy_dinh_chi_tiet = Field()
	vb_quy_dinh_het_hieu_luc = Field()
	vb_quy_dinh_het_hieu_luc_1_phan = Field()
	vb_dinh_chi = Field()
	vb_dinh_chi_1_phan = Field()
	vb_bo_sung = Field()
	vb_sua_doi = Field()



