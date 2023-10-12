
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from uuid import uuid4
from os import getenv
import requests
from bs4 import BeautifulSoup
# from time import sleep
import re

load_dotenv()
TESTMAIL_NAMESPACE = getenv("TESTMAIL_NAMESPACE")
TESTMAIL_API = getenv("TESTMAIL_API")

with sync_playwright() as p:
    browser = p.firefox.launch(headless=False)
    page = browser.new_page()

    mail_tag = uuid4()
    mail_newsletter = f'{TESTMAIL_NAMESPACE}.{mail_tag}@inbox.testmail.app'

    page.goto("https://cropp.com/ro/ro/newsletter")
    cookies_button = page.wait_for_selector("#cookiebotDialogOkButton")
    cookies_button.click()
    
    page.wait_for_selector("#newsletterTerms").set_checked(True)
    page.wait_for_selector("#newsletterMail").fill(mail_newsletter)
    page.wait_for_selector("button.newsletter-submit").click()
    # sleep(3)
    api_endpoint_confirmation_mail = f'https://api.testmail.app/api/json?apikey={TESTMAIL_API}&namespace={TESTMAIL_NAMESPACE}&tag={mail_tag}&limit=1&livequery=true'
    
    _result = requests.get(api_endpoint_confirmation_mail)
    response = _result.json()

    html_mail_confirmation = BeautifulSoup(response["emails"][0]["html"], "html.parser")
    confirmation_link = html_mail_confirmation \
        .find("strong", string=re.compile("CONFIRM")) \
        .findParent("a") \
        .attrs["href"]

    page.goto(confirmation_link)
    # sleep(3)
    timestamp: int = response["emails"][0]["timestamp"] + 1
    API_ENDPOINT_CODE_MAIL = f"https://api.testmail.app/api/json?apikey={TESTMAIL_API}&namespace={TESTMAIL_NAMESPACE}&tag={mail_tag}&limit=1&timestamp_from={timestamp}&livequery=true"

    tempmail_code_req = requests.get(API_ENDPOINT_CODE_MAIL)
    tempmail_code_json = tempmail_code_req.json()

    code_html = BeautifulSoup(tempmail_code_json["emails"][0]["html"], "html.parser")
    coupon = code_html.find("span", attrs={"style": "font-family: Arial; font-size: 26px;"}).text

    print(coupon)

    link_unsub = code_html.find("a", attrs={"style": "color: #4b4747 !important; text-decoration: underline !important;"}).attrs["href"]

    page.goto(link_unsub)
    # sleep(3)
    unsub_btn = page.wait_for_selector("#ES-Main-Box > form > table > tbody > tr:nth-child(4) > td > input:nth-child(1)")
    unsub_btn.click()

    # sleep(10)