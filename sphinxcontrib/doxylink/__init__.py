__version__ = '1.11'


def setup(app):
    from .doxylink import setup_doxylink_roles
    app.add_config_value('doxylink', {}, 'env')
    app.add_config_value('doxylink_pdf_files', {}, 'env')
    app.connect('builder-inited', setup_doxylink_roles)
