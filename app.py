from flask import Flask, render_template, url_for
import psycopg2
import requests
app = Flask(__name__)


@app.route('/', methods = ['GET','POST'])
def index():
    categories = {}
    conn = psycopg2.connect(user = '', database = 'tiki', password = '')
    cur = conn.cursor()
    query ='''
    SELECT 
        name 
    FROM categories
    WHERE parent_id is null;
    '''
    cur.execute(query)
    names = cur.fetchall()
    img_links = [
        'https://image.flaticon.com/icons/svg/1079/1079539.svg',
        'https://image.flaticon.com/icons/svg/1008/1008286.svg',
        'https://image.flaticon.com/icons/svg/1298/1298457.svg',
        'https://image.flaticon.com/icons/svg/1299/1299833.svg',
        'https://image.flaticon.com/icons/svg/1299/1299837.svg',
        'https://image.flaticon.com/icons/svg/1135/1135249.svg',
        'https://image.flaticon.com/icons/svg/1178/1178598.svg',
        'https://www.flaticon.com/premium-icon/icons/svg/1756/1756551.svg',
        'https://image.flaticon.com/icons/svg/1073/1073349.svg',
        'https://image.flaticon.com/icons/svg/1008/1008274.svg',
        'https://image.flaticon.com/icons/svg/1008/1008279.svg',
        'https://www.flaticon.com/premium-icon/icons/svg/1058/1058746.svg',
        'https://image.flaticon.com/icons/svg/1288/1288128.svg',
        'https://www.flaticon.com/premium-icon/icons/svg/1072/1072337.svg',
        'https://image.flaticon.com/icons/svg/1080/1080330.svg',
        'https://image.flaticon.com/icons/svg/1073/1073176.svg'
    ]
    cat_names = ['Điện Thoại - Máy Tính Bảng',
            'Điện Tử - Điện Lạnh',
            'Thiết Bị Số - Phụ Kiện Số',
            'Laptop - Máy Vi Tính - Linh kiện',
            'Máy Ảnh - Máy Quay Phim',
            'Điện Gia Dụng',
            'Nhà Cửa - Đời Sống',
            'Bách Hóa Online',
            'Đồ Chơi - Mẹ & Bé',
            'Làm Đẹp - Sức Khỏe',
            'Thời Trang',
            'Thể Thao - Dã Ngoại',
            'Ô Tô - Xe Máy - Xe Đạp',
            'Hàng Quốc Tế',
            'Nhà Sách Tiki',
            'Voucher - Dịch vụ']
    for i in range(len(names)):
        categories[names[i]] = (img_links[i],cat_names[i])
    return render_template('index.html', categories= categories)

@app.route('/products/<category>/<offset>')
def products(category,offset):
    conn = psycopg2.connect(user = 'philong', database = 'tiki', password = 'phan1996')
    cur = conn.cursor()
    query = "SELECT * FROM products WHERE category = %s LIMIT 48 OFFSET %s"
    val = (category,offset,)
    cur.execute(query, val)
    products = cur.fetchall()

    return render_template('products.html',products = products, category=category, offset=offset)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

