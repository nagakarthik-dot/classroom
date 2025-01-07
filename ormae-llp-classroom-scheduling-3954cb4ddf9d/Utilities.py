from get_input_paths import find_excel_files,config_full_path,load_config
from libraries import*
import Constants as const
import json
from loger_config import custom_logger



def read_input(input_path):
    def load_config(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)

    configs = load_config(config_full_path)
        
    # Read data from Excel sheets into DataFrames using config
    sheet_names = configs["sheets"]
    column_names = configs["columns"]
    
    Weekly_time_reqd_df = pd.read_excel(input_path, sheet_name=sheet_names["class_subject_details"])
    Weekly_schedule_df = pd.read_excel(input_path, sheet_name=sheet_names["period_master"], header=0)
    teacher_availability_df = pd.read_excel(input_path, sheet_name=sheet_names["teachers_availability"])
    classroom_df = pd.read_excel(input_path, sheet_name=sheet_names["classrooms_master"])
    Elective_df = pd.read_excel(input_path, sheet_name=sheet_names["elective_subjects"])
    time_slot_df = pd.read_excel(input_path, sheet_name=sheet_names["Daily period_Master"])
    print(time_slot_df)
    # Column names based on configuration
    class_subject_columns = column_names["class_subject_details"]
    period_master_columns = column_names["period_master"]
    teachers_availability_columns = column_names["teachers_availability"]
    classrooms_master_columns = column_names["classrooms_master"]
    elective_subjects_columns = column_names["elective_subjects"]
    time_slot_columns = column_names["Daily period_Master"]
    
    
    classrooms_list = classroom_df[classrooms_master_columns["classroom_name"]].to_list()
    classroom_capacity_dict = classroom_df.set_index(classrooms_master_columns["classroom_name"])[classrooms_master_columns["classroom_capacity"]].to_dict()
    days_dict = {}
    #Iterate through each row in the DataFrame
    for index, row in Weekly_schedule_df.iterrows():
        day = row[period_master_columns['day']]  # assuming 'Day' is the name of the first column
        periods = row[period_master_columns["number_of_periods"]]  # assuming 'Number of Periods' is the second column
        
        
        # Add the day as a key and the rest as values in a list
        if day not in days_dict:
            days_dict[day] = []
    
        days_dict[day]=[periods]
    #print(days_dict)
    day_list=list(days_dict.keys())

    all_periods_dict = {}
    for day, info in  days_dict.items():
        number_of_periods = days_dict[day][0]
        all_periods_dict[day] = [f"Period_{i}" for i in range(1, int(number_of_periods) + 1)]
    
    class_subject_dict = {}
    classroom_priority = {}
    class_section_dict = {}
    class_strength = {}

    for index, row in Weekly_time_reqd_df.iterrows():
        class_name = row[class_subject_columns["class"]]
        section_name = row[class_subject_columns["section"]]
        subject = row[class_subject_columns["subject"]]
        primary_teacher = row[class_subject_columns["primary_teacher"]]
        secondary_teachers = [row[class_subject_columns["secondary_teachers"]]]
        periods_per_week = row[class_subject_columns["periods_per_week"]]
        classroom_reqd = row[class_subject_columns["classroom_reqd"]]
        strength = row[class_subject_columns["strength"]]

        if class_name not in class_subject_dict:
            class_subject_dict[class_name] = {}
        if section_name not in class_subject_dict[class_name]:
            class_subject_dict[class_name][section_name] = {}
        if subject not in class_subject_dict[class_name][section_name]:
            class_subject_dict[class_name][section_name][subject] = [primary_teacher, secondary_teachers, periods_per_week]

        if not pd.isna(classroom_reqd):
            classroom_priority[(class_name, section_name, subject)] = classroom_reqd

        if class_name not in class_section_dict:
            class_section_dict[class_name] = []
        if section_name not in class_section_dict[class_name]:
            class_section_dict[class_name].append(section_name)

        if (class_name, section_name) not in class_strength:
            class_strength[(class_name, section_name)] = strength

    class_type_dict = {}
    distinct_class_types = Weekly_time_reqd_df[class_subject_columns["Class_type"]].unique()
    for class_type in distinct_class_types:
        class_names = Weekly_time_reqd_df[Weekly_time_reqd_df[class_subject_columns["Class_type"]] == class_type][class_subject_columns["class"]].unique().tolist()
        class_type_dict[class_type] = class_names

    class_list = list(class_subject_dict.keys())
    sections_list = []
    subjects_list = []
    teachers_list = []  

    for class_name, sections in class_subject_dict.items():
        for section_name, subjects in sections.items():
            if section_name not in sections_list:
                sections_list.append(section_name)
            for subject, teachers in subjects.items():
                if subject not in subjects_list:
                    subjects_list.append(subject)
                primary_teacher, secondary_teachers, _ = teachers
                if primary_teacher and primary_teacher not in teachers_list:
                    teachers_list.append(primary_teacher)
                for teacher in secondary_teachers:
                    if teacher and teacher not in teachers_list:
                        teachers_list.append(teacher)

    teachers_list = [teacher for teacher in teachers_list if teacher is not None and not (isinstance(teacher, float) and math.isnan(teacher))]

    teacher_availability = {}
    class_subject_teacher_tuples = []
    for class_name, sections in class_subject_dict.items():
        for section_name, subjects in sections.items():
            for subject, teacher_info in subjects.items():
                primary_teacher, secondary_teachers, _ = teacher_info
                class_subject_teacher_tuples.append((class_name, section_name, subject, primary_teacher))
                class_subject_teacher_tuples.extend(
                    (class_name, section_name, subject, teacher)
                    for teacher in secondary_teachers if not pd.isna(teacher)
                )

    day_period_cols = teacher_availability_df.columns[5:]
    teacher_list = teacher_availability_df[teachers_availability_columns["teacher_name"]].tolist()

    teacher_availability = {}
    min_workload_dict = {}
    max_workload_dict = {}

    for index, row in teacher_availability_df.iterrows():
        name = row[teachers_availability_columns["teacher_name"]]
        availability = row[day_period_cols].to_list()
        teacher_availability[name] = availability
        min_workload_dict[name] = row[teachers_availability_columns["min_workload"]]
        max_workload_dict[name] = row[teachers_availability_columns["max_workload"]]

    final_available_dict = {}
    for idx, col in enumerate(day_period_cols):
        day, period = col.split('\n')
        for name, availabilities in teacher_availability.items():
            if not pd.isna(availabilities[idx]):
                final_available_dict[(name, day, period)] = availabilities[idx]

    elective_groups = {}
    for class_name, sections in class_section_dict.items():
        group = Elective_df[Elective_df[elective_subjects_columns["class"]] == class_name]
        for section in sections:
            elective_groups[(class_name, section)] = group[elective_subjects_columns["subjects"]].apply(
                lambda row: [subject for subject in row if pd.notna(subject)], axis=1
            ).tolist()

    class_section_elective_tuples = [
        (class_name, section, subject)
        for (class_name, section), subject_groups in elective_groups.items()
        for subject_group in subject_groups if len(subject_group) > 1
        for subject in subject_group[1:]
    ]
    
    for teacher in teachers_list:
        if teacher not in teacher_list:
            
            error_message = f"ERROR: Availability information is missing for teacher {teacher}"
        
            logging.info(error_message)
            custom_logger.info(error_message)
            # Terminate the script
            sys.exit(1)
            
    
    total_periods = sum(len(periods) for periods in all_periods_dict.values())
    
    timings_days = {}
    for idx, row in time_slot_df.iterrows():
        day_name = row[time_slot_columns['Days']].strip()
        print(f"Day Name: {day_name}")  # Debugging print
        
        # Skip rows where day_name is NaN or not valid
        if pd.isna(day_name) or day_name == '':
            continue
        
        print(f"Processing Day: {day_name}")
        
        # Iterate over columns (excluding the first 'Days' column)
        for col_name in time_slot_df.columns[2:]:
            if pd.notna(row[col_name]):  # Check if the cell is not empty
                period_or_break_name = row[time_slot_columns['Days']]
                timings = row[col_name].strip()  # Extract timings
                print(f"Period/Break Name: {period_or_break_name}, Timings: {timings}")
                
                if period_or_break_name in timings_days:
                    timings_days[period_or_break_name].append(timings)
                else:
                    timings_days[period_or_break_name] = [timings]

   

    # Remove duplicates
    for key in timings_days:
        timings_days[key] = [item for i, item in enumerate(timings_days[key]) if item not in timings_days[key][:i]]

    

    # Get the order of periods from the 'Days' column in time_slot_df
    period_order = time_slot_df[time_slot_columns['Days']].to_list()
    
   
    ########## Teacher KPI calculation data
    teacher_max_workload_df = teacher_availability_df.iloc[:, [0, 1, 3]]
    teacher_max_workload_df.columns=["Teacher_Name","Teacher_Category","Weekly_Max_Capacity"]


    return (
    class_subject_teacher_tuples,
    day_list,
    class_subject_dict,
    final_available_dict,
    teachers_list,
    class_list,
    classrooms_list,
    days_dict,
    all_periods_dict,
    elective_groups, 
    min_workload_dict,
    max_workload_dict,
    classroom_priority,
    class_section_elective_tuples,
    class_section_dict,
    class_type_dict,
    classroom_capacity_dict,
    class_strength,
    period_order,
    timings_days,
    teacher_max_workload_df
)
