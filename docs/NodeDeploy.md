## Install PM2

Follow [PM2 docs](https://pm2.keymetrics.io/docs/usage/quick-start/) to install PM2. 

Start by:

```
pm2 start app.js --watch --name covid-database
```

Manage process by 

```
pm2 restart covid-database
pm2 reload covid-database
pm2 stop covid-database
pm2 delete covid-database

pm2 [list|ls|status]

pm2 logs

pm2 monit
```


I haven't figured out how to auto start pm2 app.