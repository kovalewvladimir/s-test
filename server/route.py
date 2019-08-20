def init_route(app):
    from auth import bp as bp_auth
    from joke import bp as bp_joke

    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_joke)
