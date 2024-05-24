from website import create_app


app = create_app()
#entry point for our app
#debug false in production
#to only run the site if this is called
if __name__ == '__main__':
    app.run(debug=True, port=4000) 
