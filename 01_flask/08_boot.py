from flask import Flask, render_template, request
import os
app = Flask(__name__)

@app.route("/")
def child():
    img_file = os.path.join(app.root_path, 'static/img/dog.jpg') # 이미지파일 선택
    mtime = int(os.stat(img_file).st_mtime)
    return render_template('08.Carousel.html', mtime=mtime)

@app.route("/table")
def child2():
    return render_template('08.Table.html')

if __name__ == '__main__':
    app.run(debug=True)