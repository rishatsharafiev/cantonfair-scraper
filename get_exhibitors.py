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

            initial_wait = WebDriverWait(driver, 60*60)
            initial_wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#pagearea'))
            )

            category = self.get_element_by_css_selector('#curmb > a')
            category = category.text

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

                initial_wait = WebDriverWait(driver, 3*60)
                initial_wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#pagearea'))
                )

                links.extend([link.get_attribute('href') for link in self.get_elements_by_css_selector('#gjh_pro_result .czs-list > .min > dl > dt > a[target="_blank"]')])

                common_wait = WebDriverWait(driver, 3*60)
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

    def get_product(self, product_url):
        driver = self.driver
        product = None
        try:
            driver.get(product_url)
            try:
                initial_wait = WebDriverWait(driver, 3*60)
                initial_wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.ContentAreaWrapper'))
                )

                common_wait = WebDriverWait(driver, 3*60)

                # 'Наименование',
                name = self.get_element_by_css_selector('.ICProductVariationArea [itemprop="name"]')
                name = name.text if name else ''

                # 'Производитель',
                manufacturer = self.get_element_by_css_selector('.ICProductVariationArea [itemprop="manufacturer"]')
                manufacturer = manufacturer.text if manufacturer else ''

                # 'Цвета',
                colors = self.get_element_by_css_selector('.ICVariationSelect .Headline.image .Bold.Value')
                colors = colors.text if colors else ''

                # 'Все размеры',
                all_size = self.get_elements_by_css_selector('.ICVariationSelect li > button')
                all_size = set([size.text for size in all_size] if all_size else [])

                # 'Неактивные размеры',
                disabled_size = self.get_elements_by_css_selector('.ICVariationSelect li.disabled > button')
                disabled_size = set([size.text for size in disabled_size] if disabled_size else [])

                # 'Активные размеры',
                active_size = all_size.difference(disabled_size)

                # 'Цена',
                price = self.get_element_by_css_selector('.PriceArea .Price')
                price = price.text if price else ''
                price_cleaned = price.replace('руб.', '').replace(' ', '').replace(',', '.')

                # 'Фотография'
                front_picture = self.get_element_by_css_selector('#ICImageMediumLarge')
                front_picture = front_picture.get_attribute('src') if front_picture else ''

                activate_second_picture = self.get_element_by_css_selector('#ProductThumbBar > li:nth-child(2) > img')

                if activate_second_picture:
                    activate_second_picture.click()
                    time.sleep(2)
                    back_picture = self.get_element_by_css_selector('#ICImageMediumLarge')
                back_picture = back_picture.get_attribute('src') if activate_second_picture and back_picture else ''

                # 'Описание'
                description = self.get_element_by_css_selector('.description[itemprop="description"]')
                description_text = description.text if description else ''
                description_html = description.get_attribute('innerHTML') if description else ''

                product = {
                    'name': name,
                    'manufacturer': manufacturer,
                    'colors': colors,
                    'all_size': all_size,
                    'disabled_size': disabled_size,
                    'active_size': active_size,
                    'price': price,
                    'price_cleaned': price_cleaned,
                    'front_picture': front_picture,
                    'back_picture': back_picture,
                    'description_text': description_text,
                    'description_html': description_html,

                }

            except (NoSuchElementException, TimeoutException):
                print('--> Product stalled')

        except Exception as e:
            self.logger.exception(str(e))

        return product

    def save_products_to_db(self):
        with psycopg2.connect(dbname='cantonfair', user='cantonfair', password='cantonfair', host='localhost', port=5432) as connection:
            try:

                for product_url in product_urls:
                    product = self.get_product(product_url)
                    if product:
                        with connection.cursor() as cursor:
                            sql_string = """
                                INSERT INTO "product" ("product_url", "name_url", "back_picture", "colors", "description_html", "description_text", "front_picture", "manufacturer", "name", "price_cleaned")
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                RETURNING id;
                            """
                            parameters = ( product_url, product_url.split('/')[-1], product['back_picture'], product['colors'], product['description_html'], product['description_text'], product['front_picture'], product['manufacturer'], product['name'], product['price_cleaned'],)
                            cursor.execute(sql_string, parameters)
                            product_id = cursor.fetchone()[0]
                            connection.commit()
                            if product_id:
                                all_size = product['all_size']
                                active_size = product['active_size']
                                for size in product['all_size']:
                                    if size in active_size:
                                        available = True
                                    else:
                                        available = False
                                    sql_string = """
                                        INSERT INTO "size" ("product_id", "available", "value")
                                        VALUES (%s, %s, %s);
                                    """
                                    parameters = ( product_id, available, size,)
                                    result = cursor.execute(sql_string, parameters)
                                connection.commit()

            finally:
                self.driver.quit()

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

if __name__ == '__main__':
    unittest.main()
