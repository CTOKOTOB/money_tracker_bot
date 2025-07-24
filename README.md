start - начать работу
add_category - добавить категорию
add_expense - добавить трату
delete_last - удалить последнюю трату



alias psql='sudo -u moneybot psql -d money_tracker'
alias postgreslog="sudo tail -100f /var/log/postgresql/postgresql-17-main.log"
alias activate='cd /home/moneybot/money_tracker_bot && source venv/bin/activate'

alias stopbot='sudo systemctl stop moneybot.service'
alias startbot='sudo systemctl start moneybot.service'
alias statusbot='sudo systemctl status moneybot.service'
alias logbot="sudo journalctl -u moneybot.service -f"
