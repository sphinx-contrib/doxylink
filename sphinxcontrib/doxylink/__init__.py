__version__ = "1.13.0"

def setup(app):
    from .doxylink import setup_doxylink_roles
    app.add_config_value('doxylink', {}, 'env')
    app.add_config_value('doxylink_pdf_files', {}, 'env')
    app.add_config_value('doxylink_parse_error_ignore_regexes',
                         default=[], types=[str], rebuild='env')
    app.connect('builder-inited', setup_doxylink_roles)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
