@echo off
cd /d C:\Users\David\Projects\MarketSquare
echo ==== APPLY (backs up DB first, writes) ====> msfix_apply.log 2>&1
ssh root@178.104.73.239 "cd /var/www/marketsquare && python3 fix_super_advert_format.py --apply" >> msfix_apply.log 2>&1
echo.>> msfix_apply.log 2>&1
echo ==== RE-RUN DRY (should show already-done / nothing to strip) ====>> msfix_apply.log 2>&1
ssh root@178.104.73.239 "cd /var/www/marketsquare && python3 fix_super_advert_format.py" >> msfix_apply.log 2>&1
type msfix_apply.log
echo.
echo (apply complete - log written to msfix_apply.log)
pause
