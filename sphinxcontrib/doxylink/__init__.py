__version__ = "1.12.2"


def setup(app):
    from .doxylink import setup_doxylink_roles
    app.add_config_value('doxylink', {}, 'env')
    app.add_config_value('doxylink_pdf_files', {}, 'env')
    app.connect('builder-inited', setup_doxylink_roles)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
