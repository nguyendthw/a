from flask import Flask, render_template, request, redirect, jsonify
from flask_cors import CORS
from datetime import datetime
from mail1 import send_email
from database import a   # hàm tạo kết nối MySQL Aiven

app = Flask(__name__)
CORS(app)

# ============================
# TẠO TABLE TRONG AIVEN MYSQL
# ============================
try:
    conn = a()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            remind_at DATETIME NOT NULL,
            is_sent BOOLEAN DEFAULT FALSE
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("✔ Đã kiểm tra / tạo bảng schedules!")
except Exception as e:
    print("Lỗi khi tạo bảng:", e)



# ============================
#           ROUTES
# ============================

@app.route("/")
def index():
    return redirect("/list")


# ----------------------------
#   HIỂN THỊ DANH SÁCH LỊCH
# ----------------------------
@app.route("/list")
def list_schedule():
    conn = a()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM schedules ORDER BY remind_at ASC")
    schedules = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("list_schedule.html", schedules=schedules)



# ----------------------------
#       THÊM LỊCH MỚI
# ----------------------------
@app.route("/add", methods=["GET", "POST"])
def add_schedule():
    if request.method == "POST":
        email = request.form.get("email")
        title = request.form.get("title")
        description = request.form.get("description")
        remind_str = request.form.get("remind_at")

        remind_at = datetime.strptime(remind_str, "%Y-%m-%dT%H:%M")

        conn = a()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO schedules (email, title, description, remind_at)
            VALUES (%s, %s, %s, %s)
        """, (email, title, description, remind_at))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/list")

    return render_template("add_schedule.html")



# ----------------------------
#  API LẤY DỮ LIỆU (JSON)
# ----------------------------
@app.route("/api/schedules")
def api_schedules():
    conn = a()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM schedules ORDER BY remind_at ASC")
    schedules = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(schedules)



# ----------------------------
#  TEST GỬI EMAIL THỦ CÔNG
# ----------------------------
@app.route("/send-test", methods=["POST"])
def send_test():
    email = request.form.get("email")
    send_email(email, "Đây là email test từ hệ thống!")
    return "Email đã gửi!"


# ----------------------------
#       START Flask
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
