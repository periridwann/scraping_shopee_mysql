from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time
import mysql.connector

opsi = webdriver.ChromeOptions()
opsi.add_argument('--headless') # agar tidak menampilkan browser saat menjalankan script
servis = Service('chromedriver.exe')
driver = webdriver.Chrome(service=servis, options=opsi)

shopee_link = 'https://shopee.co.id/search?keyword=tas%20pria'
driver.set_window_size(1300,800) # set window size agar semua data dapat diakses
driver.get(shopee_link)

rentang = 500 # panjang scroll kebawah (500 pixel)

for i in range(1,7): # dibuat scroll sebanyak 6 kali agar mendapatkan semua data
    akhir = rentang * i
    perintah = "window.scrollTo(0,"+str(akhir)+")" # buat perintah menggunakan javascript
    driver.execute_script(perintah)
    print("loading ke-"+str(i)) # untuk menampilkan sudah berapa halaman yang discroll
    time.sleep(1)

time.sleep(10)

content = driver.page_source
driver.quit()

# ----------------- SCRAPING DATA --------
i = 1
data = BeautifulSoup(content, 'html.parser') # beautifulsoup untuk parsing data
base_url = 'https://shopee.co.id'
list_produk=[]
for area in data.find_all('div',class_="col-xs-2-4 shopee-search-item-result__item"):
    print('proses data ke-'+str(i))
    nama_produk = area.find('div',class_="ie3A+n bM+7UW Cve6sh").get_text()
    harga_produk = area.find('span',class_='ZEgDH9').get_text()
    lokasi_penjualan = area.find('div',class_='zGGwiV').get_text()
    produk_terjual = area.find('div',class_='r6HknA uEPGHT')
    if produk_terjual != None:
        produk_terjual = produk_terjual.get_text()
    link_penjualan = base_url + area.find('a')['href']

    list_produk.append(
        (nama_produk, harga_produk, lokasi_penjualan, produk_terjual, link_penjualan)
    )
    i+=1
    print("------")
    
    # ----------------- SAVE TO MYSQL --------
    cnx = mysql.connector.connect(user='root', database='shopee')
    cursor = cnx.cursor()

    add_product = ("INSERT INTO product "
                "(nama_produk, harga_produk, lokasi_penjualan, produk_terjual, link_penjualan) "
                "VALUES (%s, %s, %s, %s, %s)")

    data_product = (nama_produk, harga_produk, lokasi_penjualan, produk_terjual, link_penjualan)
    cursor.execute(add_product, data_product)
    emp_no = cursor.lastrowid
    cnx.commit() # commit ke database
    cursor.close()
    cnx.close()