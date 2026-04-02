import os
import json
import gspread
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from google.oauth2.service_account import Credentials

# 환경변수에서 읽기
BOT_TOKEN = os.environ["BOT_TOKEN"]
APP_TOKEN = os.environ["APP_TOKEN"]
SHEET_ID  = os.environ["SHEET_ID"]

# 구글 시트 연결
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds  = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
gc     = gspread.authorize(creds)
sheet  = gc.open_by_key(SHEET_ID).sheet1

# 슬랙 앱 초기화
app = App(token=BOT_TOKEN)

# /기록 커맨드 처리
@app.command("/기록")
def handle_record(ack, respond, command):
    ack()
    text  = command["text"].strip()
    parts = [p.strip() for p in text.split("|")]
    if len(parts) < 2:
        respond("형식이 올바르지 않아요!\n예시: `/기록 홍길동 | 2025-04-02 | 사과 | 50개`")
        return
    sheet.append_row(parts)
    respond(f"✅ 기록 완료! {' | '.join(parts)}")

# 실행
if __name__ == "__main__":
    SocketModeHandler(app, APP_TOKEN).start()