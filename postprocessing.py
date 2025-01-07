from libraries import*
from loger_config import custom_logger
def extract_schedule(Optimizer):
    """
    Extract the schedule from the optimized model.
    """
    output_records = []
    for day in Optimizer.day_list:
        for period in Optimizer.all_periods_dict[day]:
            for classes in Optimizer.classrooms_list:
                for cls, section, subject, teacher_name in Optimizer.class_subject_teacher_tuples:
                    assignment_key = (cls, section, subject, teacher_name, day, period, classes)
                    if assignment_key in Optimizer.assignment and Optimizer.assignment[assignment_key].X > 0.1:
                        output_records.append({
                            'Class': cls,
                            'Section': section,
                            'Teacher': teacher_name,
                            'Subject': subject,
                            'Day': day,
                            'Period': period,
                            'Classroom': classes
                        })
    
 
    total_req = {}
    unfulfilled_requirements = set()

    # First loop to calculate total required periods
    for class_name, section, subject, teacher_name in Optimizer.class_subject_teacher_tuples:
        primary_teacher = Optimizer.class_subject_dict[class_name][section][subject][0]
        if teacher_name in primary_teacher:
            req = Optimizer.class_subject_dict[class_name][section][subject][2]

            if (class_name, section, subject) not in Optimizer.electives:
                if class_name not in total_req:
                    total_req[class_name] = {}

                if section not in total_req[class_name]:
                    total_req[class_name][section] = 0

                total_req[class_name][section] += req

    # Second loop to check assignments against requirements
    for class_name, section, subject, teacher_name in Optimizer.class_subject_teacher_tuples:
        primary_teacher = Optimizer.class_subject_dict[class_name][section][subject][0]
        secondary_teachers = Optimizer.class_subject_dict[class_name][section][subject][1]
        req = Optimizer.class_subject_dict[class_name][section][subject][2]  # Move this here for clarity

        if not pd.isna(secondary_teachers):
            total_assignments = (
                sum(Optimizer.assignment[class_name, section, subject, primary_teacher, day, period, classes].X
                    for day in Optimizer.day_list
                    for period in Optimizer.all_periods_dict[day]
                    for classes in Optimizer.classrooms_list) +
                sum(Optimizer.assignment[class_name, section, subject, secondary_teacher, day, period, classes].X
                    for secondary_teacher in secondary_teachers
                    for day in Optimizer.day_list
                    for period in Optimizer.all_periods_dict[day]
                    for classes in Optimizer.classrooms_list)
            )
        else:
            total_assignments = sum(Optimizer.assignment[class_name, section, subject, teacher_name, day, period, classes].X
                                    for day in Optimizer.day_list
                                    for period in Optimizer.all_periods_dict[day]
                                    for classes in Optimizer.classrooms_list)

        # Check if total requirements exceed available periods
        if total_req[class_name][section] > sum(len(periods) for periods in Optimizer.all_periods_dict.values()):
            reason = "Total periods required is greater than the available periods"
        else:
            reason = "Teacher is not available"

        # Check if the assignments fulfill the requirements
        if total_assignments < req:
            unfulfilled_requirements.add((class_name, subject, primary_teacher, section, req, total_assignments, reason))

    # Log unfulfilled requirements
    unfulfilled_requirements = list(unfulfilled_requirements)
    if len(unfulfilled_requirements) > 0:
        custom_logger.info(unfulfilled_requirements)

          
    return output_records,unfulfilled_requirements
