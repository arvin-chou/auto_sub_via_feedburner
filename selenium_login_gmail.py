import os.path
import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

username = 'xxx'
if 'SUSERNAME' in os.environ:
     username = os.environ['SUSERNAME']

password = 'xxx'
if 'PASSWORD' in os.environ:
     password = os.environ['PASSWORD']
#
# feed_list_fname seperate line by \n
#
feed_list_fname = 'test'
if 'FEED_LIST_FNAME' in os.environ:
     feed_list_fname = os.environ['FEED_LIST_FNAME']

#
# new_feed_urls seperate line by \n
#
new_feed_url_fname = 'feed'
if 'NEW_FEED_URL_FNAME' in os.environ:
     new_feed_url_fname = os.environ['NEW_FEED_URL_FNAME']

new_feed_url = 'xxx'
if 'NEW_FEED_URL' in os.environ:
     new_feed_url = os.environ['NEW_FEED_URL']

subscribe = 'xxx'
if 'SUBSCRIBE' in os.environ:
     subscribe = os.environ['SUBSCRIBE']

#print('your input:', username, password, feed_list_fname, new_feed_url_fname, new_feed_url, subscribe)

feed_list = []
new_feed_urls = []
out = []
home = 'http://feedburner.google.com'

def get_list(fname, olist):
    with open(fname) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    olist = [x.strip() for x in content] 
    return olist

def auto_sub(driver, sub_link, subscribe):
    driver.get(sub_link)
    elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name=email]")))
    elem.send_keys(subscribe)
    elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".recaptcha-checkbox-border")))
    elem.click()
    # check if it needs manual verify
    elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".recaptcha-checkbox-checkmark")))
    if elem.is_displayed():
        print("auto sub")
        elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type=submit]")))
        elem.click()
    else:
        print("sub fail, plz manual goto", sub_link)


driver = webdriver.Chrome()
driver.get(home)
wait = WebDriverWait(driver, 10)

# user name
elem = driver.find_element_by_id("identifierId")
elem.send_keys(username)
elem.send_keys(Keys.RETURN)

# password
elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type=password]")))
elem.send_keys(password)
elem.send_keys(Keys.RETURN)

# after login success
mytable = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'table')))

if os.path.isfile(feed_list_fname):
    print("ONLY get feed list from file") 
    feed_list = get_list(feed_list_fname, feed_list)

else:
    print("get feeded list...")
    for row in mytable.find_elements_by_css_selector('td.title a'):
        feed_list.append(row.text)

if os.path.isfile(new_feed_url_fname):
    print("get new feeds list...")
    new_feed_urls = get_list(new_feed_url_fname, new_feed_urls)

else:
    print("get feed")
    new_feed_urls.append(new_feed_url)


for new_feed_url in new_feed_urls:
    print("check new feed", new_feed_url)

    elem = wait.until(EC.visibility_of_element_located((By.ID, 'tonkatsu')))
    elem.send_keys(new_feed_url)
    elem.send_keys(Keys.RETURN)
    feeds = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name=sourceUrl]')))
    if feeds:
        next_step = driver.find_element_by_css_selector('input[type=submit]')
        next_step.click()
        is_got = False
        try:
            elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name=name]")))
            feed_name = elem.get_attribute("value")
            print("feedname is ", feed_name)
            is_got = True
        except:
            print("no rss url from", new_feed_url)

        if feed_name in feed_list or not is_got:
            if not is_got:
                driver.get(home)

            else:
                print("already subed, next")
                next_step = driver.find_element_by_css_selector('#deactivate')
                next_step.click()

        else:
            # new feed
            feed_list.append(feed_name)
            #print("now feed_list is ", feed_list)
            next_step = driver.find_element_by_css_selector('input[type=submit]')
            next_step.click()

            # register new sub
            elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.formAction a")))
            elem.click()

            elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#tabs ul")))
            for li in elem.find_elements_by_css_selector('li a'):
                if li.text.lower().startswith('public'):
                    li.click()

                    elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#servicesList")))
                    is_got = False
                    # change sub setting page
                    for li in elem.find_elements_by_css_selector('li a'):
                        if li.text.lower().startswith('email'):
                            li.click()

                            elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.formAction input[value=Activate]")))
                            elem.click()

                            elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a#previewLink")))
                            sub_link = elem.get_attribute("href")
                            is_got = True
                            out.append(sub_link)
                            print("sub link", sub_link)

                            # goto sub link
                            #auto_sub(driver, sub_link, subscribe)

                            break

                    if is_got:
                        driver.get(home)
                        break
    else:
        print("not found rss")

print("output sub link to out_sub_link")
with open('out_sub_link', 'w') as f:
    for item in out:
        print(item)
        f.write("%s\n" % item)
