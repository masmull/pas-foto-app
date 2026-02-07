from flask import Flask, render_template, request
from PIL import Image, ImageDraw
from rembg import remove
import os
import io
import time

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

DPI = 300
MARGIN = 10

def cm_to_px(cm):
    return int(cm * (DPI / 2.54))

PAPER_SIZES = {
    "A4": (cm_to_px(21), cm_to_px(29.7)),
    "A5": (cm_to_px(14.8), cm_to_px(21))
}

PHOTO_SIZES = {
    "2x3": (cm_to_px(2), cm_to_px(3)),
    "3x4": (cm_to_px(3), cm_to_px(4)),
    "4x6": (cm_to_px(4), cm_to_px(6))
}

def get_color(color_name):
    colors = {
        "none": (255,255,255),
        "red": (255,0,0),
        "blue": (0,0,255)
    }
    return colors.get(color_name, (255,255,255))

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["photo"]
        size = request.form["size"]
        bgcolor = request.form["bgcolor"]
        papersize = request.form["papersize"]
        count = int(request.form["count"])

        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            # buka foto
            img = Image.open(filepath).convert("RGBA")

            # hapus background
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes = img_bytes.getvalue()
            img_no_bg = remove(img_bytes)
            img_no_bg = Image.open(io.BytesIO(img_no_bg)).convert("RGBA")

            # resize sesuai pas foto
            photo_w, photo_h = PHOTO_SIZES[size]
            img_no_bg = img_no_bg.resize((photo_w, photo_h))

            # buat background warna baru
            bg_color = get_color(bgcolor)
            bg_img = Image.new("RGBA", img_no_bg.size, bg_color)
            bg_img.paste(img_no_bg, (0,0), img_no_bg)
            final_photo = bg_img.convert("RGB")

            # buat kertas
            paper_w, paper_h = PAPER_SIZES[papersize]
            paper = Image.new("RGB", (paper_w, paper_h), (255,255,255))

            # border tepi kertas
            draw = ImageDraw.Draw(paper)
            border_thickness = 10
            draw.rectangle([0,0,paper_w-1,paper_h-1], outline=(0,0,0), width=border_thickness)

            # letakkan foto sesuai jumlah
            x_offset = MARGIN
            y_offset = MARGIN
            placed = 0

            for i in range(count):
                if x_offset + photo_w > paper_w - MARGIN:
                    x_offset = MARGIN
                    y_offset += photo_h + MARGIN
                if y_offset + photo_h > paper_h - MARGIN:
                    break
                paper.paste(final_photo, (x_offset, y_offset))
                x_offset += photo_w + MARGIN
                placed += 1

            # simpan hasil
            filename = f"sheet_{int(time.time())}.jpg"
            output_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            paper.save(output_path)

            # tampilkan hasil + tombol save
            return f"""
            <h2>Hasil Sheet ({papersize}) dengan {placed} foto</h2>
            <img src='/static/uploads/{filename}' style="max-width:800px; border:1px solid #ccc;"><br><br>
            <a href='/static/uploads/{filename}' download>
                <button>Save / Download</button>
            </a>
            <button onclick="window.location.href='/'">Kembali / Reset</button>
            """

    return render_template("upload.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

