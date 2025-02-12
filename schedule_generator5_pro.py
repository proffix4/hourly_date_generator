#!/usr/bin/env python3

from datetime import datetime, timedelta
import os
import tkinter as tk
from tkinter import messagebox

class ScheduleEntry:
    def __init__(self, date, weekday, activity_type, group, type_of_class, hours):
        self.date = date
        self.weekday = weekday
        self.activity_type = activity_type
        self.group = group
        self.type_of_class = type_of_class
        self.hours = hours

    def __str__(self, detailed=False):
        hours_str = int(self.hours) if self.hours.is_integer() else self.hours
        if detailed:
            return f"{self.date}, {self.weekday}, {self.activity_type}, {self.group}, {self.type_of_class}, {hours_str} ч."
        else:
            return f"{self.date}, {self.type_of_class}, {self.group}, {hours_str} ч."

def parse_date_range(date_range):
    start_str, end_str = date_range.split('-')
    start_date = datetime.strptime(start_str.strip(), "%d.%m.%Y")
    end_date = datetime.strptime(end_str.strip(), "%d.%m.%Y")
    return start_date, end_date

def get_weekday_index(weekday_name):
    weekdays = {
        "Понедельник": 0,
        "Вторник": 1,
        "Среда": 2,
        "Четверг": 3,
        "Пятница": 4,
        "Суббота": 5,
        "Воскресенье": 6
    }
    return weekdays.get(weekday_name, None)

def generate_schedule(date_range, schedule_entries):
    start_date, end_date = parse_date_range(date_range)
    delta = timedelta(days=1)
    current_date = start_date
    schedule = []

    while current_date <= end_date:
        for entry in schedule_entries:
            weekday_index = get_weekday_index(entry[0])
            if current_date.weekday() == weekday_index:
                existing_entry = next((e for e in schedule if e.date == current_date.strftime("%d.%m.%Y") 
                                       and e.activity_type == entry[1] and e.group == entry[2] and e.type_of_class == entry[3]), None)
                if existing_entry:
                    existing_entry.hours += float(entry[4])
                else:
                    schedule.append(ScheduleEntry(
                        current_date.strftime("%d.%m.%Y"), 
                        entry[0], entry[1], entry[2], entry[3], float(entry[4])
                    ))
        current_date += delta
    return schedule

def ask_output_format():
    root = tk.Tk()
    root.withdraw()
    detailed = messagebox.askyesno("Формат вывода", "Вы хотите подробный вывод?")
    root.destroy()
    return detailed

def main():
    with open('schedule_data.txt', 'r', encoding='utf-8-sig') as file:
        lines = file.readlines()

    schedule_entries = []
    for line in lines:
        date_range, entry = line.strip().split('|')
        entry = entry.split(', ')
        schedule_entries.append((date_range, entry))

    schedule = []
    for date_range, entries in schedule_entries:
        schedule.extend(generate_schedule(date_range, [entries]))

    schedule.sort(key=lambda x: datetime.strptime(x.date, "%d.%m.%Y"))

    combined_schedule = []
    for entry in schedule:
        if combined_schedule and combined_schedule[-1].date == entry.date and combined_schedule[-1].activity_type == entry.activity_type and combined_schedule[-1].group == entry.group and combined_schedule[-1].type_of_class == entry.type_of_class:
            combined_schedule[-1].hours += entry.hours
        else:
            combined_schedule.append(entry)

    if not combined_schedule:
        print("Ошибка: расписание пустое. Проверьте входные данные.")
        return

    total_hours = sum(entry.hours for entry in combined_schedule)
    hours_per_discipline = {}
    for entry in combined_schedule:
        key = (entry.activity_type, entry.group, entry.type_of_class)
        hours_per_discipline[key] = hours_per_discipline.get(key, 0) + entry.hours

    earliest_date = datetime.strptime(combined_schedule[0].date, "%d.%m.%Y")
    latest_date = datetime.strptime(combined_schedule[-1].date, "%d.%m.%Y")
    suffix = "detailed" if ask_output_format() else "summary"
    file_name = f"{earliest_date.strftime('%d.%m.%Y')}-{latest_date.strftime('%d.%m.%Y')}_hourly_date_{suffix}.txt"
    detailed_output = suffix == "detailed"

    with open(file_name, 'w', encoding='utf-8') as f:
        for entry in combined_schedule:
            f.write(entry.__str__(detailed=detailed_output) + '\n')
        f.write(f"Всего часов: {total_hours}\n")
        f.write("\nЧасы по каждой дисциплине, группе и форме занятия:\n")
        for key, hours in hours_per_discipline.items():
            hours_str = int(hours) if hours.is_integer() else hours
            f.write(f"{key[0]}, {key[1]}, {key[2]}: {hours_str} ч.\n")

    if os.name == 'nt':
        os.startfile(file_name)
    else:
        os.system(f"xdg-open {file_name}")

if __name__ == "__main__":
    main()
