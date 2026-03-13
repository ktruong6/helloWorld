from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/hello')
def hello():  # put application's code here
    return render_template('hello.html')

@app.route('/about')
def about():  # put application's code here
    return render_template('about.html')

@app.route('/about_css')
def about_css():  # put application's code here
    return render_template('about-css.html')

@app.route('/favorite_course')
def favorite_course():  # put application's code here
    subject=request.args.get('subject')
    course_number=request.args.get('course_number')

    return render_template('favorite-course.html',subject=subject,course_number=course_number)

@app.route('/contact', methods=['GET', 'POST'])
def contact(): # put application's code here
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not first_name or not last_name or not email or not message:
            return render_template("contact.html", submitted=False)

        return render_template(
            "contact.html",
            submitted=True,
            first_name=first_name,
            last_name=last_name,
            email=email,
            message=message
        )

    return render_template("contact.html", submitted=False)

if __name__ == '__main__':
    app.run()
