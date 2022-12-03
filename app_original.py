from flask import Flask,request,abort
from linebot import LineBotApi,WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage,TemplateSendMessage,ImageSendMessage,ConfirmTemplate,QuickReply,QuickReplyButton,MessageAction,PostbackAction
import json,os
import pinterest
#from selenium import webdriver

app = Flask(__name__)

#selenium先開啟待機
'''
option = webdriver.ChromeOptions()
option.add_argument('headless')
driver = webdriver.Chrome('..\..\..\爬蟲\Selenium\chromedriver.exe',options=option)
'''

#訊息建立
line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))

#數量變數
name,num =0,0


@app.route('/',methods=['POST'])
def callback():

    try:
        body = request.get_data(as_text=True)
        json_data = json.loads(body)
        signature = request.headers['X-Line-Signature'] #大小寫都可以
        handler.handle(body,signature)
        print(json_data)

        
        
        reply_quick(json_data)
        postback_event(line_bot_api,json_data)
        

        
            

               
    except InvalidSignatureError:
        abort(400)

    return 'ok'

def reply_quick(json_data):
    
    if json_data['events'][0]['type'] == 'message':
        reply_token = json_data['events'][0]['replyToken']
        msg = json_data['events'][0]['message']['text']
        try:
            global name
            if 'pin' in msg[:3] :
                name = msg.split(',')[1]

                message = TextSendMessage(text=f'請問要傳送幾張 "{name}" 圖片???',
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(action=PostbackAction(label='1張',text='1張',data=f'{name},1')),
                                    QuickReplyButton(action=PostbackAction(label='3張',text='3張',data=f'{name},3')),
                                    QuickReplyButton(action=PostbackAction(label='5張',text='5張',data=f'{name},5')),
                                            ]
                                        )
                                    )
                line_bot_api.reply_message(reply_token,message)

        except:
            message = TextSendMessage(text='pin搜尋標準格式，"pin,搜尋名稱"')
            line_bot_api.reply_message(reply_token,message)

       
def postback_event(line_bot_api,json_data):
    global name,num    
    if json_data['events'][0]['type'] =='postback':
        reply_token = json_data['events'][0]['replyToken']
        value = json_data['events'][0]['postback']['data']

        if value =='確定':
            print(reply_token)
            img_urls = pinterest.pin_search(name,int(num))
            #判斷回傳是否字串
            if isinstance(img_urls,str):
                line_bot_api.reply_message(reply_token,TextSendMessage(text=img_urls))
            else:
                reply_img(reply_token,img_urls)
            
        else:
            
            
            name,num = value.split(',')
        
            #message = TextSendMessage(text=f'"{name}"圖片，準備傳送{num}張...\nloading...')
            message = TemplateSendMessage(alt_text='確認樣板',
                                          template=ConfirmTemplate(text=f'"{name}"圖片，準備傳送{num}張......',
                                                               actions=[PostbackAction(label='確定',data='確定'),
                                                                        PostbackAction(label='取消',data='取消')]))
            line_bot_api.reply_message(reply_token,message)       
        
def reply_img(reply_token,img_urls):
    message = []
    for i in range(len(img_urls)):
        #print(img_urls[i])
        message.append(ImageSendMessage(original_content_url=img_urls[i],preview_image_url=img_urls[i]))
    line_bot_api.reply_message(reply_token,message)
    
    

