add_expense - добавить трату
add_income - добавить доход
report - отчет
report_detail - отчет по категории за конкретный месяц
add_category - добавить категорию
delete_last - удалить последнюю трату
delete_last_income - удалить последнюю запись о доходе
start - начать работу




alias psql='sudo -u moneybot psql -d money_tracker'
alias postgreslog="sudo tail -100f /var/log/postgresql/postgresql-17-main.log"
alias activate='cd /home/moneybot/money_tracker_bot && source venv/bin/activate'

alias stopbot='sudo systemctl stop moneybot.service'
alias startbot='sudo systemctl start moneybot.service'
alias statusbot='sudo systemctl status moneybot.service'
alias logbot="sudo journalctl -u moneybot.service -f"
