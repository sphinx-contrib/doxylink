__version__ = '1.7'


def setup(app):
    from .doxylink import setup_doxylink_roles
    app.add_config_value('doxylink', {}, 'env')
    app.connect('builder-inited', setup_doxylink_roles)
