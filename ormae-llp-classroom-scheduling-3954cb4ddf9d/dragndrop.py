from scedules_KPIS import*
teacher_list=[]
def get_possible_period_swaps_with_swap_check(input_data,teacher_timetable,timetable):
    #class_combined_df,teacher_combined_df,classroom_combined_df,kpi_dict,teacher_timetable,timetable=extract_output(Optimizer)
    
    final_available=input_data.final_available_dict
    
    possible_swaps_dict = {}

    # Iterate through the entire timetable
    for class_name,timetable_info in timetable.items():  # Each class and section
        for section,timetable_data in timetable_info.items():
            for day in input_data.day_list[:-2]:  # Each day
                for period in input_data.all_periods_dict[day]:  # Each period for the day
                    current_subject_info = timetable[class_name][section][day][period]
                    if current_subject_info:
                        current_subject =(timetable[class_name][section][day][period]).split("<>")[0].strip()
                        
                    else:
                        continue  # No subject in this period, skip
                        
                    current_teacher = input_data.class_subject_dict[class_name][section][current_subject][0]  # Get the teacher for the subject
                        
                    # Create the key: (subject, current period)
                    key = (class_name,section,current_subject, day, period)
                        
                    # Get possible periods where this subject can be moved
                    possible_periods = []
                    
                    for new_day in input_data.day_list[:-2]:  # Check all days
                        for new_period in input_data.all_periods_dict[new_day]:  # Check all periods for each day
                            if new_day == day and new_period == period:
                                continue  # Skip the current period
                            
                            # Check if there is another subject already assigned in the new period for this class
                            other_subject_info = timetable[class_name][section][new_day][new_period]
                            if other_subject_info:
                                
                                other_subject =(timetable[class_name][section][new_day][new_period]).split("<>")[0]
                                
                                if pd.isna(other_subject):
                                    # If no subject is assigned, check if the teacher is available
                                    if is_teacher_available(input_data,class_name,section, current_teacher,current_subject, new_day, new_period,teacher_timetable,final_available):
                                        possible_periods.append((new_day, new_period))
                                else:
                                    # If another subject is assigned, check if swapping is possible
                                    other_teacher = input_data.class_subject_dict[class_name][section][other_subject][0]
                                    
                                    # Check if the current subject's teacher is available in the new period
                                    if is_teacher_available(input_data,class_name,section, current_teacher,current_subject, new_day, new_period,teacher_timetable,final_available):
                                        # Check if the other subject's teacher is available in the current period
                                        if is_teacher_available(input_data,class_name,section, other_teacher,other_subject, day, period,teacher_timetable,final_available):
                                            possible_periods.append((new_day, new_period))  # Possible swap
                            else:
                                possible_periods.append((new_day, new_period))

                    # Add to the dictionary
                    possible_swaps_dict[key] = possible_periods

    return possible_swaps_dict


def is_teacher_available(input_data,cls,sec, teacher,subject, day, period,teacher_timetable,final_available):
    """Check if the teacher is available during the specified period"""
    
    
    
    if (cls,sec) in input_data.elective_groups.keys() and any(subject in group for group in input_data.elective_groups[(cls,sec)]):
        # Find the corresponding teachers for the group of subjects
        group_teachers =[]
        for group in input_data.elective_groups[(cls,sec)]:
            if subject in group:
                for sub in group:
                    group_teachers.append(input_data.class_subject_dict[cls][sec][sub][0])
                    group_teachers=list(set(group_teachers))
                break
        all_teacher_available=True
        for each_teacher in group_teachers:
            if teacher_timetable[each_teacher][day][period]!="" or input_data.final_available_dict[(each_teacher,day,period)]!=1:
                teacher_list.append((each_teacher,day,period))
                
                all_teacher_available=False
                break
        return all_teacher_available
    else:

        if teacher_timetable[teacher][day][period]!='' or input_data.final_available_dict[(teacher,day,period)]!=1:
                
                return False  # Teacher is already assigned during this period
        return True

def possible_df(input_data,teacher_timetable,timetable):
    

    #class_combined_df,teacher_combined_df,classroom_combined_df,kpi_dict,teacher_timetable,timetable,classroom_timetable=extract_output(input_data)
    
    
    data=get_possible_period_swaps_with_swap_check(input_data,teacher_timetable,timetable)
    # Step 1: Generate all day-period combinations
    all_combinations = [(day, period) for day in input_data.day_list for period in input_data.all_periods_dict[day]]

    # Step 2: Create the DataFrame
    rows = []
    for (class_name,section, subject_name, day, period), assigned_combinations in data.items():
        # Create a row with class, subject, and day-period combination
        row = {
            'Class': f"{class_name}{section}",
            'Subject': subject_name,
            'Day-Period': f"({day}, {period})"
        }
        
        # For each possible day-period combination, mark 1 if it's present, else 0
        for combo in all_combinations:
            row[combo] = 1 if combo in assigned_combinations else 0
        
        rows.append(row)

    # Create the DataFrame
    available_periods = pd.DataFrame(rows)
    return available_periods
