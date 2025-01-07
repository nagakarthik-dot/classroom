# global_data.py
from Utilities import read_input,find_excel_files
from Constants import input_full_path
paths = find_excel_files(input_full_path)
        
if isinstance(paths, list) and paths:
    path = paths[0]
class GlobalData:
    def __init__(self, input_path):
        (self.class_subject_teacher_tuples,
         self.day_list,
         self.class_subject_dict,
         self.final_available_dict,
         self.teachers_list,
         self.class_list,
         self.classrooms_list,
         self.days_dict,
         self.all_periods_dict,
         self.elective_groups, 
         self.min_workload_dict,
         self.max_workload_dict,
         self.classroom_priority,
         self.class_section_elective_tuples,
         self.class_section_dict,
         self.class_type_dict,
         self.classroom_capacity_dict,
         self.class_strength,
         self.period_order,
         self.timings_days,
         self.teacher_max_workload_df) = read_input(input_path)

