from selenium import webdriver
from bs4 import BeautifulSoup
import os,requests,random

#搜尋圖片
def search_imgs(num,driver):   
    photo = []
    count = 0
    count_flag = 0
    y = 0
    while True:
        flag = 0
        soup = BeautifulSoup(driver.page_source,'lxml')
        imgs = soup.find_all('img')
        
        #搜尋關鍵字，找不到圖片，輸出文字
        try:
            e_msg = soup.find('div',class_="tBJ dyH iFc j1A O2T zDA swG").text
            print(e_msg)
            return e_msg
        except:
            pass

        #儲存第一張圖片位置
        try:
            if count == 0: 
                img_id = soup.find('div',attrs={'data-test-id':"pin"})['data-test-pin-id']
                img_url = ''.join(['https://www.pinterest.com/pin/',img_id])
                print('已獲取img_url:',img_url)
        except:
            print('img_url有問題重試')
            continue

        
        for i in imgs:
            if num != count:
                img = i['src']
                if '236x' in img:
                    img = img.replace('236x','originals')
                    if img not in photo:
                        photo.append(img)
                        count += 1
                        flag = 1
            else:
                print(f'數量:{count}張，已捕獲完成') 
                return photo
            
        #比較資料庫檔案數量，如果頁面到底部無法再儲存新圖片，累計50次跳轉新頁面
        if not flag:
            if count_flag == 50:
                driver.get(img_url)
                print('轉換新頁面繼續抓圖')
                count_flag = 0
            else:
                count_flag +=1
        else:
            count_flag = 0
            
        #數量不夠，拉動卷軸
        if num != count:
            y+=1000
            scroll_page(driver,y)
#轉動卷軸
def scroll_page(driver,y):
    driver.execute_script(f'window.scrollTo(0,{y})')

        
#★檔案格式比對
def check_filetype(url):
    
    if '.jpg' in url:
        url = url.replace('.jpg','.png')
        return url
    elif '.png' in url:
        url = url.replace('.png','.gif')
        return url
    elif '.gif' in url:
        url = url.replace('.gif','.webp')
        return url
    else:
        print(url,'有問題')

#★隨機選圖片
def random_pic(links,num):
    #判斷列表內容
    if not links:
        print('列表已空')
        return None
            
    
    imgs = []
    
    while num:
        pic = random.choice(links) #隨機亂選一張圖片
        r = requests.get(pic)

        if r.ok: #網路測試
            if '.gif' in pic: 
                links.pop(links.index(pic.replace('.gif','.jpg'))) #從列表中刪除
                print('刪除:',pic)
                return random_pic(links) #回傳自己本身
            elif '.webp' in pic: 
                links.pop(links.index(pic.replace('.webp','.jpg'))) #從列表中刪除
                print('刪除:',pic)
                return random_pic(links) #回傳自己本身
            #line_notify(pic) #Line Notify 傳送
            imgs.append(pic) 
            num-=1
            if '.png' in pic:
                links.pop(links.index(pic.replace('.png','.jpg'))) #從列表中刪除
            links.pop(links.index(pic)) #一樣的排除
            
        else:
            pic = check_filetype(pic) #資料比對
    return imgs
            

#主程式    
def pin_search(keyword,num):
    URL = 'https://www.pinterest.com/search/pins/?q='

    #option = webdriver.ChromeOptions()
    #option.add_argument('headless')
    #driver = webdriver.Chrome('..\..\..\爬蟲\Selenium\chromedriver.exe',options=option)

    #keyword = input('請輸入要搜尋的關鍵字:')
    #num = int(input('輸入圖片數量:'))

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless") #無頭模式
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)


    driver.get(URL+keyword)


    #圖片連結
    links = search_imgs(100,driver)
    #判斷有無搜尋到圖片
    if type(links) == str:
        driver.quit()
        return links

    imgs = random_pic(links,num)
    #print(imgs)
    driver.quit()
    return imgs

    '''
        #隨機選圖片
        key = int(input('想要傳送幾個圖片連結:'))

        for i in range(key):
            random_pic(links)
        #links = []
    '''

    
