from crate.theme.rtd.conf.cloud_cli import *

exclude_patterns = ["out/**"]

# crate.theme sets html_favicon to favicon.png which causes a warning because
# it should be a .ico and in addition there is no favicon.png in this project
# so it can't find the file
html_favicon = None

site_url = 'https://crate.io/docs/croud/en/latest/'
extensions = ['sphinx_sitemap']

# The file extension
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'
