from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import time
import urllib.request
from urllib.parse import urlparse
import os
import requests
import io
from PIL import Image
import re
import csv
import random
import math

import patch

class GoogleImageScraper():
    def __init__(self, webdriver_path, image_path, search_key="cat", number_of_images=10, headless=True, min_resolution=(0, 0), max_resolution=(1920, 1080), max_missed=10, test_split=0.2):
        self.train_path = os.path.join(image_path, 'train', search_key)
        self.test_path = os.path.join(image_path, 'test', search_key)
        self.data_path = os.path.join(image_path, 'data')
        
        os.makedirs(self.train_path, exist_ok=True)
        os.makedirs(self.test_path, exist_ok=True)
        os.makedirs(self.data_path, exist_ok=True)

        number_of_images *= 6
        if type(number_of_images) != int:
            print("[Error] Number of images must be integer value.")
            return

        if not os.path.isfile(webdriver_path):
            is_patched = patch.download_lastest_chromedriver()
            if not is_patched:
                exit("[ERR] Update the chromedriver.")

        options = Options()
        if headless:
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=webdriver.chrome.service.Service(webdriver_path), options=options)
        self.driver.set_window_size(1400, 1050)
        
        self.search_key = search_key
        self.number_of_images = number_of_images
        self.image_path = image_path
        self.url = f"https://www.google.com/search?q={search_key}&source=lnms&tbm=isch"
        self.headless = headless
        self.min_resolution = min_resolution
        self.max_resolution = max_resolution
        self.max_missed = max_missed
        self.test_split = test_split

    def find_image_urls(self):
        print("[INFO] Gathering image links")
        self.driver.get(self.url)
        image_urls = []
        count, missed_count = 0, 0
        time.sleep(2)

        try:
            first_image = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[jsname="dTDiAc"]'))
            )
            first_image.click()
        except Exception as e:
            print("[ERROR] Couldn't click the first image:", e)
            return image_urls

        while self.number_of_images > count and missed_count < self.max_missed:
            try:
                time.sleep(1)
                class_names = ["n3VNCb", "iPVvYb", "r48jcc", "pT0Scc"]
                images = [self.driver.find_elements(By.CLASS_NAME, class_name) for class_name in class_names if self.driver.find_elements(By.CLASS_NAME, class_name)]
                images = images[0] if images else []
                for image in images:
                    src_link = image.get_attribute("src")
                    if "http" in src_link and not "encrypted" in src_link:
                        print(f"[INFO] {self.search_key} \t #{count} \t {src_link}")
                        image_urls.append(src_link)
                        count += 1
                        break
            except Exception:
                print("[INFO] Unable to get link")
            try:
                if count % 3 == 0:
                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ARROW_RIGHT)
                element = self.driver.find_element(By.CLASS_NAME, "mye4qd")
                element.click()
                print("[INFO] Loading next page")
                time.sleep(1)
            except Exception:
                time.sleep(1)

        self.driver.quit()
        print("[INFO] Google search ended")
        return list(set(image_urls))

    def save_images(self, image_urls, keep_filenames=True):
        self._save_images_and_log(image_urls, self.train_path, keep_filenames)

        all_train_images = os.listdir(self.train_path)
        num_test_images = math.floor(len(all_train_images) * self.test_split)
        test_images = random.sample(all_train_images, num_test_images)

        for image_name in test_images:
            src_path = os.path.join(self.train_path, image_name)
            dest_path = os.path.join(self.test_path, image_name)
            os.rename(src_path, dest_path)

        self._append_to_csv(self.train_path, "train_dataset.csv")
        self._append_to_csv(self.test_path, "test_dataset.csv")
        print("[INFO] Image saving, splitting, and CSV logging completed.")

    def _save_images_and_log(self, urls, save_path, keep_filenames=True):
        print(f"[INFO] Saving images to {save_path}...")
        for indx, image_url in enumerate(urls):
            try:
                search_string = ''.join(e for e in self.search_key if e.isalnum())
                image = requests.get(image_url, timeout=5)
                if image.status_code == 200:
                    with Image.open(io.BytesIO(image.content)) as image_from_web:
                        # Forzar el formato de archivo a .jpg
                        if keep_filenames:
                            o = urlparse(image_url)
                            image_url = o.scheme + "://" + o.netloc + o.path
                            name = os.path.splitext(os.path.basename(image_url))[0]
                            filename = f"{name}.jpg"
                        else:
                            filename = f"{search_string}{indx}.jpg"

                        image_path = os.path.join(save_path, filename)
                        image_from_web = image_from_web.convert("RGB")  # Convertir a RGB para asegurar el formato .jpg
                        image_from_web.save(image_path, "JPEG")
                        image_resolution = image_from_web.size
                        if (image_resolution[0] < self.min_resolution[0] or
                            image_resolution[1] < self.min_resolution[1] or
                            image_resolution[0] > self.max_resolution[0] or
                            image_resolution[1] > self.max_resolution[1]):
                            image_from_web.close()
                            os.remove(image_path)
                        image_from_web.close()
            except Exception as e:
                print("[ERROR] Download failed: ", e)
                pass
        print(f"[INFO] Downloads to {save_path} completed.")

    def _append_to_csv(self, directory, csv_file):
        csv_path = os.path.join(self.data_path, csv_file)
        print(f"[INFO] Appending to CSV file {csv_path}...")
        
        with open(csv_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if os.stat(csv_path).st_size == 0:
                writer.writerow(["filename", "target"])  # Escribir encabezado solo si el archivo está vacío

            for filename in os.listdir(directory):
                writer.writerow([filename, self.search_key])
        
        print(f"[INFO] Data appended to CSV file {csv_path}.")
