"""AUTO-RENEW-1 rig: the REAL backend (bea_main, security gate on) with a throwaway database and payments.py
pointed at the local Paystack stand-in. rig_front.py plays nginx in front of it. Rig-only; nothing here ships."""
import os, sys
RIG = '/home/claude/rig'
sys.path.insert(0, RIG); os.chdir(RIG)
_mk = os.makedirs
os.makedirs = lambda p, *a, **k: None if str(p).startswith('/var/www') else _mk(p, *a, **k)
import starlette.staticfiles as _sf
_i = _sf.StaticFiles.__init__
def _i2(self, *a, **k):
    k['check_dir'] = False; return _i(self, *a, **k)
_sf.StaticFiles.__init__ = _i2
import database
database.DB_PATH = os.environ.get('RIG_DB', '/home/claude/rigdata/marketsquare.db')
os.environ['MS_DB'] = os.path.join(os.path.dirname(database.DB_PATH), 'flights.db')
import payments
payments._BASE_URL = os.environ.get('RIG_PAYSTACK', 'http://127.0.0.1:8999')
import bea_main
app = bea_main.app
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='warning')
