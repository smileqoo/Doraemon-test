from linebot import LineBotApi,WebhookHandler
from linebot.exceptions import InvalidSignatureError
from flask import Flask,request,abort
from linebot.models import MessageEvent,PostbackEvent,TextMessage,TextSendMessage,TemplateSendMessage,ButtonsTemplate,PostbackAction,MessageAction,URIAction,QuickReply,QuickReplyButton,ImageSendMessage
import pinterest
import os


app = Flask(__name__)

#訊息建立
line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))

#全局變數
img_urls = []


@app.route('/',methods=['POST'])
def callback():
    body = request.get_data(as_text=True) #★這邊要改成True
    signature = request.headers['X-Line-Signature']
    try:
        handler.handle(body,signature)
    except InvalidSignatureError:
        abort(400)
    return 'ok'

#訊息
@handler.add(MessageEvent,message=TextMessage)
def handler_message(event):
    print(event)
    mtext = event.message.text
    reply_tk = event.reply_token

    if 'pin' in mtext[0:3] :
        reply_quick(mtext,reply_tk)
    elif '準備隨機傳送' in mtext:
        reply_img(reply_tk)
            
#Postback訊息
@handler.add(PostbackEvent)
def handler_postback(event):
    print(event)
    data = event.postback.data
    name,num = data.split(',')
    global img_urls
    img_urls = pinterest.pin_search(name,int(num))
    #print(img_urls)

    #搜尋不到回傳訊息
    if isinstance(img_urls,str):
        re_tk = event.reply_token
        line_bot_api.reply_message(re_tk,TextSendMessage(text=img_urls))    

#快速回復-選單
def reply_quick(text,re_tk):
    try:
        name = text.split(',')[1]
        message = TextSendMessage(text=f'請問要隨機傳送幾張 "{name}" 圖片???',
                                  quick_reply=QuickReply(
                                      items=[
                                          QuickReplyButton(action=PostbackAction(label='1張',text='1張，準備隨機傳送...',data=f'{name},1')),
                                          QuickReplyButton(action=PostbackAction(label='3張',text='3張，準備隨機傳送...',data=f'{name},3')),
                                          QuickReplyButton(action=PostbackAction(label='5張',text='5張，準備隨機傳送...',data=f'{name},5'))
                                          ]
                                      )
                                  )
        line_bot_api.reply_message(re_tk,message)
    except:
        message = TextSendMessage(text='pin搜尋標準格式，"pin,搜尋名稱"')
        line_bot_api.reply_message(re_tk,message)

#傳送圖片
def reply_img(re_tk):
    links =[]
    for i in img_urls:
        message = ImageSendMessage(original_content_url=i,preview_image_url=i)
        links.append(message)
    line_bot_api.reply_message(re_tk,links)

