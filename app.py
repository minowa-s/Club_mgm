from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/page_a')
def page_a():
    return render_template('page_a.html')

@app.route('/page_b')
def page_b():
    return render_template('page_b.html')
        
@app.route('/page_c')
def page_c():
    return render_template('page_c.html')

if __name__ == '__main__':
    app.run(debug=True)
