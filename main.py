from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pretty_html_table import build_table
import os

URL = "https://store.steampowered.com/specials/"

# Keep Chrome browser open after program finishes
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(20)
driver.get(URL)
driver.execute_script("window.scrollTo(0, 1000);")

discount_games_list = []
discount_percent_list = []
price_after_discount_list = []

parent_elements = driver.find_elements(By.CLASS_NAME, 'ImpressionTrackedElement')
print(len(parent_elements))
for parent in parent_elements:

    discount_games = parent.find_element(By.CLASS_NAME, '_2eQ4mkpf4IzUp1e9NnM2Wr')
    discount_games_list.append(discount_games.get_attribute('alt'))

    price_after_discount = parent.find_element(By.CLASS_NAME, '_3j4dI1yA7cRfCvK8h406OB')
    price_after_discount_list.append(price_after_discount.text)

    try:
        # Attempt to find the element
        discount_percent = parent.find_element(By.CLASS_NAME, 'cnkoFkzVCby40gJ0jGGS4')
    except NoSuchElementException:
        discount_percent_list.append('-0%')
    else:
        discount_percent_list.append(discount_percent.text)

for item in price_after_discount_list:
    if item == 'Prepurchase':
        discount_games_list.pop(price_after_discount_list.index(item))
        discount_percent_list.pop(price_after_discount_list.index(item))
        price_after_discount_list.pop(price_after_discount_list.index(item))

data = {
    "Games": discount_games_list,
    "Discount": discount_percent_list,
    "Price_After_Discount": price_after_discount_list
}

df = pd.DataFrame(data)
df['Discount'] = df['Discount'].str.strip("-")
df_sorted = df.sort_values('Discount', ascending=False)
df_sorted_selected = df_sorted.head(10)
print(df_sorted_selected)
# df_sorted_selected.to_csv("data.csv")

sender_email = os.environ.get('sender_email')
receiver_email = os.environ.get('receiver_email')
password = os.environ.get('password')

subject = "Top 10 Steam Daily Discount Games"
body = """
<html>
  <body>
    <p>Hello,</p>
    <p>Here are the top 10 discount games on Steam for today!</p>
    <p>{0}</p>
    <p>https://store.steampowered.com/specials/</p>
    <p>Best regards,<br>Your Python Script</p>
  </body>
</html>
""".format(build_table(df_sorted_selected, color="orange_light"))

try:
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
