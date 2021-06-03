from crate.theme.rtd.conf.cloud_cli import *  # noqa

extensions += ["sphinx_sitemap", "sphinxarg.ext"]  # noqa:F405

html_static_path = ["_static"]
html_context = {"extra_css_files": ["_static/sphinxarg.css"]}
