command_start = '/stats'
only_for_admins = 'Sorry, this function is available only for admins. Set "admin" flag in django admin panel.'

ADMIN_MENU_BASE = f'⚠️ Выберите нужное действие\n{command_start} - bot stats'

users_amount_stat = "<b>Users</b>: {user_count}\n" \
                    "<b>24h active</b>: {active_24}"
