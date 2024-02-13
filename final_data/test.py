import json
import time

import pandas as pd
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# file_path = './final_data/surnames/surname.csv'
file_path = '/Users/mulukenbogale/PycharmProjects/data_man_project/final_data/surnames/surname.csv'

# HOMEPAGE = "https://albo.alboweb-fnofi.net/registry/search"
HOMEPAGE = "https://albo.alboweb.net/registry/search"

data = []

index_pointer = 0

try:
    with open('/Users/mulukenbogale/PycharmProjects/data_man_project/fnofi_last_index.txt', 'r') as file:
        content = file.read()
        index_pointer = int(content)
except FileNotFoundError:
    print("File 'fnofi_last_index.txt' not found. Using default index_pointer value.")

name_of_file = f"fnofi_data_{index_pointer}"


def get_data(url, df):
    # PROXY = "192.111.139.163:19404"
    browser_options = ChromeOptions()
    browser_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    browser_options.add_experimental_option('useAutomationExtension', False)
    browser_options.add_argument('--disable-blink-features=AutomationControlled')
    # browser_options.add_argument("--proxy-server=https://%s" % PROXY)
    driver = Chrome(options=browser_options)

    driver.get(url)

    wait = WebDriverWait(driver, 10)
    global index_pointer

    try:
        for outer_index, row in df.iloc[index_pointer:].iterrows():
            sure_name_input = row["surname"]
            # print("runnig",row["surename"])
            sure_name_input = "abate"
            index_pointer += 1
            print({"name": sure_name_input, "pointer": index_pointer, "index": outer_index})

            # if outer_index % 10 == 0:
            #     break

            sure_name = wait.until(EC.presence_of_element_located((By.ID, "last_name")))
            search = driver.find_element(By.ID, "saveSearch")

            sure_name.send_keys(sure_name_input)
            time.sleep(2)
            search.click()

            WebDriverWait(driver, 10).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete')

            time.sleep(1)
            # table_data = wait.until(EC.presence_of_element_located((By.ID, "awTable")))
            table_data = driver.execute_script("""
            let table = $('#awTable').DataTable();
            let data = table.rows().data();
            let finalData = Object.entries(data)
            .filter(([key, value]) => !isNaN(Number(key)))
            .reduce((acc, [key, value]) => {
                acc[key] = value;
                return acc;
            }, {});;
            return JSON.stringify(finalData);
            """)

            parsed_data = json.loads(table_data)
            if len(parsed_data.values()) > 0:
                for value in parsed_data.values():
                    user = {}
                    user["person_id"] = value["id"]
                    user["surname"] = value["last_name"]
                    user["first_name"] = value["first_name"]
                    user["date_of_birth"] = value["birth_date"]
                    user["birth_place"] = value["birth_place"]
                    user["client_name"] = value["client_name"]
                    full_name_data_string = value['full_name']
                    full_name_data_list = json.loads(full_name_data_string)
                    user["special_register"] = full_name_data_list

                    if user:
                        data.append(user)

                    time.sleep(10)

            try:
                # open_modal = WebDriverWait(driver, 10).until(
                #     EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Filtri Avanzati')]"))
                # )
                # open_modal.click()


            #     open_modal = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div[1]/div[2]/button")
                back_link = WebDriverWait(driver, 10).until(
                    # EC.presence_of_element_located((By.XPATH, "//a[@class='nav-link' and text()='Nuova ricerca']")))
                    EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-primary' and @data-toggle='modal' and @data-target='#searchModal' and contains(text(), 'Filtri Avanzati')]")))
                # back_link.click()

                driver.execute_script("arguments[0].click();", back_link)

            except Exception as e:
                print(f"Errorhh: {e}")
    except Exception as e:
        print(e)


def export_data(data, name):
    df = pd.DataFrame(data)
    df.to_csv(f"{name}.csv", index=False)
    with open(f"{name}.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(df)  # DEBUG


def main():
    try:
        start_time = time.time()
        df = pd.read_csv(file_path)
        get_data(url=HOMEPAGE, df=df)
        end_time = time.time()
        total_time = end_time - start_time
        print(f"DONE Total time taken: {total_time} seconds")
    except Exception as e:
        print(f"Errotttr: {e}")
    finally:
        export_data(data, name_of_file)
        with open('/Users/mulukenbogale/PycharmProjects/data_man_project/fnofi_last_index.txt', 'w') as file:
            file.write(str(index_pointer))
        print("The last index was", index_pointer)


main()
