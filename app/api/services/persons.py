from datetime import datetime


async def find_max_min(person_list: list):

    if len(person_list) < 2:
        person = person_list[0]
        person.time_end = "-"
        person.snapPicUrl2 = "-"

        return person

    min_time = datetime.strptime(person_list[0].time, "%H:%M:%S")
    max_time = datetime.strptime(person_list[0].time, "%H:%M:%S")

    min_time_index = 0
    max_time_index = 0

    i = 0

    for person in person_list:

        current_time = datetime.strptime(person.time, "%H:%M:%S")

        if current_time < min_time:
            min_time = current_time
            min_time_index = i

        if current_time > max_time:
            max_time = current_time
            max_time_index = i

        i += 1

    person = person_list[min_time_index]
    person.time_end = person_list[max_time_index].time
    person.snapPicUrl2 = person_list[max_time_index].snapPicUrl

    return person
