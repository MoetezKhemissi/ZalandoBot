from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

def load_csv_data(csv_file, min_price=None, max_price=None, out_of_stock=None, search=None):
    df = pd.read_csv(csv_file)

    if min_price is not None:
        df = df[df['final_price'] >= min_price]

    if max_price is not None:
        df = df[df['final_price'] <= max_price]

    if out_of_stock is not None:
        df = df[df['out_of_stock'] == out_of_stock]
    if search is not None:
        # Apply search filter if specified
        df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False, na=False).any(), axis=1)]

    return df.to_dict(orient='records')

@app.route('/')
def show_csv():
    min_price = request.args.get('min_price', default=None, type=float)
    max_price = request.args.get('max_price', default=None, type=float)
    out_of_stock = request.args.get('out_of_stock', default=None, type=lambda x: x.lower() == 'true')
    search = request.args.get('search', default=None, type=str)

    csv_file = 'merged_campaigns.csv'  # Path to your merged CSV
    data = load_csv_data(csv_file, min_price=min_price, max_price=max_price, out_of_stock=out_of_stock, search=search)
    return render_template('./index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
