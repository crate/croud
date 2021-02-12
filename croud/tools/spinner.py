import sys

from halo import Halo

# It's sadly not possible to set arbitrary colours, but cyan (the default)
# is close(ish) to Crate Blue (#00a6d1).
HALO = Halo(text="Working ...", spinner="dots", stream=sys.stderr)
