import os
import json
import gspread
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# 환경변수에서 읽기
BOT_TOKEN = os.environ["BOT_TOKEN"] # 슬랙 봇 토큰 - api.slack.com → OAuth & Permissions → Bot User OAuth Token (xoxb-...)

APP_TOKEN = os.environ["APP_TOKEN"] # 슬랙 앱 토큰 - api.slack.com → Basic Information → App-Level Tokens (xapp-...)

SHEET_ID  = os.environ["SHEET_ID"] # 구글 스프레드시트 ID - 시트 URL에서 /d/ 뒤에 오는 긴 문자열

CALENDAR_ID = os.environ["CALENDAR_ID"] # 구글 캘린더 ID - 캘린더 설정 → 캘린더 통합 섹션 (xxx@group.calendar.google.com)

# 구글 인증 (시트 + 캘린더 둘 다)
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar"
]
creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)

# 구글 시트 연결
gc    = gspread.authorize(creds)
sheet = gc.open_by_key(SHEET_ID).sheet1

# 구글 캘린더 연결
calendar_service = build("calendar", "v3", credentials=creds)

# 슬랙 앱 초기화
app = App(token=BOT_TOKEN)

# /기록 커맨드 처리
@app.command("/기록")
def handle_record(ack, respond, say, command):
    ack()
    text  = command["text"].strip()
    parts = [p.strip() for p in text.split("_")]
    if len(parts) < 2:
        respond("형식이 올바르지 않아요!")
        return
    
    user_id = command["user_id"]  # 입력한 사람 슬랙 ID
    sheet.append_row(parts)
    say(f"✅ <@{user_id}>님이 기록했어요!\n{' _ '.join(parts)}")

# /일정 커맨드 처리
@app.command("/일정")
def handle_calendar(ack, respond, command):
    ack()
    text = command["text"].strip()
    parts = [p.strip() for p in text.split("_")]
    if len(parts) != 4:
        respond("형식이 올바르지 않아요!\n예시: `/일정 팀 회의_2025-04-03_14:00_15:00`")
        return
    title, date, start_time, end_time = parts
    event = {
        "summary": title,
        "start": {
            "dateTime": f"{date}T{start_time}:00",
            "timeZone": "Asia/Seoul"
        },
        "end": {
            "dateTime": f"{date}T{end_time}:00",
            "timeZone": "Asia/Seoul"
        }
    }
    try:
        calendar_service.events().insert(
            calendarId=CALENDAR_ID, body=event
        ).execute()
        respond(f"✅ 일정 추가 완료!\n📅 {title}\n🕐 {date} {start_time} ~ {end_time}")
    except Exception as e:
        respond(f"❌ 오류가 발생했어요: {str(e)}")

# 실행
if __name__ == "__main__":
    SocketModeHandler(app, APP_TOKEN).start()