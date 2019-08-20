from application import app

if __name__ == '__main__':
    # CROS for swagger
    @app.after_request
    def cros_for_swagger(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, api_key, Authorization')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response


    app.run(debug=True, host='0.0.0.0', port=8080)
