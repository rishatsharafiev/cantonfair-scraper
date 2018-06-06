# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
DOTENV_PATH = os.path.join(BASE_PATH, '.env')
load_dotenv(DOTENV_PATH)

import logging, time
import unittest, json
import psycopg2, csv, math
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException

class TestCantonfairSite(unittest.TestCase):

    def setUp(self):
        # initialize logget
        self.logger = logging.getLogger(__name__)
        logger_handler = logging.FileHandler(os.path.join(BASE_PATH, '{}.log'.format(__file__)))
        logger_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        logger_handler.setFormatter(logger_formatter)
        self.logger.addHandler(logger_handler)
        self.logger.setLevel(logging.WARNING)
        self.logger.propagate = False

        self.display = Display(visible=0, size=(1024,800))
        self.display.start()

        self.current_path = os.path.dirname(os.path.realpath(__file__))
        self.chromedriver_path = os.path.join(self.current_path, 'chromedriver')
        self.driver = webdriver.Chrome(self.chromedriver_path)
        self.write_filename = 'output.csv'

    def get_category_max_page(self, category_url):
        driver = self.driver
        try:
            driver.get(category_url)

            initial_wait = WebDriverWait(driver, 5*60)
            initial_wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#pagearea'))
            )

            category = self.get_element_by_css_selector('#curmb > a')
            category = category.text if category else 'International Pavilion'

            pages = driver.find_elements_by_css_selector('.pagenumber > a')
            pages = [page.text for page in pages]
            if len(pages) > 1:
                end_page_id = pages[-1]
            else:
                end_page_id = 1
        except Exception as e:
            self.logger.exception(str(e))
            end_page_id = 0
        return (int(end_page_id), category)

    def get_exhibitors_links(self, category_url, max_page):
        driver = self.driver

        links = []

        try:
            try:
                driver.get(category_url)

                initial_wait = WebDriverWait(driver, 5*60)
                initial_wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#pagearea'))
                )

                links.extend([link.get_attribute('href') for link in self.get_elements_by_css_selector('#gjh_pro_result .czs-list > .min > dl > dt > a[target="_blank"]')])

                common_wait = WebDriverWait(driver, 5*60)
                for page_id in range(2, max_page + 1):
                    print(page_id)
                    page_button = self.get_element_by_css_selector('.pagenumber > a[_pageindex="{page_id}"'.format(page_id=page_id))
                    page_button.click()
                    common_wait.until(
                        EC.presence_of_element_located((By.XPATH,  "//span[contains(@class, 'page_cur') and text() = '{page_id}']".format(page_id=page_id)))
                    )
                    links.extend([link.get_attribute('href') for link in self.get_elements_by_css_selector('#gjh_pro_result .czs-list > .min > dl > dt > a[target="_blank"]')])

            except (NoSuchElementException, TimeoutException):
                print('--> Page stalled')

        except Exception as e:
            self.logger.exception(str(e))

        return list(set(links))

    def get_element_by_css_selector(self, selector):
        driver = self.driver
        try:
            element = driver.find_element_by_css_selector(selector)
        except (NoSuchElementException, TimeoutException):
            element = None
        return element

    def get_elements_by_css_selector(self, selector):
        driver = self.driver
        try:
            elements = driver.find_elements_by_css_selector(selector)
        except (NoSuchElementException, TimeoutException):
            elements = None
        return elements

    def get_exhibitors_data(self, exhibitors_url):
        driver = self.driver
        try:
            driver.get(exhibitors_url)
            try:
                initial_wait = WebDriverWait(driver, 5*60)
                initial_wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#content .cright'))
                )

                address = self.get_element_by_css_selector('#Exhi_Address')
                address = address.text if address else ''

                business_type = self.get_element_by_css_selector('#Exhi_TypeName')
                business_type = business_type.text if business_type else ''

                city_province = self.get_element_by_css_selector('#Exhi_Province')
                city_province = city_province.text if city_province else ''

                company_name = self.get_element_by_css_selector('#Exhi_Name')
                company_name = company_name.text if company_name else ''

                exhibition_records = self.get_element_by_css_selector('#Exhi_Record')
                exhibition_records = exhibition_records.text if exhibition_records else ''

                international_commercial_terms = self.get_element_by_css_selector('#Exhi_OEMode')
                international_commercial_terms = international_commercial_terms.text if international_commercial_terms else ''

                main_products = self.get_element_by_css_selector('#Exhi_KeyWord')
                main_products = main_products.text if main_products else ''

                number_of_staff = self.get_element_by_css_selector('#Exhi_PeopleNum')
                number_of_staff = number_of_staff.text if number_of_staff else ''

                post_code = self.get_element_by_css_selector('#Exhi_ZipCode')
                post_code = post_code.text if post_code else ''

                registered_capital = self.get_element_by_css_selector('#Exhi_ExhFund')
                registered_capital = registered_capital.text if registered_capital else ''

                target_customer = self.get_element_by_css_selector('#Exhi_BuyerType')
                target_customer = target_customer.text if target_customer else ''

                website = self.get_element_by_css_selector('#Exhi_WebSite')
                website = website.text if website else ''

                product = {
                    'address': address,
                    'business_type': business_type,
                    'city_province': city_province,
                    'company_name': company_name,
                    'exhibition_records': exhibition_records,
                    'international_commercial_terms': international_commercial_terms,
                    'main_products': main_products,
                    'number_of_staff': number_of_staff,
                    'post_code': post_code,
                    'registered_capital': registered_capital,
                    'target_customer': target_customer,
                    'website': website,
                }

            except (NoSuchElementException, TimeoutException):
                print('--> Product stalled')

        except Exception as e:
            self.logger.exception(str(e))

        return product

    def save_exhibitors_data(self):
        try:
            with psycopg2.connect(dbname='cantonfair', user='cantonfair', password='cantonfair', host='localhost', port=5432) as connection:
                with connection.cursor() as cursor:
                    sql_string = """
                        SELECT
                            "url"
                        FROM "exhibitor"
                        WHERE is_done = false;
                    """
                    cursor.execute(sql_string)

                    exhibitors = cursor.fetchall()

                    for exhibitor in exhibitors:
                        url = exhibitor[0]
                        data = self.get_exhibitors_data(url)

                        address = data['address']
                        business_type = data['business_type']
                        city_province = data['city_province']
                        company_name = data['company_name']
                        exhibition_records = data['exhibition_records']
                        international_commercial_terms = data['international_commercial_terms']
                        is_done = True
                        main_products = data['main_products']
                        number_of_staff = data['number_of_staff']
                        post_code = data['post_code']
                        registered_capital = data['registered_capital']
                        target_customer = data['target_customer']
                        website = data['website']


                        sql_string = """
                            UPDATE "exhibitor" SET
                                   "address" = %s,
                             "business_type" = %s,
                             "city_province" = %s,
                              "company_name" = %s,
                        "exhibition_records" = %s,
            "international_commercial_terms" = %s,
                                   "is_done" = %s,
                             "main_products" = %s,
                           "number_of_staff" = %s,
                                 "post_code" = %s,
                        "registered_capital" = %s,
                           "target_customer" = %s,
                                   "website" = %s
                            WHERE url=%s;
                        """
                        parameters = (
                            address,
                            business_type,
                            city_province,
                            company_name,
                            exhibition_records,
                            international_commercial_terms,
                            is_done,
                            main_products,
                            number_of_staff,
                            post_code,
                            registered_capital,
                            target_customer,
                            website,
                            url,
                        )
                        cursor.execute(sql_string, parameters)
                        connection.commit()
        except Exception as e:
            self.logger.exception(str(e))

    def convert_to_csv(self):
        with psycopg2.connect(dbname='fcmoto', user='fcmoto', password='fcmoto', host='localhost', port=5432) as connection:
            with connection.cursor() as cursor:
                with open(self.write_filename, 'w', encoding='utf-8') as write_file:
                    csv_writer = csv.writer(write_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n')
                    # заголовок
                    col_names = [
                        'Наименование',
                        'Наименование артикула',
                        'Код артикула',
                        'Валюта',
                        'Цена',
                        'Доступен для заказа',
                        'Зачеркнутая цена',
                        'Закупочная цена',
                        'В наличии',
                        'Основной артикул',
                        'В наличии @Склад в Москве',
                        'В наличии @Склад в Европе',
                        'Краткое описание',
                        'Описание',
                        'Наклейка',
                        'Статус',
                        'Тип товаров',
                        'Теги',
                        'Облагается налогом',
                        'Заголовок',
                        'META Keywords',
                        'META Description',
                        'Ссылка на витрину',
                        'Адрес видео на YouTube или Vimeo',
                        'Дополнительные параметры',
                        'Производитель',
                        'Бренд',
                        'Подходящие модели автомобилей',
                        'Вес',
                        'Страна происхождения',
                        'Пол',
                        'Цвет',
                        'Материал',
                        'Материал подошвы',
                        'Уровень',
                        'Максимальный вес пользователя',
                        'Размер',
                        'Изображения',
                        'Изображения',
                    ]
                    csv_writer.writerow([item.encode('utf8').decode('utf8') for item in col_names])
                    # подзаголовок 1
                    col_names = [
                        '<Категория>',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '<Ссылка на категорию>',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                    ]
                    csv_writer.writerow([item.encode('utf8').decode('utf8') for item in col_names])
                    # подзаголовок 2
                    col_names = [
                        '<Подкатегория>',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '<Ссылка на подкатегорию>',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                    ]
                    csv_writer.writerow([item.encode('utf8').decode('utf8') for item in col_names])

                    cursor.execute('SELECT DISTINCT "id" FROM "product";')
                    for row in cursor.fetchall():
                        sql_string = """
                            SELECT
                                "back_picture",
                                "colors",
                                "description_html",
                                "description_text",
                                "front_picture",
                                "manufacturer",
                                "name",
                                "name_url",
                                "price_cleaned",
                                "product_url",
                                "available",
                                "value"
                            FROM "product"
                            INNER JOIN "size" ON "product"."id" = "size"."product_id"
                            WHERE "product"."id" = %s
                            ORDER BY "value";
                        """
                        parameters = (row[0], )
                        cursor.execute(sql_string, parameters)

                        product_list = []

                        counter = 1
                        all_size=[]
                        items = list(cursor.fetchall())
                        for item in items:
                            back_picture = item[0].replace('"', "'")
                            colors = item[1].replace('"', "'")
                            description_html = item[2].replace('"', "'")
                            description_text = item[3].replace('"', "'")
                            front_picture = item[4]
                            manufacturer = item[5]
                            name = item[6].replace('"', "'")
                            name_url = item[7].replace('"', "'")
                            price_cleaned = math.ceil(float(item[8]))
                            product_url = item[9]
                            available = item[10]
                            value = item[11].replace('"', "'")

                            all_size.append(value)
                            sex = 'мужской'
                            keywords = ", ".join(name.split(' '))

                            if counter == 1:
                                item = [
                                    name,
                                    '{size}, {colors}'.format(size=value, colors=colors),
                                    '',
                                    'RUB',
                                    price_cleaned,
                                    1 if available else 0,
                                    '0',
                                    price_cleaned,
                                    1 if available else 0,
                                    '',
                                    '0',
                                    1 if available else 0,
                                    name,
                                    description_html,
                                    '',
                                    '1',
                                    'Одежда',
                                    keywords,
                                    '',
                                    name,
                                    keywords,
                                    description_text,
                                    name_url,
                                    '',
                                    '',
                                    manufacturer,
                                    manufacturer,
                                    '',
                                    '',
                                    '',
                                    '',
                                    '{colors}'.format(colors=colors),
                                    '',
                                    '',
                                    '',
                                    '',
                                    value,
                                    front_picture,
                                    back_picture,
                                ]
                                product_list.append(item)
                            else:
                                item = [
                                    name,
                                    '{size}, {colors}'.format(size=value, colors=colors),
                                    '',
                                    'RUB',
                                    price_cleaned,
                                    1 if available else 0,
                                    '0',
                                    price_cleaned,
                                    1 if available else 0,
                                    '',
                                    '0',
                                    1 if available else 0,
                                    name,
                                    description_html,
                                    '',
                                    '1',
                                    'Одежда',
                                    keywords,
                                    '',
                                    name,
                                    keywords,
                                    description_text,
                                    name_url,
                                    '',
                                    '',
                                    manufacturer,
                                    manufacturer,
                                    '',
                                    '',
                                    '',
                                    '',
                                    '{colors}'.format(colors=colors),
                                    '',
                                    '',
                                    '',
                                    '',
                                    value,
                                    '',
                                    '',
                                ]
                                product_list.append(item)


                            if len(items) == counter:
                                all_size = ",".join(sorted(all_size))
                                available_order = sum([item[10] for item in items])

                                main_item = [
                                    name,
                                    '',
                                    '',
                                    'RUB',
                                    price_cleaned,
                                    available_order,
                                    '0',
                                    price_cleaned,
                                    available_order,
                                    '',
                                    '0',
                                    available_order,
                                    name,
                                    description_html,
                                    '',
                                    '1',
                                    'Одежда',
                                    keywords,
                                    '',
                                    name,
                                    keywords,
                                    description_text,
                                    name_url,
                                    '',
                                    '',
                                    manufacturer,
                                    manufacturer,
                                    '',
                                    '',
                                    '',
                                    sex,
                                    '<{{{colors}}}>'.format(colors=colors),
                                    '',
                                    '',
                                    '',
                                    '',
                                    '<{{{all_size}}}>'.format(all_size=all_size),
                                    front_picture,
                                    back_picture,
                                ]
                                product_list.insert(0, main_item)
                            counter+=1

                        # write end rows
                        [csv_writer.writerow(item) for item in product_list]
                        # write ending row
                        col_names = [
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                            '',
                        ]
                        csv_writer.writerow([item.encode('utf8').decode('utf8') for item in col_names])

    def save_exhibitors_links(self):
        category_list = [
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=411&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=412&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=410&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=414&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=403&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=404&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=405&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=408&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=454&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=455&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=451&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=401&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=402&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=406&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=407&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=415&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=416&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=427&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=453&StageOne=0&StageTwo=0&StageThree=0&Export=0&Import=0&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
            'http://i.cantonfair.org.cn/en/SearchResult/Index?QueryType=2&KeyWord=&CategoryNo=&StageOne=1&StageTwo=0&StageThree=0&Export=0&Import=1&Provinces=&Countries=&ShowMode=1&NewProduct=0&CF=0&OwnProduct=0&PayMode=&NewCompany=0&BrandCompany=0&ForeignTradeCompany=0&ManufacturCompany=0&CFCompany=0&OtherCompany=0&OEM=0&ODM=0&OBM=0&OrderBy=1&producttab=1',
        ]

        for category_url in category_list:
            max_page, category = self.get_category_max_page(category_url)
            with psycopg2.connect(dbname='cantonfair', user='cantonfair', password='cantonfair', host='localhost', port=5432) as connection:
                with connection.cursor() as cursor:
                    for link in self.get_exhibitors_links(category_url, max_page):
                        sql_string = """
                            INSERT INTO "exhibitor" ("url", "category_name")
                            VALUES (%s, %s)
                            ON CONFLICT ("url")
                            DO
                                UPDATE
                                    SET url = %s, category_name = %s;
                        """
                        parameters = ( link, category, link, category)
                        cursor.execute(sql_string, parameters)
                        connection.commit()


    def test_main(self):
        # self.save_products_to_db()
        # self.convert_to_csv()
        self.save_exhibitors_links()
        # self.save_exhibitors_data()
        self.driver.quit()

if __name__ == '__main__':
    unittest.main()
