import threading
import time
import random
import string
from zlapi import ZaloAPI, ThreadType, Message, Mention
from config import API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES
from collections import defaultdict

class Bot(ZaloAPI):
    def __init__(self, api_key, secret_key, imei=None, session_cookies=None):
        super().__init__(api_key, secret_key, imei, session_cookies)
        self.running = False

    def fetchGroupInfo(self):
        try:
            all_groups = self.fetchAllGroups()
            group_list = []
            for group_id, _ in all_groups.gridVerMap.items():
                group_info = super().fetchGroupInfo(group_id)
                group_name = group_info.gridInfoMap[group_id]["name"]
                group_list.append({'id': group_id, 'name': group_name})
            return group_list
        except Exception as e:
            print(f"Lỗi khi lấy danh sách nhóm: {e}")
            return []

    def display_group_menu(self):
        groups = self.fetchGroupInfo()
        if not groups:
            print("Không tìm thấy nhóm nào.")
            return None
        grouped = defaultdict(list)
        for group in groups:
            first_char = group['name'][0].upper()
            if first_char not in string.ascii_uppercase:
                first_char = '#'
            grouped[first_char].append(group)
        print("\nDanh sách các nhóm:")
        index_map = {}
        idx = 1
        for letter in sorted(grouped.keys()):
            print(f"\nNhóm {letter}:")
            for group in grouped[letter]:
                print(f"{idx}. {group['name']} (ID: {group['id']})")
                index_map[idx] = group['id']
                idx += 1
        return index_map

    def select_group(self):
        index_map = self.display_group_menu()
        if not index_map:
            return None
        while True:
            try:
                choice = int(input("Nhập số thứ tự của nhóm: ").strip())
                if choice in index_map:
                    return index_map[choice]
                print("Số không hợp lệ.")
            except ValueError:
                print("Vui lòng nhập số hợp lệ.")

    def send_reo_file_all(self, thread_id, filename, delay):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                message_lines = [line.strip() for line in f if line.strip()]
            if not message_lines:
                print("❌ File rỗng hoặc không có dòng hợp lệ.")
                return

            remaining_lines = []
            self.running = True

            def spam_loop():
                nonlocal remaining_lines
                while self.running:
                    if not remaining_lines:
                        remaining_lines = message_lines.copy()
                        random.shuffle(remaining_lines)
                    line = remaining_lines.pop()
                    final_text = f"{line} =)) @All"
                    mention = Mention("-1", offset=len(final_text) - 4, length=4)
                    msg = Message(text=final_text, mention=mention)
                    self.setTyping(thread_id, ThreadType.GROUP)
                    time.sleep(1.5)
                    self.send(msg, thread_id=thread_id, thread_type=ThreadType.GROUP)
                    print(f"✅ Đã gửi: {final_text}")
                    time.sleep(delay)

            thread = threading.Thread(target=spam_loop)
            thread.daemon = True
            thread.start()

            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop_sending()
        except FileNotFoundError:
            print(f"❌ Không tìm thấy file: {filename}")
        except Exception as e:
            print(f"❌ Lỗi khi gửi nội dung: {e}")

    def stop_sending(self):
        self.running = False
        print("⛔ Đã dừng gửi tin nhắn.")

def run_tool():
    print("TOOL RÉO TAG @All TỪ FILE KHÔNG LẶP LẠI")
    print("[1] Gửi nội dung từ file (réo @All)")
    print("[0] Thoát")
    choice = input("Nhập lựa chọn: ").strip()
    if choice != '1':
        print("Đã thoát tool.")
        return

    client = Bot(API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES)
    thread_id = client.select_group()
    if not thread_id:
        return

    filename = input("Nhập tên file chứa nội dung: ").strip()
    try:
        delay = float(input("Nhập delay giữa các tin nhắn (giây): ").strip())
    except ValueError:
        print("⏱️ Dùng mặc định 10s.")
        delay = 10

    client.send_reo_file_all(thread_id=thread_id, filename=filename, delay=delay)

if __name__ == "__main__":
    run_tool()
