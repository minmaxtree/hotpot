from hotpot import Hotpot, Blueprint, render_template, abort
from jinja2 import TemplateNotFound

simple_page = Blueprint('simple_page', __name__, template_folder='template_tests')

# @simple_page.route('/', defaults={'page': 'index'})
@simple_page.route('/<page>')
def show(page):
    try:
        return render_template('pages/%s.html' % page)
    except TemplateNotFound:
        abort(404)

app = Hotpot(__name__)
app.register_blueprint(simple_page)
app.register_blueprint(simple_page, url_prefix='/pages')

if __name__ == '__main__':
    app.run()
