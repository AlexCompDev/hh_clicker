from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
)
import time
import os  # Чтение данных из файла user_data.txt


def read_user_data(file_path):
    user_data = {}

    with open(file_path, "r") as f:
        for line in f:
            # Пропускаем пустые строки и комментарии

            if line.strip() and not line.startswith("#"):
                key, value = line.split("=", 1)

                user_data[key.strip()] = value.strip().strip('"')

    return user_data


# Считываем данные

data = read_user_data("user_data.txt")

LOGIN = data.get("LOGIN")

PASSWORD = data.get("PASSWORD")

base_url = data.get("base_url")

vacancy_title = data.get("vacancy_title")

# Создаем экземпляр драйвера Chrome
driver = webdriver.Chrome()

# Переходим на сайт https://hh.ru/
driver.get("https://hh.ru/")

# Ждем загрузки страницы
driver.implicitly_wait(5)

# Check for captcha
captcha_locator = (
    By.XPATH,
    "//h1[@data-qa='title' and contains(text(), 'Подтвердите, что вы не робот')]",
)

while True:
    try:
        captcha_element = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located(captcha_locator)
        )
        input("Введите капчу и авторизуйтесь, затем нажмите Enter...")
    except TimeoutException:
        break

# Найдем первую кнопку по XPath
button1 = driver.find_element(By.XPATH, "//*[contains(text(), 'Войти')]")

# Произведем клик по первой кнопке
button1.click()

# Ждем загрузки страницы
driver.implicitly_wait(2)

# Найдем вторую кнопку по XPath
button2 = driver.find_element(
    By.XPATH,
    '//*[@id="HH-React-Root"]/div/div[2]/div[4]/div[1]/div/div/div/div/div/div/div/div/div[1]/div/div/div/div[3]/form/div[5]/div/a/span/span',
)

button2.click()

# Ждем загрузки страницы
driver.implicitly_wait(2)

# Найдем поле ввода e-mail по XPath
input_field_email = driver.find_element(
    By.XPATH,
    '//*[@id="HH-React-Root"]/div/div[2]/div[4]/div[1]/div/div/div/div/div/div/div/div/div[1]/div/div/div/form/div[1]/div/div/div[2]/div[1]/input',
)
# Вводим текст в поле e-mail
input_field_email.send_keys(LOGIN)

# Найдем поле ввода пароля по XPath
input_field_password = driver.find_element(
    By.XPATH,
    '//*[@id="HH-React-Root"]/div/div[2]/div[4]/div[1]/div/div/div/div/div/div/div/div/div[1]/div/div/div/form/div[3]/div[1]/div[1]/div[2]/div[1]/input',
)


# Вводим текст в поле пароля
input_field_password.send_keys(PASSWORD)

# Найдем кнопку входа по XPath
login_button = driver.find_element(
    By.XPATH,
    '//*[@id="HH-React-Root"]/div/div[2]/div[4]/div[1]/div/div/div/div/div/div/div/div/div[1]/div/div/div/form/div[8]/button/div/span/span',
)

# Произведем клик по кнопке входа
login_button.click()

# Ждем загрузки страницы
driver.implicitly_wait(2)

# Ждем, пока пользователь введет капчу и авторизуется
input("Введите капчу и авторизуйтесь, затем нажмите Enter...")

# поднимаем резюме по кнопке
button1 = driver.find_elements(By.XPATH, "//button[contains(text(), 'Поднять')]")
button2 = driver.find_elements(
    By.XPATH, "//div[@data-qa='applicant-index-nba-action_update-resumes']"
)

if button1:
    button1[0].click()
elif button2:
    button2[0].click()


# Check for captcha again
while True:
    try:
        captcha_element = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located(captcha_locator)
        )
        input("Введите капчу и авторизуйтесь, затем нажмите Enter...")
    except TimeoutException:
        break


# Check for captcha again
try:
    captcha_element = WebDriverWait(driver, 1).until(
        EC.presence_of_element_located(captcha_locator)
    )
    input("Введите капчу и авторизуйтесь, затем нажмите Enter...")
except TimeoutException:
    pass

# Создаем файл links.txt и сохраняем все ссылки на вакансии
with open("links.txt", "w") as f:
    page = 0

    while True:
        # Формируем URL с учетом номера страницы
        url = f"{base_url}&page={page}"
        driver.get(url)

        # Ожидаем загрузки элементов с вакансиями
        try:
            vacancies = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "span[data-qa='serp-item__title-text']")
                )
            )
        except TimeoutException:
            print(f"Не удалось загрузить вакансии на странице {page}.")
            break

        if not vacancies:
            print(f"На странице {page} вакансий не найдено.")
            break

        # Обрабатываем все вакансии на текущей странице
        for vacancy in vacancies:
            # Получаем родительский элемент, чтобы найти ссылку
            vacancy_link = vacancy.find_element(By.XPATH, "./ancestor::a")
            href = vacancy_link.get_attribute("href")

            # Записываем ссылку в файл
            f.write(f"{href}\n")

            # Выводим название вакансии в терминал
            vacancy_name = vacancy.text  # Используем .text для получения названия
            print(f"Вакансия найдена: {vacancy_name}")

        # Увеличиваем номер страницы
        page += 1

print("Файл links.txt создан успешно")

# Проверяем, если файл links.txt пустой, то ждем 10 секунд и проверяем снова
for i in range(4):
    if os.path.getsize("links.txt") == 0:
        print(f"Файл links.txt пустой, ждем 10 секунд и проверяем снова ({i+1}/4)")
        time.sleep(10)
    else:
        break
else:
    print("Файл links.txt остался пустым после 4 попыток")
    exit()

# Переходим по каждой ссылке из файла links.txt
try:
    with open("links.txt", "r") as f:
        for link in f.readlines():
            link = link.strip()
            try:
                driver.get(link)
                driver.implicitly_wait(2)

                # Проверяем наличие капчи снова
                try:
                    element_captcha = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located(captcha_locator)
                    )
                    input("Введите капчу и авторизуйтесь, затем нажмите Enter...")
                except TimeoutException:
                    pass

                # Ждем загрузки страницы
                time.sleep(3)

                # Найти кнопку "Откликнуться"
                button_response = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//span[text()='Откликнуться']/ancestor::a")
                    )
                )
                button_response.click()

                # Дождаться появления модального окна ответа
                WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.ID, "RESPONSE_MODAL_FORM_ID"))
                )

                # Найти элемент с текстом названия вакансии
                try:
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                "//*[contains(text(), '{}')]".format(vacancy_title),
                            )
                        )
                    )
                    element.click()

                except TimeoutException:
                    with open("bad.txt", "a") as f:
                        f.write(link + "\n")
                    continue

                # Найти кнопку "Сопроводительное письмо"
                button_letter = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//button[@data-qa='vacancy-response-letter-toggle']",
                        )
                    )
                )
                try:
                    button_letter.click()
                except ElementClickInterceptedException:
                    with open("bad.txt", "a") as f:
                        f.write(link + "\n")
                    continue

                # Найти элемент текстовой области
                text_area = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//textarea[@data-qa='vacancy-response-popup-form-letter-input']",
                        )
                    )
                )

                # Прочитать текст из файла cv.txt
                with open("cv.txt", "r") as f:
                    text_from_file = f.read()

                # Ввести текст в текстовую область
                text_area.send_keys(text_from_file)

                # Ждем 4 секунды перед закрытием модального окна
                time.sleep(4)

                # Найти кнопку "Откликнуться"
                button_response_locator = (
                    By.XPATH,
                    "//button/span[text()='Откликнуться']",
                )

                try:
                    button_response = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(button_response_locator)
                    )
                    button_response.click()
                    print("Успешно! Кнопка 'Откликнуться' найдена и кликнута.")
                except:
                    print("Неудача! Кнопка 'Откликнуться' не найдена.")

                    time.sleep(7)

            except Exception as e:
                print(f"Ошибка: {e}")
                with open("bad.txt", "a") as f:
                    f.write(link + "\n")
                continue

    print("Скрипт завершился без ошибок!")
finally:
    driver.quit()
