# -*- coding: utf-8 -*-

from selenium import webdriver
from time import sleep


URL = 'https://www.cian.ru/cat.php?currency=2&deal_type=sale&engine_version=2&maxprice=18000000&metro%5B0%5D=116&minprice=14000000&offer_type=flat&parking_type%5B0%5D=1&parking_type%5B1%5D=2&parking_type%5B2%5D=3&room2=1'


def go(driver, url):
    driver.get(url)
    
    print("========")
    body = driver.find_element_by_tag_name('body')
    print( body.text )
    print( 'a', body.find_elements_by_tag_name('a') )

    sleep(1)
    offers = body.find_elements_by_xpath("//div[contains(@class,'offer-container')]")
    print( len(offers) )
    for offer in offers:
        print( offer.tag_name, offer.get_attribute('class') )
        img = offer.find_elements_by_tag_name("img")
        for i in img:
            print( '-', i.get_attribute('src') )

    sleep(15)

    
    for d in body.find_elements_by_tag_name('div'):
        if 'offerInfo' in d.get_attribute('class'):
            print( '***' )
            print( d )
            print( d.get_attribute('class'), d.id )
            print( d.text )
            print( 'Go deeper' )
            for ch in d.find_elements_by_tag_name('div'):
                print ('-')
                print (ch.id, ch.get_attribute('class'))
                print (ch.text)
    


if __name__ == '__main__':
    # driver = webdriver.Chrome('/home/stnslv/realty/chromedriver')
    driver = webdriver.PhantomJS()
    print("start")
    driver.implicitly_wait(5)
    go(driver, URL)
    driver.quit()
