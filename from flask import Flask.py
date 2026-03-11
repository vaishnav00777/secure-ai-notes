from flask import Flask, request, render_template_string
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

key = Fernet.generate_key()
cipher = Fernet(key)

notes = []

def simple_summary(text):
    return text.split(".")[0]

html = """
<h2>Secure AI Notes</h2>

<h3>Add Note</h3>
<form method="POST" enctype="multipart/form-data">
<textarea name="note" rows="4" cols="40" placeholder="Write your note"></textarea><br><br>
<input type="file" name="image"><br><br>
<button type="submit">Save Secure Note</button>
</form>

<h3>Saved Notes</h3>
<ul>
{% for n in notes %}
<li>
<b>Note:</b> {{n["note"]}} <br>
<b>Summary:</b> {{n["summary"]}} <br>
{% if n["image"] %}
<img src="/uploads/{{n['image']}}" width="200">
{% endif %}
</li>
<br>
{% endfor %}
</ul>
"""

@app.route("/", methods=["GET","POST"])
def home():
    if request.method == "POST":
        note = request.form["note"]

        image = request.files["image"]
        filename = ""   

        if image and image.filename != "":
            filename = image.filename
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        encrypted_note = cipher.encrypt(note.encode())
        decrypted_note = cipher.decrypt(encrypted_note).decode()

        summary = simple_summary(decrypted_note)

        notes.append({
            "note": decrypted_note,
            "summary": summary,
            "image": filename
        })

    return render_template_string(html, notes=notes)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return app.send_static_file("uploads/" + filename)

if __name__ == "__main__":
    app.run(debug=True)