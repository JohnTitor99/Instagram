from django.utils import timezone


# making a dict of created date in required format
def created_dict(items):
    item_created_dict = {}

    for item in items:
        item_created = item.created
        now = timezone.now()
        period = now - item_created
        n_str = "{}".format(period.total_seconds()) # n - a total amount of seconds
        n_float = float(n_str)
        n = int(n_float)

        month_int = n // 2592000
        day_int = n // 86400
        full_min = n // 60
        hour_int = full_min // 60
        min_int = full_min % 60
        sec_int = n % 60

        if month_int > 0:
            month = str(month_int) + " month" if month_int == 1 else str(month_int) + " months"
            item_created_dict[item.id] = month
        else:
            if day_int > 0:
                day = str(day_int) + " day" if day_int == 1 else str(day_int) + " days"
                item_created_dict[item.id] = day
            else:
                if hour_int > 0:
                    hour = str(hour_int) + " hour" if hour_int == 1 else str(hour_int) + " hours"
                    item_created_dict[item.id] = hour
                else:
                    if min_int > 0:
                        min = str(min_int) + " minute" if min_int == 1 else str(min_int) + " minutes"
                        item_created_dict[item.id] = min
                    else:
                        if sec_int > 0:
                            sec = str(sec_int) + " second" if sec_int == 1 else str(sec_int) + " seconds"
                            item_created_dict[item.id] = sec
                        else:
                            item_created_dict[item.id] = 'Now'


    return item_created_dict