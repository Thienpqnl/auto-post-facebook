import requests
import os
import random
from dotenv import load_dotenv
# Load biến môi trường từ file .env
load_dotenv()
# ===== CONFIG =====

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")
PIXABAY_KEY = os.getenv("PIXABAY_KEY")
# Chủ đề bài viết
TOPIC = "nuoi day con"  # viet khong dau neu can
if GEMINI_API_KEY:
    print(f"✅ GEMINI_API_KEY loaded: {GEMINI_API_KEY[:5]}...{GEMINI_API_KEY[-5:]}")
else:
    print("❌ GEMINI_API_KEY not found in .env")
# Gemini API URL
apiUrl = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# ===== AI Sinh bài viết =====
def generate_post(topic):
    prompt = f"""
    Hay viet 1 bai post Facebook dai khoang 120 tu ve chu de {topic}.
    Giong van am ap, tich cuc, co 3 hashtag lien quan.
    Them 2 emoji phu hop o dau va cuoi bai, không được trùng lặp với những lần hỏi trước của tôi, nếu đây không phải lần đầu.
    """

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    r = requests.post(
        f"{apiUrl}?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json=body
    )

    if r.status_code == 200:
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    else:
        print("Error from Gemini API:", r.text)
        return None

# ===== Lấy ảnh minh họa từ Pixabay =====
def get_image():
    url = f"https://pixabay.com/api/?key={PIXABAY_KEY}&q=beautiful&image_type=photo"
    r = requests.get(url)
    
    if r.status_code != 200:
        raise Exception(f"Loi API Pixabay: {r.status_code}, noi dung: {r.text}")
    
    try:
        data = r.json()
    except Exception as e:
        raise Exception(f"Loi parse JSON: {e}, noi dung: {r.text}")
    
    if "hits" not in data or len(data["hits"]) == 0:
        raise Exception("Khong tim thay anh phu hop tu Pixabay")
    
    return data["hits"][0]["webformatURL"]

# ===== Đăng bài lên Facebook =====
def post_to_facebook(message, image_url=None):
    if image_url:
        endpoint = f"https://graph.facebook.com/{PAGE_ID}/photos"
        data = {
            "url": image_url,
            "caption": message,
            "access_token": ACCESS_TOKEN
        }
    else:
        endpoint = f"https://graph.facebook.com/{PAGE_ID}/feed"
        data = {
            "message": message,
            "access_token": ACCESS_TOKEN
        }
    r = requests.post(endpoint, data=data)
    return r.json()

# ===== Main =====
if __name__ == "__main__":
    post_text = generate_post(TOPIC)
    if post_text:
        image_url = get_image()
        result = post_to_facebook(post_text, image_url)
        print(result)