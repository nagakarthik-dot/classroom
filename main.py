from Optimizer import optimizer
from postprocessing import extract_schedule
from Constants import input_full_path
from Utilities import read_input,find_excel_files
from libraries import*
from loger_config import custom_logger
from scedules_KPIS import extract_output
from dragndrop import*
from Update_dict import*


def create_output(schedule, output_dir='outputs'):
    """
    Save the schedule to an Excel file.
    """
    os.makedirs(output_dir, exist_ok=True)
    df = pd.DataFrame(schedule, columns=['Class', 'Section', 'Teacher', 'Subject', 'Day', 'Period', 'Classroom'])
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_filename = os.path.join(output_dir, f'schedule_{timestamp}.xlsx')
    df.to_excel(excel_filename, index=False, sheet_name='Schedule')
    print(f"Excel file '{excel_filename}' created successfully.")
 
def main():
    try:
        custom_logger.info("STEP 1: Starting the script.")
        paths = find_excel_files(input_full_path)
        
        if isinstance(paths, list) and paths:
            path = paths[0]
            custom_logger.info("STEP 2: Found Excel files.")
        else:
            raise ValueError("The input_full_path list is empty or invalid.")
        
        custom_logger.info("STEP 3: Valid input path identified.")
        (class_subject_teacher_tuples, day_list, class_subject_dict, final_available_dict, teachers_list, class_list, 
         classrooms_list, days_dict, all_periods_dict, elective_groups, min_workload, max_workload, 
         classroom_priority, electives, section_lst, class_type, classroom_capacity_dict, 
         class_strength, period_order, timings_days,teacher_max_workload_df) = read_input(path)
        
        custom_logger.info("STEP 4: Input data read successfully.")

        Optimizer = optimizer( 
            class_subject_teacher_tuples, day_list, class_subject_dict, final_available_dict, teachers_list, 
            class_list, classrooms_list, days_dict, all_periods_dict, elective_groups, min_workload, max_workload, 
            classroom_priority, electives, section_lst, class_type, classroom_capacity_dict, class_strength, period_order, timings_days,teacher_max_workload_df
        )
        custom_logger.info("STEP 5: Optimizer initialized.")
        
        Optimizer.initialize_problem()
        custom_logger.info("STEP 5.1: Problem initialized.")
        
        Optimizer.variables()
        custom_logger.info("STEP 5.2: Variables defined.")
        
        Optimizer.create_constraints()
        custom_logger.info("STEP 5.3: Constraints created.")
        
        Optimizer.objective_function()
        custom_logger.info("STEP 5.4: Objective function set.")

        # Set stopping criteria
        # Optimizer.model.setParam('TimeLimit', 3600)  # 3600 seconds = 1 hour
        # Optimizer.model.setParam('MIPGap', 0.01)     # 1% optimality gap
        # Optimizer.model.setParam('IterationLimit', 500000)  # Limit to 500000 iterations

        # Optimize the model
        Optimizer.model.optimize()
        custom_logger.info("STEP 5.5: Optimization completed.")

        Optimizer.model.write("lp_file1.lp")
   
        # Extract the schedule and convert to DataFrames
        teacher_timetable,classroom_timetable,timetable=extract_data(Optimizer)
        class_combined_df,teacher_combined_df,classroom_combined_df,kpi_dict,a,b,c = extract_output(Optimizer,teacher_timetable,classroom_timetable,timetable)
        output_records,unfulfilled_requirements = extract_schedule(Optimizer)
        
        possible_dfs = possible_df(Optimizer,teacher_timetable,timetable)
        possible_dfs.to_excel("requirement.xlsx")
        
        #########################3
        
        # def update_timetable_and_possibility_df(Optimizer,file,timetable,teacher_data):
        #     """
        #     Updates the timetable and teacher data based on a drag-and-drop action, then regenerates possibility_df.
        #     """
        #     # Perform the drag-and-drop action (modify timetable and teacher_data as needed)
        #     timetable_data, teacher_data = convert_excel_to_timetable_dict(
        #         file, timetable, teacher_data
        #     )
            
        #     # Generate new possibility DataFrame after the update
        #     new_possibility_df = possible_df(Optimizer,teacher_data,timetable_data)
            
        #     return new_possibility_df
       
        # new_possibility_dfs = update_timetable_and_possibility_df(Optimizer,file_name,timetable,teacher_timetable)
        # new_possibility_dfs.to_excel("poss.xlsx")

         
        
        # Print DataFrames
        print("Class Timetable DataFrame:")
        class_combined_df.to_excel("class_sched.xlsx")
        print(class_combined_df)

        print("\nTeacher Timetable DataFrame:")
        teacher_combined_df.to_excel("teacher_sched.xlsx")
        print(teacher_combined_df)

        print("\n Classroom Timetable DataFrame:")
        classroom_combined_df.to_excel("classroom_sched.xlsx")
        print(classroom_combined_df)

        print("\n KPI'S:")
        print(kpi_dict)
        
        
    except Exception as e:
        custom_logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

