# -*- coding: utf-8 -*

import scrapy
import os
import html2text
import json
import codecs
import io
import re 

from scrapy.conf import settings
from scrapy import Spider
from scrapy.selector import Selector
from klbc.items import KlbcItem
from scrapy.item import Item, Field
from pymongo import MongoClient



def to_unicode(string, encoding = 'utf-8'):
	if isinstance(string, basestring):
		if not isinstance(string, unicode):
			string = unicode(string, encoding)
	return string

def check_data(data):
	if(len(data) > 0):
		# return data[0].strip()
		return ', '.join(x.strip() for x in data)
	else:
		return ''

class KlbcSpider(Spider):
	name = settings['BOT_NAME']
	allowed_domains = ['vbpl.vn', 'www.vbpl.vn','http://vbpl.vn']
	start_urls = [
		"http://vbpl.vn/pages/portal.aspx"
	]
#####################
	client = MongoClient('localhost', 27017)
	client.drop_database('klbc')
	db = client.klbc
	collection = db.laws
######################
	def parse(self, response):
		original_url = "http://vbpl.vn/VBQPPL_UserControls/Publishing_22/TimKiem/p_KetQuaTimKiemVanBan.aspx?&IsVietNamese=True&DivID=tabVB_lv1_01"
		row_per_page = "&RowPerPage=" + settings['ROW_PER_PAGE']
	

		# drop database
		for i in range(settings['FROM_PAGE'], settings['TO_PAGE']):
			page = "&Page=" + `i`
		
			url = original_url + page + row_per_page
			yield scrapy.Request(url, callback = self.parse_page)
# crawl with array value

	# def parse(self, response):
	# 	original_url = "http://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID="
	# 	#id_list = ["32970","32603","27708","97167","26403","26404","12272","12661","16868","26759","17750","13914","21957","22072","21957","20981"]
	# 	id_list = ["11635"]

	# 	for i in id_list:
	# 		meta = {}
	# 		meta['item_id'] = i
	# 		meta['ten_vb'] = ''
	# 		meta['mo_ta'] = ''
	# 		original_url_tmp = original_url + i 
	# 		yield scrapy.Request(original_url_tmp, callback = self.parse_document, meta = meta)


	def parse_page(self,response):
		items  = response.xpath('//div[@class="item"]//p[@class="title"]')
		original_url = "http://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID="
		descriptions = response.xpath('//div[@class="item"]//div[@class="left"]/div[@class="des"]/p/text()')
		for i in items:
			l = i.xpath('a/@href').extract()[0]
			item_id = (l.split('ItemID=')[1]).split('&')[0]
			name = ""
			description = ""
			try:
				name = (i.xpath('a/text()').extract_first()).strip()
				description = descriptions.extract()[items.index(i)].strip()
			except Exception:
				print "null"
			meta = {}
			meta['item_id'] = item_id
			meta['ten_vb'] = name
			meta['mo_ta'] = description
			url = original_url + item_id
			yield scrapy.Request(url,callback =self.parse_document,meta = meta) 


	def parse_document(self, response):
		meta = response.meta
		directory = settings['DIRECTORY'] + "/" + meta['item_id']
		fulltext_file_name = directory + '/' + meta['item_id'] + '.txt'
		fulltext_file_name_with_html = directory + '/' + meta['item_id'] + '_html.txt'
		div_content = response.xpath("//div[@class='fulltext']/div[2]")
		div_content1 = response.xpath("//a[@id='A3']/@href").extract_first()
		meta['full_text'] = ""
		meta['full_html'] = ""
		content = div_content.extract_first()

		if content is not None:
			if not os.path.exists(directory):
				os.makedirs(directory)
			fulltext_file = open(fulltext_file_name, "w")
			fulltext_file_html = open(fulltext_file_name_with_html,"w")
			fulltext_file_html.write(content.encode('utf-8'))
			meta['full_html'] = content.encode('utf-8')
			a = html2text.HTML2Text()
			a.ignore_links = True
			b = a.handle(content).encode('utf-8')
			meta['full_text'] = re.sub(r"\n(?!\n)"," ",b)
			fulltext_file.write(b)
			url = "http://vbpl.vn/TW/Pages/vbpq-thuoctinh.aspx?ItemID=" + meta['item_id']
			yield scrapy.Request(url, callback = self.parse_attribute, meta = meta)

		if div_content1 is not None:
			content = div_content1.split(',')[1]
			content1 = content.split("'")[1]
			print content1
			yield scrapy.Request(
	            url="http://vbpl.vn" + content1,
	            callback=self.save_pdf,
	            meta = meta
	        )
    
	def parse_attribute(self, response):
		meta = response.meta

		div_properties = response.xpath('//div[@class="vbProperties"]')

		list_properties = {}
		list_properties['item_id'] = meta['item_id']
		list_properties['ten_vb'] = meta['ten_vb']
		list_properties['mo_ta'] = meta['mo_ta']
		list_properties['full_text'] = meta['full_text']
		list_properties['full_html'] = meta['full_html']

		list_properties['loai'] = check_data(div_properties
								  .xpath('//tr[1]/td/text()').extract())
		list_properties['so_ki_hieu'] = check_data(div_properties
									  .xpath('//tr[2]/td[2]/text()').extract())
		list_properties['ngay_ban_hanh'] = check_data(div_properties
								.xpath('//tr[2]/td[4]/text()').extract())
		list_properties['loai_van_ban'] = check_data(div_properties
										.xpath('//tr[3]/td[2]/a/text()').extract())
		list_properties['ngay_co_hieu_luc'] = check_data(div_properties
										   .xpath('//tr[3]/td[4]/text()').extract())
		list_properties['nguon_thu_thap'] = check_data(div_properties
										  .xpath('//tr[4]/td[2]/text()').extract())
		list_properties['ngay_cong_bao'] = check_data(div_properties
										 .xpath('//tr[4]/td[4]/text()').extract())

		row = 5

		if div_properties.xpath('//tr['+str(row)+']/td[1]/text()').extract()[0].strip() == to_unicode('Ngành'):
			list_properties['nganh'] = check_data(div_properties
									   .xpath('//tr['+str(row)+']/td[2]/ul/li/text()').extract())
			list_properties['linh_vuc'] = check_data(div_properties
										 .xpath('//tr['+str(row)+']/td[4]/ul/li/text()').extract())
			row = row + 1
		else:
			list_properties['nganh'] = ''
			list_properties['linh_vuc'] = ''

		flag = True
		temp = 1
		temp_2 = 2
		while flag:
			field_1 = 'co_quan_ban_hanh_' + str(temp)
			field_2 = 'chuc_danh_' + str(temp)
			field_3 = 'nguoi_ki_' + str(temp)
		
			list_properties[field_1] = check_data(div_properties
											   .xpath('//tr['+str(row + temp -1)+']/td['+str(temp_2)+']/a/text()').extract())
			list_properties[field_2] = check_data(div_properties
										  .xpath('//tr['+str(row + temp -1)+']/td['+str(temp_2+1)+']/text()').extract())
			list_properties[field_3] = check_data(div_properties
										 .xpath('//tr['+str(row + temp -1)+']/td['+str(temp_2+2)+']/text()').extract())
			next_row = len(div_properties.xpath('//tr['+str(row+temp)+']/td'))

			temp = temp + 1
			temp_2 = 1
			if next_row != 3:
				row = row + temp - 1
				flag = False

		list_properties['tong_so_co_quan'] = str(temp -1)

		list_properties['pham_vi'] = check_data(div_properties
										.xpath('//tr['+str(row)+']/td[2]/ul/li/text()').extract())
		list_properties['thong_tin_ap_dung'] = html2text.html2text(check_data(div_properties
												.xpath('//tr['+str(row+1)+']/td').extract()))
		list_properties['tinh_trang_hieu_luc'] = check_data(div_properties
												  .xpath('//tr['+str(row+2)+']/td/text()').extract())

		url = "http://vbpl.vn/TW/Pages/vbpq-vanbanlienquan.aspx?ItemID=" + meta['item_id']
		yield scrapy.Request(url, callback = self.parse_related_documents, meta = list_properties)

	def parse_related_documents(self, response):
		meta = response.meta

		list_properties = {}
		list_properties['ten_vb'] = meta['ten_vb']
		list_properties['mo_ta'] = meta['mo_ta']
		list_properties['full_text'] = meta['full_text']
		list_properties['full_html'] = meta['full_html']
		list_properties['item_id'] = meta['item_id']
		list_properties['loai'] = meta['loai']
		list_properties['so_ki_hieu'] = meta['so_ki_hieu']
		list_properties['ngay_ban_hanh'] = meta['ngay_ban_hanh']
		list_properties['loai_van_ban'] = meta['loai_van_ban']
		list_properties['ngay_co_hieu_luc'] = meta['ngay_co_hieu_luc']
		list_properties['nguon_thu_thap'] = meta['nguon_thu_thap']
		list_properties['ngay_cong_bao'] = meta['ngay_cong_bao']
		list_properties['nganh'] = meta['nganh']
		list_properties['linh_vuc'] = meta['linh_vuc']
		temp = int(meta['tong_so_co_quan'])

		list_properties['tong_so_co_quan'] = temp
		co_quan_ban_hanh = []
		nguoi_ki = []
		chuc_danh = []

		for i in range(1,temp+1):
			list_properties['co_quan_ban_hanh_' + str(i)] = meta['co_quan_ban_hanh_'+str(i)]
			list_properties['chuc_danh_' + str(i)] = meta['chuc_danh_'+str(i)]
			list_properties['nguoi_ki_'+ str(i)] = meta['nguoi_ki_'+str(i)]
			co_quan_ban_hanh.append(meta['co_quan_ban_hanh_'+str(i)])
			nguoi_ki.append(meta['nguoi_ki_'+str(i)])
			chuc_danh.append(meta['chuc_danh_'+str(i)])
		list_properties['co_quan_ban_hanh'] = ', '.join(co_quan_ban_hanh)
		list_properties['nguoi_ki'] = ', '.join(nguoi_ki)
		list_properties['chuc_danh'] = ', '.join(chuc_danh)

		list_properties['pham_vi'] = meta['pham_vi']
		list_properties['thong_tin_ap_dung'] = meta['thong_tin_ap_dung']
		list_properties['tinh_trang_hieu_luc'] = meta['tinh_trang_hieu_luc']

		div_related_documents = response.xpath('//div[@class="vbLienQuan"]')
		number_rows = len(div_related_documents.xpath('//div[@class="content"]/table/tbody/tr'))
		for i in range(0, number_rows):
			doc_type = div_related_documents.xpath('//div[@class="content"]/table/tbody/tr[' 
						+ `i + 1` +"]/td[1]/text()").extract()[0].strip()
			if(doc_type == to_unicode("Văn bản căn cứ")):
				doc_type = 'vb_can_cu'
			elif(doc_type == to_unicode("Văn bản dẫn chiếu")):
				doc_type = 'vb_dan_chieu'
			elif(doc_type == to_unicode("Văn bản bị hết hiệu lực")):
				doc_type = 'vb_bi_het_hieu_luc'
			elif(doc_type == to_unicode("Văn bản được sửa đổi bổ sung")):
				doc_type = 'vb_sua_doi_bo_sung'
			elif(doc_type == to_unicode("Văn bản bị thay thế")):
				doc_type = 'vb_bi_thay_the'
			elif(doc_type == to_unicode("Văn bản bị bãi bỏ một phần")):
				doc_type = 'vb_bi_bo_mot_phan'
			elif(doc_type == to_unicode("Văn bản được hướng dẫn")):
				doc_type = 'vb_duoc_huong_dan'
			elif(doc_type == to_unicode("Văn bản được quy định chi tiết")):
				doc_type = 'vb_duoc_quy_dinh_chi_tiet'
			elif(doc_type == to_unicode("Văn bản hết hiệu lực")):
				doc_type = 'vb_het_hieu_luc'
			elif(doc_type == to_unicode("Văn bản bị hết hiệu lực 1 phần")):
				doc_type = 'vb_bi_het_hieu_luc_1_phan'
			elif(doc_type == to_unicode("Văn bản bị đình chỉ")):
				doc_type = 'vb_bi_dinh_chi'
			elif(doc_type == to_unicode("Văn bản bị đình chỉ 1 phần")):
				doc_type = 'vb_bi_dinh_chi_1_phan'
			elif(doc_type == to_unicode("Văn bản được bổ sung")):
				doc_type = 'vb_duoc_bo_sung'
			elif(doc_type == to_unicode("Văn bản được sửa đổi")):
				doc_type = 'vb_duoc_sua_doi'
			elif(doc_type == to_unicode("Văn bản hiện thời")):
				doc_type = 'vb_hien_thoi'
			elif(doc_type == to_unicode("Văn bản liên quan khác")):
				doc_type = 'vb_lien_quan_khac'
			elif(doc_type == to_unicode("Văn bản hướng dẫn")):
				doc_type = 'vb_huong_dan'
			elif(doc_type == to_unicode("Văn bản quy định chi tiết")):
				doc_type = 'vb_quy_dinh_chi_tiet'
			elif(doc_type == to_unicode("Văn bản quy định hết hiệu lực")):
				doc_type = 'vb_quy_dinh_het_hieu_luc'
			elif(doc_type == to_unicode("Văn bản quy định hết hiệu lực 1 phần")):
				doc_type = 'vb_quy_dinh_het_hieu_luc_1_phan'
			elif(doc_type == to_unicode("Văn bản đình chỉ")):
				doc_type = 'vb_dinh_chi'
			elif(doc_type == to_unicode("Văn bản đình chỉ 1 phần")):
				doc_type = 'vb_dinh_chi_1_phan'
			elif(doc_type == to_unicode("Văn bản bổ sung")):
				doc_type = 'vb_bo_sung'
			elif(doc_type == to_unicode("Văn bản sửa đổi")):
				doc_type = 'vb_sua_doi'
			else:
				continue
			tmp = []
			num_documents_related = len(div_related_documents.xpath('//div[@class="content"]/table/tbody/tr[' 
						+ `i + 1` + ']/td[2]/ul[@class="listVB"]/li'))
			for j in range(0, num_documents_related):
				item_related_id = check_data(div_related_documents.xpath('//div[@class="content"]'
					+'/table/tbody/tr[' + `i + 1` + ']/td[2]/ul[@class="listVB"]/li[' 
					+ `j + 1` + ']/div[@class="item"]/p[@class="title"]/a/@href')
					.extract()).split("=")[1]
				list_properties[doc_type +'_'+ `j + 1`] = item_related_id
				tmp.append(item_related_id)
			list_properties[doc_type] = ', '.join(tmp)
		self.collection.insert_one(list_properties)



	def save_pdf(self, response):
		meta = response.meta
		directory = settings['DIRECTORY'] + "/" + meta['item_id']
		if not os.path.exists(directory):
			os.makedirs(directory)
		path = directory + '/' + meta['item_id'] + '.pdf'
		fulltext_file = open(path, "w")
		fulltext_file.write(response.body)
