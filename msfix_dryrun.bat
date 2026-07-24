@echo off
cd /d C:\Users\David\Projects\MarketSquare
echo ==== SCP migration script to server ====> msfix.log 2>&1
scp scripts\fix_super_advert_format.py root@178.104.73.239:/var/www/marketsquare/ >> msfix.log 2>&1
echo.>> msfix.log 2>&1
echo ==== DRY RUN (no writes) ====>> msfix.log 2>&1
ssh root@178.104.73.239 "cd /var/www/marketsquare && python3 fix_super_advert_format.py" >> msfix.log 2>&1
echo.>> msfix.log 2>&1
echo ==== END DRY RUN ====>> msfix.log 2>&1
type msfix.log
echo.
echo (dry-run complete - log written to msfix.log)
pause
