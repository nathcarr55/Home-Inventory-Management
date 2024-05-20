from BinGenie import create_app

app = create_app('production_config.py')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
