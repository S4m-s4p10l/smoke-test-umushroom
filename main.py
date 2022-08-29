from requests import get
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains


LOGIN = "romankretov@protonmail.com"
PASS1 = "Qwerty321"
PASS2 = "Qwerty123"
RATES = "https://api.exchangerate-api.com/v4/latest/USD"



class MainTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()
        self.driver.get("http://www.umushroom.com/")
        self.currencies = get(RATES).json()['rates']


    def test_Login(self):
        self.driver.find_element(By.XPATH, "//button[normalize-space()='Login']").click()
        login_field = self.driver.find_element(By.XPATH, "//input[@id='email']")
        login_field.send_keys(LOGIN)
        pass_field = self.driver.find_element(By.XPATH, "//input[@placeholder='Password']")
        pass_field.send_keys(PASS1)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        sleep(1)
        self.driver.find_element(By.XPATH, "//span[@class='name']").click()
        self.driver.find_element(By.XPATH, "//a[normalize-space()='Account Settings']").click()
        self.driver.find_element(By.XPATH, "//a[normalize-space()='Change']").click()
        self.driver.find_element(By.XPATH, "//input[@id='oldPassword']").send_keys(PASS1)
        self.driver.find_element(By.XPATH, "//input[@id='password']").send_keys(PASS2)
        self.driver.find_element(By.XPATH, "//input[@id='confirmPassword']").send_keys(PASS2)
        self.driver.find_element(By.XPATH, "//button[@class='transition']").click()
        self.driver.find_element(By.XPATH, "//a[normalize-space()='Change']").click()
        self.driver.find_element(By.XPATH, "//input[@id='oldPassword']").send_keys(PASS2)
        self.driver.find_element(By.XPATH, "//input[@id='password']").send_keys(PASS1)
        self.driver.find_element(By.XPATH, "//input[@id='confirmPassword']").send_keys(PASS1)
        self.driver.find_element(By.XPATH, "//button[@class='transition']").click()
        self.driver.find_element(By.XPATH, "//div[@class='profile-holder relative']//a").click()
        self.driver.find_element(By.XPATH, "//a[normalize-space()='Logout']").click()

    def test_portfolio_in_profile(self):
        self.driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[3]/div[1]/button[1]").click()
        self.driver.find_element(By.XPATH, "//button[normalize-space()='Login']").click()
        self.driver.find_element(By.XPATH, "//input[@id='email']").send_keys(LOGIN)
        self.driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys(PASS1)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.driver.find_element(By.XPATH, "//span[@class='name']").click()
        self.driver.find_element(By.XPATH, "//div[@class='profile-dropdown']//div//a[normalize-space()='My Profile']").click()
        sleep(1)
        self.driver.find_element(By.XPATH, '/html/body/div/div[3]/div/div[2]/div[3]/div/div/div[2]/div/div/div[1]/div/div[1]').click()
        sleep(1)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        portfolio_currency = self.driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[2]/div[2]/span[2]").text
        total_value = float(list(soup.find('div', class_="portfolio-title-area").h2.strong.string.split(" "))[1].replace(",",""))/self.currencies[portfolio_currency]
        cash = float(list(soup.find_all('span', class_="value")[1].string.split(" "))[1].replace(",",""))/self.currencies[portfolio_currency]
        cash_weigth_calc = cash/total_value*100
        cash_weight = float(soup.find_all('span', class_="weight")[1].string.strip("%"))
        with self.subTest():
            self.assertEqual(int(cash_weight), int(cash_weigth_calc), msg="Cash weight is incorrect")
        eq_num = int(self.driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[3]/div[1]/div[1]/span[1]").text.replace("Name (", "").replace(")", ""))
        total_invested_eq = 0
        if eq_num > 4:
            self.driver.find_element(By.XPATH, "//a[normalize-space()='See All Equities']").click()
        #Equities in portfolio
        for i in range(eq_num):
            price_per_share = float(self.driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[3]/div[1]/div[2]/div[{}]/div[3]/span[1]".format(str(i+1))).text.split(" ")[1].replace(",",""))
            shares = int(self.driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[3]/div[1]/div[2]/div[{}]/div[6]/span[1]".format(str(i+1))).text)
            currency = self.driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[3]/div[1]/div[2]/div[{}]/div[3]/span[1]".format(str(i+1))).text.split(" ")[0]
            total_invested_eq += (price_per_share * shares)/self.currencies[currency]
            eq_weight = float(self.driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[3]/div[1]/div[2]/div[{}]/div[8]/span[1]".format(str(i+1))).text.strip("%"))
            calc_eq_weight = ((price_per_share * shares)/self.currencies[currency])/total_value*100
            with self.subTest():
                self.assertAlmostEqual(eq_weight, calc_eq_weight, None, msg="The weight of the equity is incorrect", delta=1)
        #Funds in portfolio
        fnd_num = int(self.driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[3]/div[2]/div[1]/span[1]").text.replace("Name (", "").replace(")",""))
        total_invested_fnd = 0
        for i in range(fnd_num):
            price_per_share = float(self.driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[3]/div[2]/div[2]/div[{}]/div[3]/span[1]".format(str(i + 1))).text.split(" ")[1].replace(",", ""))
            shares = int(self.driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[3]/div[2]/div[2]/div[{}]/div[6]/span[1]".format(str(i + 1))).text)
            currency = self.driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[3]/div[2]/div[2]/div[{}]/div[3]/span[1]".format(str(i + 1))).text.split(" ")[0]
            total_invested_fnd += (price_per_share * shares) / self.currencies[currency]
            fnd_weight = float(self.driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[3]/div[2]/div[2]/div[{}]/div[8]/span[1]".format(str(i + 1))).text.strip("%"))
            calc_fnd_weight = ((price_per_share * shares) / self.currencies[currency]) / total_value * 100
            with self.subTest():
                self.assertAlmostEqual(fnd_weight, calc_fnd_weight, None, msg="The weight of the equity is incorrect",delta=1)
        total_invested = total_invested_eq + total_invested_fnd
        margin = total_invested * 0.05
        invested_both = float(self.driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[4]/div[2]/span[1]").text.split(" ")[3].replace(",", "")) / self.currencies[portfolio_currency]
        with self.subTest():
            self.assertAlmostEqual(invested_both, total_invested, msg="The total invested is incorrect", delta=margin)

    def test_interface(self):
        self.driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[3]/div[1]/button[1]").click()
        self.driver.find_element(By.XPATH, "//button[normalize-space()='Login']").click()
        self.driver.find_element(By.XPATH, "//input[@id='email']").send_keys(LOGIN)
        self.driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys(PASS1)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

    def test_new_portfolio(self):
        self.driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[3]/div[1]/button[1]").click()
        self.driver.find_element(By.XPATH, "//button[normalize-space()='Login']").click()
        self.driver.find_element(By.XPATH, "//input[@id='email']").send_keys(LOGIN)
        self.driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys(PASS1)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        sleep(1)
        self.driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[2]/div[1]/div[3]/a[3]").click()
        self.driver.find_element(By.XPATH, "//span[normalize-space()='New']").click()
        self.driver.find_element(By.XPATH, "//input[@type='text']").send_keys("000")
        self.driver.find_element(By.XPATH, "//button[@class='create-portfolio transition']").click()
        self.driver.find_element(By.XPATH, "//span[normalize-space()='Add New Investments']").click()
        self.driver.find_element(By.XPATH, "//a[@href='/en/browse/stocks']").click()
        self.driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/a[1]/h5[1]").click()
        stock_name = self.driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/h5[1]").text
        stock_isin = self.driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/div[2]/span[2]").text.split(" ")[1]
        stock_valor = self.driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/div[2]/span[4]").text.split(" ")[1]
        stock_price = self.driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/span[1]/strong[1]").text.replace(",", "")
        currancy = self.driver.find_element(By.XPATH,"/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/span[1]").text.split(" ")[0]
        sleep(1)
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[2]/div[2]/div[2]/button[1]/img[1]").click()
        sleep(2)
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[6]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]").click()
        self.driver.find_element(By.XPATH, "//a[normalize-space()='My portfolio']").click()
        shares = floor(1000000 / (float(stock_price) / self.currencies[currancy]))
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[6]/div[1]/div[1]/div[2]/div[1]/div[3]/div[1]/div[1]/input[1]").send_keys(
            Keys.BACKSPACE)
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[6]/div[1]/div[1]/div[2]/div[1]/div[3]/div[1]/div[1]/input[1]").send_keys(
            int(shares * 1.15))
        with self.subTest():
            self.assertEqual(self.driver.find_element(By.XPATH,
                                                      "/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[6]/div[1]/div[1]/div[2]/div[1]/div[3]/div[2]/div[1]/span[1]").text,
                             "You don’t have enough cash to purchase {} shares.".format(int(shares * 1.15)))
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[6]/div[1]/div[1]/div[2]/div[1]/div[3]/div[1]/div[1]/input[1]").clear()
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[6]/div[1]/div[1]/div[2]/div[1]/div[3]/div[1]/div[1]/input[1]").send_keys(
            shares)
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[6]/div[1]/div[1]/div[2]/div[1]/button[1]").click()
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[6]/div[1]/div[1]/div[1]/div[1]/button[2]").click()
        sleep(2)
        with self.subTest():
            self.assertEqual(stock_name, self.driver.find_element(By.XPATH,
                                                                  "/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[5]/div[2]/div[1]/div[1]/a[1]/div[1]/h5[1]").text)
        with self.subTest():
            self.assertEqual(stock_valor, self.driver.find_element(By.XPATH,
                                                                   "/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[5]/div[2]/div[1]/div[1]/a[1]/div[1]/p[1]/span[2]").text.split(
                " ")[1])
        with self.subTest():
            self.assertEqual(stock_isin, self.driver.find_element(By.XPATH,
                                                                  "/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[5]/div[2]/div[1]/div[1]/a[1]/div[1]/p[1]/span[1]").text.split(
                " ")[1])
        hover = ActionChains(self.driver).move_to_element(self.driver.find_element(By.XPATH,
                                                                                   "/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[5]/div[2]/div[1]/div[6]"))
        hover.perform()
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[5]/div[2]/div[1]/div[8]/a[1]/img[1]").click()
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[3]/div[1]/div[1]/div[3]/div[1]/div[1]/input[1]").clear()
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[3]/div[1]/div[1]/div[3]/div[1]/div[1]/input[1]").send_keys(
            "0")
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[3]/div[1]/div[1]/div[3]/button[1]").click()
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[3]/div[1]/div[1]/button[1]").click()
        self.driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[2]/div[1]/div[3]/a[3]").click()
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[3]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[3]/div[1]/a[1]/img[1]").click()
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[3]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[3]/div[1]/div[1]/a[2]").click()
        self.driver.find_element(By.XPATH,
                                 "/html[1]/body[1]/div[1]/div[3]/div[1]/div[2]/div[3]/div[2]/div[1]/div[1]/button[1]").click()





    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()