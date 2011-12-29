import os, errno, re
from time import gmtime, strftime

from flask import Flask, render_template, abort, send_from_directory,make_response,send_file
from jinja2 import TemplateNotFound


from lib.placeholder import Placeholder, PlaceholderOptionError

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

app = Flask(__name__)
app.run

@app.route('/', defaults={'page': 'index'})
@app.route('/<page>')
def flask_geekmeet(page=None):
    try:
        return render_template('%s.html' % page)
    except TemplateNotFound:
        abort(404)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.context_processor
def inject_year():
    return dict(c_year=strftime('%Y', gmtime()))

def rectangle(input, box, fill, outline, width):
    draw = ImageDraw.Draw(input)
    draw.rectangle(box, fill=outline) # The outer rectangle
    out = draw.rectangle( # The inner rectangle
        (box[0] + width, box[1] + width, box[2] - width, box[3] - width),
        fill=fill
    )
    return out



'''
placeholder
image handling
exmaples:
host:port/200x100/898989/333333/placeholder.png
host:port/200x100/placeholder.png
host:port/placeholder.png
'''

@app.route( "/placeholder.png" )
@app.route( "/<int:width>x<int:height>/placeholder.png" )
@app.route( "/<int:width>x<int:height>/<foreground>/<background>/placeholder.png" )
@app.route( "/<int:width>x<int:height>/<foreground>/<background>/<metadata>/placeholder.png" )
@app.route( "/<int:width>x<int:height>/<foreground>/<background>/<metadata>/<border>/placeholder.png" )
def placeholder( width=400, height=300, foreground="333333", background="CCCCCC", border=False, metadata=True ):
    border = False if not border or border == "noborder" else True
    metadata = False if not metadata or metadata == "nometadata" else True
    out = "./output/%dx%d/%s/%s/%s/%s.png" % ( width, height, foreground, background, 'border' if border else 'noborder', 'metadata' if metadata else 'nometadata' )

    if height > 1000 or width > 1000:
        abort( 501,  "Max size is 1000x1000.  Take pity on my poor server, please." )
    if re.search( r'[^0-9a-fA-F]', foreground ):
        abort( 501, "Please use a foreground hex value in the form `RRGGBB`: You entered `%s`" % foreground )
    if re.search( r'[^0-9a-fA-F]', background ):
        abort( 501, "Please use a background hex value in the form `RRGGBB`: You entered `%s`" % background )

    if not os.path.exists( out ):
        mkdir_p( os.path.dirname( out ) )
        p = Placeholder( width=width, height=height, foreground=foreground, background=background, border=border, out=out, metadata=metadata )
        p.write()
    try:
        return send_file( filename_or_fp=out, mimetype='image/png', cache_timeout=31556926 )
    except:
        abort(404)


'''
helpers
'''

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')
'''
#look .server/*.conf
@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(app.root_path, 'static'),'robots.txt')

@app.route('/crossdomain.xml')
def crossdomain():
    return send_from_directory(os.path.join(app.root_path, 'static'),'crossdomain.xml', mimetype='text/xml')
'''

if __name__ == '__main__':
    app.debug = True
    if (app.debug):
        app.run(host='localhost', port=8181)