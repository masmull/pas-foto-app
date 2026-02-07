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


# =========================
# HELPER
# =========================

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
        "red": (255, 0, 0),
        "blue": (0, 0, 255)
    }
    return colors.get(color_name, (255, 255, 255))


# =========================
# ROUTES
# =========================

@app.route("/", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        file = request.files["photo"]
        size = request.form["size"]
        bgcolor = request.form["bgcolor"]
        papersize = request.form["papersize"]
        count = int(request.form["count"])

        if not file:
            return render_template("upload.html")

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        img = Image.open(filepath).convert("RGBA")

        # =========================
        # Background handling
        # =========================

        if bgcolor == "none":
            # TANPA remove background
            photo = img
        else:
            # Remove background pakai AI
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')

            removed = remove(img_bytes.getvalue())
            removed_img = Image.open(io.BytesIO(removed)).convert("RGBA")

            bg_color = get_color(bgcolor)

            bg = Image.new("RGBA", removed_img.size, bg_color)
            bg.paste(removed_img, (0, 0), removed_img)

            photo = bg

        # resize pas foto
        photo_w, photo_h = PHOTO_SIZES[size]
        photo = photo.resize((photo_w, photo_h)).convert("RGB")

        # =========================
        # Buat kertas
        # =========================

        paper_w, paper_h = PAPER_SIZES[papersize]
        paper = Image.new("RGB", (paper_w, paper_h), (255, 255, 255))

        draw = ImageDraw.Draw(paper)

        # border tepi
        draw.rectangle(
            [0, 0, paper_w - 1, paper_h - 1],
            outline=(0, 0, 0),
            width=8
        )

        # grid foto
        x = MARGIN
        y = MARGIN
        placed = 0

        for i in range(count):

            if x + photo_w > paper_w - MARGIN:
                x = MARGIN
                y += photo_h + MARGIN

            if y + photo_h > paper_h - MARGIN:
                break

            paper.paste(photo, (x, y))
            x += photo_w + MARGIN
            placed += 1

        # =========================
        # Save hasil
        # =========================

        filename = f"sheet_{int(time.time())}.jpg"
        output_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        paper.save(output_path, quality=95)

        # =========================
        # Render result page (CANTIK)
        # =========================

        return render_template(
            "result.html",
            image_url=f"/static/uploads/{filename}",
            papersize=papersize,
            placed=placed
        )

    return render_template("upload.html")


# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
