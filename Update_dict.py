import pandas as pd
import os

# Get the current working directory
current_directory = os.getcwd()

# Specify your file name
file_name = "class_timetable.xlsx"

# Construct the full file path
file_path = os.path.join(current_directory, file_name)

print(f"File path: {file_path}")



def update_timetables(input_data,file_path, timetable_dict):
    lst = []
    # Read the Excel file
    xls = pd.ExcelFile(file_path)
    
    

    # Iterate through each sheet in the Excel file
    for sheet_name in xls.sheet_names:
        # Extract class and section from the sheet name
        class_section = sheet_name
        cls = int(class_section[:-1])  
        section = class_section[-1] 
        
        # Read the sheet into a DataFrame
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # Initialize a nested dictionary for this class and section if it doesn't exist
        if cls not in timetable_dict:
            timetable_dict[cls] = {}
        if section not in timetable_dict[cls]:
            timetable_dict[cls][section] = {}

        for index, row in df.iterrows():
            period = row['Period-Day'].strip()
            if 'Period_' not in period:
                continue  # Skip rows without a valid 'Period_' prefix
            
            # Extracting period name before '-'
            period_key = period.split('-')[0].strip()
            
            # Iterate over each day (from Monday to Friday)
            for day in df.columns[1:]:  # Skip the first column which is 'Period-Day'
                subject_info = row[day]
                
                if pd.notna(subject_info) and period_key in input_data.all_periods_dict[day]:
                    # Initialize day-period structure
                    if day not in timetable_dict[cls][section]:
                        timetable_dict[cls][section][day] = {}
                    timetable_dict[cls][section][day][period_key] = subject_info

                    
                        
                elif pd.isna(subject_info) and period_key in input_data.all_periods_dict[day]:
                    # Handle empty periods by setting a placeholder if needed
                    timetable_dict[cls][section][day][period_key] = ""
    # Initialize dictionaries for teacher and classroom timetables
    classroom_timetable = {
        str(classroom): {day: {period: "" for period in input_data.all_periods_dict[day]} for day in input_data.day_list}
        for classroom in input_data.classrooms_list
    }
    teacher_timetable = {
        teacher: {day: {period: "" for period in input_data.all_periods_dict[day]} for day in input_data.day_list}
        for teacher in input_data.teachers_list
    }

    # Loop through the timetable_data to populate teacher and classroom timetables
    for class_name, sections in timetable_dict.items():
        for section, days in sections.items():
            for day, periods in days.items():
                for period, subject_info in periods.items():
                    if pd.notna(subject_info):
                        if len(subject_info.split("<>"))==3:
                            subject, teacher, classroom=subject_info.split("<>")
                            # Populate teacher_timetable
                            if teacher not in teacher_timetable:
                                teacher_timetable[teacher] = {}
                            teacher_timetable[teacher][day][period] = f"{subject}<>{class_name}({section})<>{classroom}"

                            # Populate classroom_timetable
                            if classroom not in classroom_timetable:
                                classroom_timetable[classroom] = {}
                            classroom_timetable[classroom][day][period] = f"{subject}<>{class_name}({section})<>{teacher}"

                     # Check if the period has an assignment
                        # Split the subject info to get the subject, teacher, and classroom details
                        elif len(subject_info.split("<>"))>3:
                            for entry in subject_info.split(','):
                                subject, teacher, classroom = entry.split('<>')
                                
                                # Populate teacher_timetable
                                if teacher not in teacher_timetable:
                                    teacher_timetable[teacher] = {}
                                teacher_timetable[teacher][day][period] = f"{subject}<>{class_name}({section})<>{classroom}"

                                # Populate classroom_timetable
                                if classroom not in classroom_timetable:
                                    classroom_timetable[classroom] = {}
                                classroom_timetable[classroom][day][period] = f"{subject}<>{class_name}({section})<>{teacher}"       

    return timetable_dict, teacher_timetable, classroom_timetable