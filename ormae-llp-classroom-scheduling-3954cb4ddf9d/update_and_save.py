from Update_dict import*
from scedules_KPIS import*
from dragndrop import*
from global_data import GlobalData
from Constants import input_full_path

# Initialize GlobalData with input path once
data = GlobalData(input_full_path)
teacher_timetable,classroom_timetable,timetable_data=extract_data(data)
#possible_dfs = possible_df(data,teacher_timetable,timetable_data)


def update_timetable_and_possibility_df(input_data,file,timetable_data):
            
    new_timetable_data,new_teacher_data,new_classroom_data = update_timetables(input_data,
        file, timetable_data)
    
    
    # Generate new possibility DataFrame after the update
    new_possibility_df = possible_df(input_data,new_teacher_data,new_timetable_data)
    timetable_data=new_timetable_data
    return new_possibility_df,new_timetable_data,new_teacher_data,new_classroom_data


def save_shedules(data,timetable_data,teacher_timetable,classroom_timetable):
    class_combined_df,teacher_combined_df,classroom_combined_df,kpi_dict,teacher_timetable,timetable_data,classroom_timetable=extract_output(data,teacher_timetable,classroom_timetable,timetable_data)
    return teacher_combined_df,classroom_combined_df,kpi_dict


new_possibility_dfs,updated_timetable_dict,updated_teacher_dict,updated_classroom_dict = update_timetable_and_possibility_df(data,file_name,timetable_data,teacher_timetable,classroom_timetable)

teacher_combined_df,classroom_combined_df,kpi_dict=save_shedules(data,updated_timetable_dict,updated_teacher_dict,updated_classroom_dict)
