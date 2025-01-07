
from libraries import *
from loger_config import custom_logger
import pandas as pd

def extract_data(Optimizer):
    
    classroom_timetable = {
        classroom: {day: {period: "" for period in Optimizer.all_periods_dict[day]} for day in Optimizer.day_list}
        for classroom in Optimizer.classrooms_list
    }
    teacher_timetable = {
        teacher: {day: {period: "" for period in Optimizer.all_periods_dict[day]} for day in Optimizer.day_list}
        for teacher in Optimizer.teachers_list
    }
    
    
    # teacher_workload = {teacher: {day: 0 for day in Optimizer.day_list} for teacher in set(teacher for _, _,_, teacher in Optimizer.class_subject_teacher_tuples)}
    # classroom_workload = {classroom: {day: {period: 0 for period in Optimizer.all_periods_dict[day]} for day in Optimizer.day_list} for classroom in Optimizer.classrooms_list}
    subject_records =[]
    
   
   
  
    timetable_data = {cls:{section:{day: {period: "" for period in Optimizer.all_periods_dict[day]} for day in Optimizer.day_list}for _, section,_, teacher in Optimizer.class_subject_teacher_tuples}for cls, _,_, teacher in Optimizer.class_subject_teacher_tuples}
    for class_name in Optimizer.class_list:
        for section in Optimizer.section_lst[class_name]:
            
            for day in Optimizer.day_list:
                for period in Optimizer.all_periods_dict[day]:
                    for cls, sec, subject, teacher_name in Optimizer.class_subject_teacher_tuples:
                        if cls == class_name and sec == section:
                            for classroom in Optimizer.classrooms_list:
                                assignment_key = (class_name, section, subject, teacher_name, day, period, classroom)
                                
                                if assignment_key in Optimizer.assignment and Optimizer.assignment[assignment_key].X > 0.1:
                                    subject_label = f"{subject}<>{teacher_name}<>{classroom}"
                                    subject_label_cls = f"{subject}<>{class_name}({section})<>{teacher_name}"
                                    subject_label_teach = f"{subject}<>{class_name}({section})<>{classroom}"

                                    # Add subject to the timetable data for that day and period
                                    if timetable_data[class_name][section][day][period]:
                                        timetable_data[class_name][section][day][period] += f",{subject_label}"
                                    else:
                                        timetable_data[class_name][section][day][period] = subject_label

                                    classroom_timetable[classroom][day][period] = subject_label_cls
                                    teacher_timetable[teacher_name][day][period] = subject_label_teach
                                    

            # Convert the list of records into a DataFrame
    return teacher_timetable,classroom_timetable,timetable_data
def calculate_workload(teacher_timetable, classroom_timetable):
    """
    Calculate workload for teachers and classrooms based on timetable data.
    
    Parameters:
    - teacher_timetable (dict): A dictionary with teacher schedules by day and period.
    - classroom_timetable (dict): A dictionary with classroom schedules by day and period.
    
    Returns:
    - teacher_workload (dict): A dictionary with workload counts for each teacher by day.
    - classroom_workload (dict): A dictionary with workload counts for each classroom by day and period.
    """
    # Initialize teacher and classroom workload dictionaries
    teacher_workload = {
        teacher: {day: 0 for day in teacher_timetable[teacher].keys()}
        for teacher in teacher_timetable
    }
    
    classroom_workload = {
        classroom: {day: {period: 0 for period in classroom_timetable[classroom][day]}
                    for day in classroom_timetable[classroom]}
        for classroom in classroom_timetable
    }
    
    # Calculate teacher workload
    for teacher, days in teacher_timetable.items():
        for day, periods in days.items():
            for period, assignment in periods.items():
                if assignment:  # If there is an assignment for this period
                    teacher_workload[teacher][day] += 1
    
    # Calculate classroom workload
    for classroom, days in classroom_timetable.items():
        for day, periods in days.items():
            for period, assignment in periods.items():
                if assignment:  # If there is an assignment for this period
                    classroom_workload[classroom][day][period] += 1
    
    return teacher_workload, classroom_workload
import pandas as pd

def get_subject_records(timetable_data, Optimizer):
    """
    Generate a DataFrame containing subject assignment records for each class, section, subject, teacher, classroom, day, and period.
    
    Parameters:
    - timetable_data (dict): Nested dictionary with timetable assignments for each class and section.
    - Optimizer (object): Optimizer instance containing subject, teacher, and classroom data.

    Returns:
    - subject_records_df (DataFrame): DataFrame with columns for class, section, subject, primary teacher, secondary teacher, classroom, day, and period.
    """
    subject_records = []

    for class_name, sections in timetable_data.items():
        for section, days in sections.items():
            for day, periods in days.items():
                for period, assignment in periods.items():
                    if assignment:  # If there's an assignment in this period
                        lst = assignment.split("<>")
                        if len(lst) == 3:
                            subject, teacher, classroom =lst[0],lst[1],lst[2]
                            primary_teacher = ""
                            secondary_teacher = ""
                            
                            # Check if the teacher is primary or secondary for this subject
                            if teacher == Optimizer.class_subject_dict[class_name][section][subject][0]:
                                primary_teacher = teacher
                            elif teacher in Optimizer.class_subject_dict[class_name][section][subject][1]:
                                secondary_teacher = teacher

                            # Append the record
                            record = {
                                "Class": class_name,
                                "Section": section,
                                "Subject": subject,
                                "Primary_Teacher": primary_teacher,
                                "Secondary_Teacher": secondary_teacher,
                                "Classroom": classroom,
                                "Day": day,
                                "Period": period
                            }
                            subject_records.append(record)
                        else:
                            for subject_info in assignment.split(','):
                                subject, teacher, classroom = subject_info.split('<>')
                                primary_teacher = ""
                                secondary_teacher = ""
                                
                                # Check if the teacher is primary or secondary for this subject
                                if teacher == Optimizer.class_subject_dict[class_name][section][subject][0]:
                                    primary_teacher = teacher
                                elif teacher in Optimizer.class_subject_dict[class_name][section][subject][1]:
                                    secondary_teacher = teacher

                                # Append the record
                                record = {
                                    "Class": class_name,
                                    "Section": section,
                                    "Subject": subject,
                                    "Primary_Teacher": primary_teacher,
                                    "Secondary_Teacher": secondary_teacher,
                                    "Classroom": classroom,
                                    "Day": day,
                                    "Period": period
                                }
                                subject_records.append(record)
        
    # Convert the list of records into a DataFrame
    subject_records_df = pd.DataFrame(subject_records, columns=[
        "Class", "Section", "Subject", "Primary_Teacher", "Secondary_Teacher", "Classroom", "Day", "Period"
    ])
    
    return subject_records_df


def create_class_timetable_df(Optimizer,timetable_data): 
        
    Class_output_dict ={}
    #_,_,timetable_data,_,_,_=extract_data(Optimizer)
    with pd.ExcelWriter("class_timetables.xlsx") as writer:
        for cls, timetable_info in timetable_data.items():
            for section,timetable in timetable_info.items():
                df = pd.DataFrame.from_dict(timetable, orient='index').transpose()
                    
                break_count = 0
                df.insert(0,"Period-Day",[f'{df.index[i]}-\n({Optimizer.timings_days[df.index[i]][0]})' for i in range(len(df.index))])
                tt_cols = df.columns

                days_temp_lst = []
                for p in Optimizer.period_order:
                    if p in df.index:
                        days_temp_lst.append(df.loc[p].to_list())
                    else:
                        if p != 'BREAK':
                            days_temp_lst.append([Optimizer.timings_days[p][0]] + [p for i in range(len(df.columns)-1)])
                        else:
                            days_temp_lst.append([Optimizer.timings_days[p][break_count]] + [p for i in range(len(df.columns)-1)])
                            break_count+=1
                days_df = pd.DataFrame(days_temp_lst,columns=tt_cols)
            
                # # Save the final DataFrame to an Excel file
                timetable_filename = f"{cls}{section}.xlsx"
                days_df.to_excel(timetable_filename)
                print(f"Timetable for {cls}{section} saved to '{timetable_filename}'")
                Class_output_dict[f"{cls}{section}"]=(days_df)
    return Class_output_dict      
    ## 2. Creating Classroom output data     

def create_classroom_timetable_df(Optimizer,classroom_timetable): 
        
    Classroom_output_dict ={}
    #_,classroom_timetable,timetable_data,_,_,_=extract_data(Optimizer)    
    with pd.ExcelWriter("classroom_timetables.xlsx") as writer:
        for classroom, timetable in classroom_timetable.items():
            break_count = 0
            
            df = pd.DataFrame.from_dict(timetable, orient='index').transpose()
            
            df.insert(0,"Period-Day",[f'{df.index[i]}-\n({Optimizer.timings_days[df.index[i]][0]})' for i in range(len(df.index))])
            tt_cols = df.columns

            days_temp_lst = []
            for p in Optimizer.period_order:
                if p in df.index:
                    days_temp_lst.append(df.loc[p].to_list())
                else:
                    if p != 'BREAK':
                        days_temp_lst.append([Optimizer.timings_days[p][0]] + [p for i in range(len(df.columns)-1)])
                    else:
                        days_temp_lst.append([Optimizer.timings_days[p][break_count]] + [p for i in range(len(df.columns)-1)])
                        break_count+=1
            final_df = pd.DataFrame(days_temp_lst,columns=tt_cols)
            final_df.to_excel(writer, sheet_name=f"Classroom {classroom}", index=False)
            Classroom_output_dict[f"{classroom}"] = final_df
    for classroom, timetable in classroom_timetable.items():
        # Create a DataFrame from the timetable data
        df = pd.DataFrame(timetable)
    
    print("Classroom timetables saved to 'classroom_timetables.xlsx'.")

    return Classroom_output_dict
    # Loop through each classroom and create a dataframe for each timetable
    
    # 3. Teacher output data     
def create_teacher_timetable_df(Optimizer,teacher_timetable): 
        
    Teacher_output_dict ={}
    #teacher_timetable,classroom_timetable,timetable_data,_,_,_=extract_data(Optimizer)    
    with pd.ExcelWriter("Teacher_timetables.xlsx") as writer:
        for teacher, timetable in teacher_timetable.items():
            break_count = 0
            
            df = pd.DataFrame.from_dict(timetable, orient='index').transpose()
            
            df.insert(0,'Period-Day',[f'{df.index[i]}-\n({Optimizer.timings_days[df.index[i]][0]})' for i in range(len(df.index))])
            tt_cols = df.columns

            days_temp_lst = []
            for p in Optimizer.period_order:
                if p in df.index:
                    days_temp_lst.append(df.loc[p].to_list())
                else:
                    if p != 'BREAK':
                        days_temp_lst.append([Optimizer.timings_days[p][0]] + [p for i in range(len(df.columns)-1)])
                    else:
                        days_temp_lst.append([Optimizer.timings_days[p][break_count]] + [p for i in range(len(df.columns)-1)])
                        break_count+=1
            final_df = pd.DataFrame(days_temp_lst,columns=tt_cols)
            final_df.to_excel(writer, sheet_name=f"Teacher {teacher}", index=False)
            Teacher_output_dict[f"{teacher}"] = final_df
    return Teacher_output_dict


def combined_dfs(Optimizer,teacher_timetable,timetable_data,classroom_timetable):
    Class_output_dict = create_class_timetable_df(Optimizer,timetable_data)
    Classroom_output_dict =create_classroom_timetable_df(Optimizer,classroom_timetable)
    Teacher_output_dict=create_teacher_timetable_df(Optimizer,teacher_timetable)
    # Merging the Class, teacher and classroom dfs in one df for each with one column as the label for each class, teacher and Classroom 
    # 1. Class dfs
    cls_dfs=[]
    for filename, df in Class_output_dict.items():
        # Add index column
        df = df.reset_index()
        # Add filename column
        df['filename'] = filename
       
        cls_dfs.append(df)
    if cls_dfs:
        class_combined_df = pd.concat(cls_dfs, ignore_index=True)
    else:
        class_combined_df = pd.DataFrame()
    class_combined_df.to_excel("classcombined_excel.xlsx")
    # 2. Classroom Dfs
    classroom_dfs=[]
    for filename, df in Classroom_output_dict.items():
        # Add index column
        df = df.reset_index()
        # Add filename column
        df['filename'] = filename
       
        classroom_dfs.append(df)
    if classroom_dfs:
        classroom_combined_df = pd.concat(classroom_dfs, ignore_index=True)
    else:
        classroom_combined_df = pd.DataFrame()
    classroom_combined_df.to_excel("classroomcombined_excel.xlsx")
    # Teacher DFs
    teacher_dfs=[]
    for filename, df in Teacher_output_dict.items():
        # Add index column
        df = df.reset_index()
        # Add filename column
        df['filename'] = filename
       
        teacher_dfs.append(df)
    if teacher_dfs:
        teacher_combined_df = pd.concat(teacher_dfs, ignore_index=True)
    else:
        teacher_combined_df = pd.DataFrame()
    teacher_combined_df.to_excel("teachercombined_excel.xlsx")
    print(teacher_combined_df)
    return class_combined_df,teacher_combined_df,classroom_combined_df

############################## Kpis calculation ##########################################################
def create_Kpis(Optimizer,teacher_timetable,classroom_workload,teacher_workload,subject_records):
# 1. Classroom KPI's
# 1.1  Classroom daily utilization 
# 1.2 Classroom weekly utilization 
    kpi_dict={}
# 1.1 Classroom daily utilization 
    # Loop through each classroom and create a dataframe for each timetable
    #teacher_timetable,classroom_timetable,timetable_data,classroom_workload,teacher_workload,subject_records=extract_data(Optimizer)   
    for classroom, timetable in teacher_timetable.items():
        # Create a DataFrame from the timetable data
        df = pd.DataFrame(timetable)
    
    # Create a DataFrame for the classroom workload
    classroom_workload_data = []
    for classroom, days in classroom_workload.items():
        for day, periods in days.items():
            for period, workload in periods.items():
                classroom_workload_data.append([classroom, day, period, workload])
    
    classroom_workload_df = pd.DataFrame(classroom_workload_data, columns=["Classroom", "Day", "Period", "Workload"])
    
    # Save the classroom workload to a new Excel file
    classroom_workload_df.to_excel("classroom_workload.xlsx", index=False)
    print("Classroom workload saved to 'classroom_workload.xlsx'.")
    
    
    # Step 3: Calculate daily utilization for each classroom
    classroom_daily_utilization = classroom_workload_df.groupby(['Classroom', 'Day']).agg(
        Total_available_periods=('Workload', 'size'),  # Count all periods in a day
        Total_used_periods=('Workload', 'sum')     # Sum of periods that are actually used
    ).reset_index()
    classroom_daily_utilization['Utilization (%)'] = (classroom_daily_utilization['Total_used_periods'] / classroom_daily_utilization['Total_available_periods']) * 100
    classroom_daily_utilization_kpi_df = classroom_daily_utilization[['Classroom', 'Day', 'Total_available_periods', 'Total_used_periods', 'Utilization (%)']]
    kpi_dict["Classroom_daily_utilization"]=(classroom_daily_utilization_kpi_df)
    classroom_daily_utilization_kpi_df.to_excel("Classroom_kpi.xlsx",index=False)



# 1.2 Classroom weekly utilization 

    weekly_utilization = classroom_workload_df.groupby(['Classroom', 'Day']).agg(
    total_periods=('Workload', 'size'),  # Count all rows (periods)
    used_periods=('Workload', 'sum')     # Sum of 'Usage' (1 for used, 0 for not used)
).reset_index()

    # Step 3: Aggregate over the whole week for each classroom
    classroom_weekly_utilization = weekly_utilization.groupby('Classroom').agg(
        total_periods=('total_periods', 'sum'),
        used_periods=('used_periods', 'sum')
    ).reset_index()
    
    # Step 4: Calculate utilization percentage
    classroom_weekly_utilization['Utilization (%)'] = (classroom_weekly_utilization['used_periods'] / classroom_weekly_utilization['total_periods']) * 100
    classroom_weekly_utilization_df=classroom_weekly_utilization[['Classroom', 'total_periods', 'used_periods', 'Utilization (%)']]
    kpi_dict["classroom_weekly_utilization"]=(classroom_weekly_utilization_df)
    
    classroom_weekly_utilization_df.to_excel("kpi.xlsx", index=False)
    
    teacher_day_availability = {}

    # Iterate through the final_available_dict to calculate availability for each teacher per day
    for (teacher_name, day,period), availability in Optimizer.final_available_dict.items():
        if period in Optimizer.all_periods_dict[day]:
            #if day in Optimizer.day_list:
                if teacher_name not in teacher_day_availability:
                    teacher_day_availability[teacher_name] = {}

                if day not in teacher_day_availability[teacher_name]:
                    teacher_day_availability[teacher_name][day] = 0
                
                # Sum the availabilities
                teacher_day_availability[teacher_name][day] += availability
    # 2. Teacher_kpi
      # 2.1 Weekly utilization KPI
    daily_workload_data = []
    weekly_workload_data = []
    for teacher, workload in teacher_workload.items():
        total_workload = sum(workload.values())        
        weekly_workload_data.append([teacher, total_workload])
        for day,value in workload.items():
            if day in teacher_day_availability.get(teacher_name, {}):
                if teacher_day_availability[teacher][day]!=0:
                    daily_utilization =  (value/teacher_day_availability[teacher][day])*100
                    daily_workload_data.append([day,teacher,value,teacher_day_availability[teacher][day],daily_utilization])
                
        
    weekly_workload_df = pd.DataFrame(weekly_workload_data, columns=["Teacher", "Weekly Workload"])
    daily_workload_df =  pd.DataFrame(daily_workload_data, columns=["day","Teacher", "daily Workload","Total Availability","Total Utilization"])
    
    # Filter teacher availability for weekly workload
    filtered_availability = Optimizer.teacher_max_workload_df[
        Optimizer.teacher_max_workload_df["Teacher_Name"].isin(weekly_workload_df['Teacher'])
    ]
    # Merge and calculate weekly utilization
    weekly_workload_df = weekly_workload_df.merge(
        filtered_availability, 
        left_on="Teacher", 
        right_on="Teacher_Name", 
        how="left"
    )
    subject_df = pd.DataFrame(subject_records)
    subject_df.to_excel("Subject_distribution.xlsx",index=False)
    weekly_workload_df = weekly_workload_df.drop(columns=["Teacher_Name"])
    weekly_workload_df['Utilization (%)'] = (weekly_workload_df['Weekly Workload'] / weekly_workload_df["Weekly_Max_Capacity"]) * 100
    kpi_dict["Teacher_kpi"]=(weekly_workload_df)
    weekly_workload_df.to_excel("teacher_weekly_workload.xlsx", index=False)
    print("Teacher weekly workload saved to 'teacher_weekly_workload.xlsx'.")
    #class_combined_df.to_excel("classcombined_excel.xlsx")
    
    ################### Daily teacher utilization KPI ###########################
    daily_workload_df.to_excel("Daily_teachers_utilization.xlsx",index=False)
    kpi_dict["Teachers_daily_Utilization"] =(daily_workload_df)

    ################### Subject Distribution KPI ######################
    kpi_dict["Subject_distribution"] = (subject_df)
    return kpi_dict

def extract_output(Optimizer,teacher_timetable,classroom_timetable,timetable_data):
    # teacher_timetable,classroom_timetable,timetable_data,classroom_workload,teacher_workload,subject_records=extract_data(Optimizer)
    class_combined_df,teacher_combined_df,classroom_combined_df=combined_dfs(Optimizer,teacher_timetable,timetable_data,classroom_timetable)
    teacher_workload, classroom_workload=calculate_workload(teacher_timetable, classroom_timetable)
    subject_records=get_subject_records(timetable_data,Optimizer)
    kpi_dict = create_Kpis(Optimizer,teacher_timetable,classroom_workload,teacher_workload,subject_records)
    
    return class_combined_df,teacher_combined_df,classroom_combined_df,kpi_dict,teacher_timetable,timetable_data,classroom_timetable
 