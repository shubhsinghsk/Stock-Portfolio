import os
import secrets
from flask import render_template,request,redirect,session,url_for,flash,redirect,abort
from stock.forms import RegistrationForm,LoginForm,UpdateAccountForm,GetCurrentPriceForm,WatchStockForm
from PIL import Image
from stock.models import User,Stock, Watch
from stock import app,db,bcrypt
from flask_login import login_user, current_user, logout_user, login_required
import datetime
from pandas_datareader import data

## Routes *****************************************************8


@app.route('/')
def index():
    return render_template('home.html')

    
@app.route('/home')
def home():
    return render_template('home.html',title='Home')


@app.route('/about')
def about():
    return render_template('about.html',title='About')


@app.route('/stock_analysis')
def stock_analysis():
    return render_template('stock_analysis.html',title='Stock Analysis')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,name=form.name.data, email=form.email.data, password=hashed_password,)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('my_investment'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.mobileno = form.mobileno.data
        hashed_adhar = bcrypt.generate_password_hash(form.adharno.data).decode('utf-8')
        current_user.adharno = hashed_adhar
        hashed_pan = bcrypt.generate_password_hash(form.panno.data).decode('utf-8')
        current_user.panno = hashed_pan
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        print(type(current_user.username))
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.mobileno.data = current_user.mobileno
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)



@app.route('/my_investment')
@login_required
def my_investment():
    stocks = Stock.query.filter_by(author=current_user)
    return render_template('dashboard.html',title='my_investment',stocks=stocks)


@app.route('/add_stock/<string:symbol>', methods=['GET', 'POST'])
@login_required
def add_stock(symbol):
    stock = Stock.query.filter_by(stock_symbol=symbol).first()
    stock_name = stock.stock_symbol
    no_of_stocks = stock.number_of_shares
    purchase_price = stock.purchase_price
    return render_template('add_stock.html', title='Add Stock',symbol=stock_name,no_of_stocks=no_of_stocks,
                        purchase_price=purchase_price,stock=stock)


@app.route('/get_price', methods=['GET', 'POST'])
@login_required
def get_price():
    form = GetCurrentPriceForm()
    if form.validate_on_submit():
        quote =form.stock_symbol.data
        stockData = data.get_quote_yahoo(quote)
        x = stockData['price']
        stock = Stock(stock_symbol=form.stock_symbol.data,
                  number_of_shares=form.number_of_shares.data, 
                  purchase_price=x[0], author=current_user)
        db.session.add(stock)
        db.session.commit()
        return redirect(url_for('add_stock',symbol=form.stock_symbol.data))
    return render_template('get_stock.html',title='Get price',form=form)




@app.route("/my_investment/<int:stock_id>")
def stockes(stock_id):
    stock = Stock.query.get_or_404(stock_id)
    quote = stock.stock_symbol
    stockData = data.get_quote_yahoo(quote)
    x = stockData['price']
    if stock.stock_symbol== 'GOOGL':
        stock_name = 'GOOGLE'
    else:    
        stock_name = stockData['shortName'][0]

    stock_position = (stock.number_of_shares)*x[0]

    # end_date = datetime.datetime.today().strftime('%Y-%m-%d')
    end_date = stock.prchase_date
    start_date =  '2021-10-15'
    historicalPrices = data.DataReader(quote, start=start_date, end=end_date, data_source='yahoo')
    z = historicalPrices['Low']
    labels = z.index
    values = []
    for y in z:
        values.append(y)
    return render_template('stock.html', title=stock.stock_symbol, stock=stock, 
                             stock_name=stock_name,current_price=x[0],
                             labels=labels,values=values,stock_position=stock_position)


@app.route("/my_investment/<int:stock_id>/delete", methods=['POST','GET'])
@login_required
def sell_stock(stock_id):
    stock = Stock.query.get_or_404(stock_id)
    if stock.author != current_user:
        abort(403)
    db.session.delete(stock)
    db.session.commit()
    flash('You have successfully sell the stock', 'success')
    return redirect(url_for('my_investment'))

@app.route("/add_watch_stock",methods=['POST','GET'])
@login_required
def add_stock_watch():
    form = WatchStockForm()
    if form.validate_on_submit():
        quote = form.stock_symbol.data
        stockData = data.get_quote_yahoo(quote)
        current_price = stockData['price'][0]
        day_high = stockData['regularMarketDayHigh'][0]
        day_low = stockData['regularMarketDayLow'][0]
        previous_close = stockData['regularMarketPreviousClose'][0]
        company_name = stockData['shortName'][0]
        stock = Watch(stock_symbol=form.stock_symbol.data,current_price=current_price,day_high=day_high,
                     day_low=day_low,previous_close=previous_close,company_name=company_name,
                     author=current_user)    
        db.session.add(stock)
        db.session.commit()
        flash('You have added the stock for watchlist', 'success')
        return redirect(url_for('watch_stock'))
    return render_template('add_stock_watch.html', title='Add Watch Stock', form=form)


@app.route("/watchlist")
@login_required
def watch_stock():
    watch = Watch.query.order_by(Watch.id).filter_by(user_id=current_user.id).all()
    for watchstock in watch:
        quote = watchstock.stock_symbol
        stockData = data.get_quote_yahoo(quote)
        current_user.current_price = stockData['price'][0]
        print(current_user.current_price)
        current_user.day_high = stockData['regularMarketDayHigh'][0]
        current_user.day_low = stockData['regularMarketDayLow'][0]
        current_user.previous_close = stockData['regularMarketPreviousClose'][0]
        current_user.company_name = stockData['shortName'][0]
        db.session.commit()
    watchs = Watch.query.order_by(Watch.id).filter_by(user_id=current_user.id).all()

    return render_template('watchlist.html',title='Watchlist',stocks=watchs)


@app.route("/watchlist/<int:stock_id>/delete", methods=['POST'])
@login_required
def delete_watch_stock(stock_id):
    stock = Watch.query.get_or_404(stock_id)
    if stock.author != current_user:
        abort(403)
    db.session.delete(stock)
    db.session.commit()
    flash('You have successfully delete the stock from watchlist', 'success')
    return redirect(url_for('watch_stock'))


@app.route("/watched_stock/<int:stock_id>")
def watchlist_stock(stock_id):
    stock = Watch.query.get_or_404(stock_id)
    quote = stock.stock_symbol
    stockData = data.get_quote_yahoo(quote)
    x = stockData['price']
    if stock.stock_symbol== 'GOOGL':
        stock_name = 'GOOGLE'
    else:    
        stock_name = stockData['shortName'][0]

    end_date = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(days=30)
    historicalPrices = data.DataReader(quote, start=start_date, end=end_date, data_source='yahoo')
    z = historicalPrices['Low']
    labels = z.index
    values = []
    for y in z:
        values.append(y)
    return render_template('watched_stock.html', title=stock.stock_symbol, stock=stock, 
                             stock_name=stock_name,current_price=x[0],
                             labels=labels,values=values)
