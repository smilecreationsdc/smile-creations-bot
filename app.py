import os
from flask import Flask, request
import anthropic
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])
claude = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

SYSTEM_PROMPT = """คุณคือผู้ช่วยตอบคำถามของ Smile Creations Dental Clinic 
คลินิกทันตกรรมย่านสะพานควาย กรุงเทพฯ

ข้อมูลคลินิก:
- ที่อยู่: 698/10 Ideo Mix ชั้น 2 ถนนพหลโยธิน พญาไท กทม. 10400 (BTS สะพานควาย ทางออก 4)
- โทร: 097-297-4610
- Line ID: 0972974610
- เปิดทุกวัน 10:00-20:00 น. (นัดเคสสุดท้าย 19:00 น.)
- บริการ: ทันตกรรมทุกประเภท เช่น อุดฟัน ถอนฟัน ขูดหินปูน จัดฟัน รากฟันเทียม วีเนียร์ ครอบฟัน รักษารากฟัน ฟอกสีฟัน

วิธีตอบ:
- ตอบภาษาไทย กระชับ เป็นกันเอง
- ถ้าถามเรื่องราคา ให้บอกว่าต้องมาตรวจก่อนเพื่อประเมินราคาที่แน่นอน
- ถ้าอยากนัด ให้แนะนำทักไลน์ 0972974610 หรือโทร 097-297-4610
- ห้ามวินิจฉัยโรคหรือแนะนำยาเอง"""

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    keywords = ["มีวันไหนว่าง", "ขอนัด", "จองคิว", "เลื่อนนัด", "ยกเลิกนัด", "ตารางว่าง", "วันไหนว่าง", "คิวว่าง"]
    if any(k in user_message for k in keywords):
        return

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )
    reply_text = response.content[0].text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run(port=5000)
