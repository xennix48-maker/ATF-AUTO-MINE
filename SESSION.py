from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Your API credentials
API_ID = 28752231
API_HASH = 'ec1c1f2c30e2f1855c3edee7e348480b'

# Session name
SESSION_NAME = "atf_miner"

def main():
    print("=== Telegram Session Creator (2FA Supported) ===")

    phone = input("Enter your phone number (with country code): ")

    with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        client.connect()

        if not client.is_user_authorized():
            client.send_code_request(phone)
            code = input("Enter the code you received: ")

            try:
                client.sign_in(phone, code)

            except SessionPasswordNeededError:
                # 2FA enabled
                password = input("Enter your 2FA password: ")
                client.sign_in(password=password)

        print("\n✅ Session created successfully!")
        print(f"Saved as: {SESSION_NAME}.session")

if __name__ == "__main__":
    main()