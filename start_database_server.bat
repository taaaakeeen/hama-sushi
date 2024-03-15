pg_ctl -D C:\PostgreSQL\server_01 -l C:\PostgreSQL\server_01\server_01.log start
pg_ctl -D C:\PostgreSQL\server_02 -l C:\PostgreSQL\server_02\server_02.log start
pg_ctl -D C:\PostgreSQL\server_03 -l C:\PostgreSQL\server_03\server_03.log start
pg_ctl -D C:\PostgreSQL\server_04 -l C:\PostgreSQL\server_04\server_04.log start

netstat -ano -o | find "5433"
netstat -ano -o | find "5434"
netstat -ano -o | find "5435"
netstat -ano -o | find "5436"

pause