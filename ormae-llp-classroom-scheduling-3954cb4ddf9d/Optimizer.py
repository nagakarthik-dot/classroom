import datetime

import gurobipy as gp
from gurobipy import GRB

from Constants import input_full_path
from Utilities import read_input,find_excel_files
import logging
import sys
import re
import random
from libraries import*



logging.basicConfig(filename="log_output.log", level=logging.DEBUG,
                    format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")
      
class optimizer:
    """
    Class for scheduling optimization.
    """
    
    

    def __init__(self,class_subject_teacher_tuples,day_list,class_subject_dict,final_available_dict,teachers_list,class_list,classrooms_list,days_dict,all_periods_dict,elective_groups,min_workload ,max_workload,classroom_priority,electives,section_lst,class_type,classroom_capacity_dict,class_strength,period_order,timings_days,teacher_max_workload_df):
        """
        Attributes:
            class_subject_teacher_tuples(list) : List of unique combinations of teacher,class and subjects
            day_list (list): List of unique day names.
            period_list(list): List of periods in a day .
            period_type_list(list) : List of types of period in a week.
            class_subject_dict(dictionary) : Dictionary containing the classes mapped to the subject it have which is
            mapped to the list of teacher which teach that subject in the class and the number of classes of each type
            required for that subject.
            teachers_list(list) = List of the names of all the teachers
            """
        
        self.class_subject_teacher_tuples = class_subject_teacher_tuples
        self.day_list = day_list
        self.class_subject_dict = class_subject_dict
        self.teachers_list = teachers_list
        self.final_available_dict = final_available_dict
        self.class_list = class_list
        self.days_dict = days_dict
        self.all_periods_dict = all_periods_dict
        self.classrooms_list = classrooms_list
        self.elective_groups = elective_groups
        self.min_workload=min_workload
        self.max_workload=max_workload
        self.classroom_priority=classroom_priority
        self.electives=electives
        self.section_lst=section_lst
        self.class_type = class_type
        self.classroom_capacity_dict = classroom_capacity_dict
        self.class_strength = class_strength
        self.period_order = period_order
        self.timings_days = timings_days
        self.teacher_max_workload_df = teacher_max_workload_df
        


    def initialize_problem(self):
        """
        
        Initialize the optimization problem by creating a Gurobi model object.
        """
        self.model = gp.Model("Classroom_Scheduling")

###################################################### Variables ####################################################################################
    def variables(self):    
        
    #1. Assignment variable
        self.assignment = {(class_name,section, subject,teacher_name, day, period,classroom): self.model.addVar(vtype=GRB.BINARY, name=f"assignment of {class_name},{section},{subject},{teacher_name},{day},{period},{classroom}")
                    for class_name, section,subject, teacher_name in self.class_subject_teacher_tuples
                    for day in self.day_list
                    for period in self.all_periods_dict[day]
                    for classroom in self.classrooms_list
                    }
    #2. Penalty Variaable   
        self.penalty = {(class_name,section, subject, teacher_name,day): self.model.addVar(vtype=GRB.BINARY, name=f"penalty of {class_name},{subject},{teacher_name},{day}")
                    for class_name, section,subject, teacher_name in self.class_subject_teacher_tuples
                    for day in self.day_list}
        
        
     
        
###################################################### Defining Constraints ####################################################################       
    def create_constraints(self):


    # 1. Teacher availability constraint
        
        for class_name,section,subject, teacher_name in self.class_subject_teacher_tuples:
            
            for day in self.day_list:
                for period in self.all_periods_dict[day]:
                    for classes in self.classrooms_list:
                   
                        # Check if the subject is in the subjects dictionary for the specific class
                        if class_name in self.elective_groups.keys() and any(subject in group for group in self.elective_groups[class_name]):
                            # Find the corresponding teachers for the group of subjects
                            group_teachers =[]
                            for group in self.elective_groups[class_name]:
                                if subject in group:
                                    for sub in group:
                                        group_teachers.append(self.class_subject_dict[class_name][sub][0])
                                        group_teachers=list(set(group_teachers))
                                    break
                                                      
                            self.model.addConstr(
                                self.assignment[(class_name,section, subject, teacher_name,day, period,classes)] <= 
                                min(self.final_available_dict[(teacher, day, period)] for teacher in group_teachers),name=f"TeacherAvailability_{class_name}_{section}_{subject}_{teacher_name}_{day}_{period}_{classes}"
                            ) 

                            # Add the constraint to ensure that all subjects within the same group are assigned to the same period
                            
                        else:
                            self.model.addConstr(
                                self.assignment[(class_name,section, subject, teacher_name,day, period,classes)] <= 
                                self.final_available_dict[(teacher_name,day,period)],name=f"TeacherAvailability_{class_name}_{section}_{subject}_{teacher_name}_{day}_{period}_{classes}"
                            )

    #2. Atmost one subject can be assigned to a teacher in a period
        for teacher_names in self.teachers_list:
            for day in self.day_list:
                for period in self.all_periods_dict[day]:
                    
                    # Constraint to ensure a teacher teaches only one class per period
                    self.model.addConstr(   
                        gp.quicksum(
                            self.assignment[class_name,section, subject, teacher_names,  day, period,classes]
                            for (class_name,section, subject, teach) in self.class_subject_teacher_tuples
                            for classes in self.classrooms_list
                            if teacher_names==teach
                                ) <= 1,f"OneSubjectPerPeriod_{teacher_name}_{day}_{period}"
                        )
    
       # 3. Atmost one subject can be assigned to  class in a particular period of the day
       
        for class_name in self.class_list:
            for section in self.section_lst[class_name]:
                for day in self.day_list:
                    for period in self.all_periods_dict[day]:
                       
                        # Constraint to ensure a teacher teaches only one class per period
                        self.model.addConstr(   
                            gp.quicksum(
                                self.assignment[class_name,section, subject, teacher_names,  day, period,classes]
                                for (cls,sec, subject, teacher_names) in self.class_subject_teacher_tuples
                                for classes in self.classrooms_list
                                if cls==class_name and section == sec and (class_name,section,subject) not in self.electives
                                    ) <= 1,f"OneSubjectPerPeriod_{class_name}_{day}_{period}"
                        )

        # 4. Ensure unique classrooms for each subject in a period
        for classroom in self.classrooms_list:
            for day in self.day_list:
                for period in self.all_periods_dict[day]:
                    self.model.addConstr(
                        gp.quicksum(
                            self.assignment[class_name, section, subject, teacher_name, day, period, classroom]
                            for class_name, section, subject, teacher_name in self.class_subject_teacher_tuples
                        ) <= 1,
                        name=f"UniqueClassroom_{class_name}_{section}_{subject}_{day}_{period}"
                    )

        # 5  Subjects in the Same Elective Group Are assigned in the Same Period
        for class_name in self.class_list:
            if class_name in self.elective_groups.keys():  
                for subject_group in self.elective_groups[class_name]:
                    #print(subject_group)
                    for day in self.day_list:
                        for period in self.all_periods_dict[day]:
                            for classes in self.classrooms_list:
                            
                                # Ensure all subjects in the group are assigned to the same period
                                group_len = len(subject_group)
                                self.model.addConstr(
                                    gp.quicksum(
                                        self.assignment[class_name,section, subject, teacher_name, day, period,classes]
                                        for subject in subject_group
                                        for _,section, subj, teacher_name in self.class_subject_teacher_tuples
                                        if subj == subject and class_name == _
                                    ) <= group_len,name=f"ElectiveGroupSamePeriod_{class_name}_{section}_{day}_{period}"
                                )
        
        #6 Constraint for ensuring all subjects in the group are assigned to the same period
        for (class_name, section), subjects_groups in self.elective_groups.items():
            for subject_group in subjects_groups:
                for i, subj1 in enumerate(subject_group):
                    for j in range(i + 1, len(subject_group)):
                        subj2 = subject_group[j]
                        teacher1 = self.class_subject_dict[class_name][section][subj1][0]
                        teacher2 = self.class_subject_dict[class_name][section][subj2][0]

                        for day in self.day_list:
                            for period in self.all_periods_dict[day]:
                                # Constraint to ensure the subjects are in the same period
                                self.model.addConstr(
                                    gp.quicksum(
                                        self.assignment[class_name, section, subj1, teacher1, day, period, classroom]
                                        for classroom in self.classrooms_list
                                    ) ==
                                    gp.quicksum(
                                        self.assignment[class_name, section, subj2, teacher2, day, period, classroom]
                                        for classroom in self.classrooms_list
                                    ),name=f"ElectiveSubjectsSamePeriod_{class_name}_{section}_{subj1}_{subj2}_{day}_{period}"
                                )

                                # Constraint to ensure the subjects are in different classrooms
                                for classroom1 in self.classrooms_list:
                                    for classroom2 in self.classrooms_list:
                                        if classroom1== classroom2:
                                            self.model.addConstr(
                                                self.assignment[class_name, section, subj1, teacher1, day, period, classroom1] +
                                                self.assignment[class_name, section, subj2, teacher2, day, period, classroom2]
                                                <= 1,name=f"DifferentClassrooms_{class_name}_{section}_{subj1}_{subj2}_{day}_{period}"
                                            )

            
           
        # 7. Requirement constraint for classes 
        for class_name, section, subject, teacher_name in self.class_subject_teacher_tuples:
            req = self.class_subject_dict[class_name][section][subject][2]
            
            # Get the priority classroom if specified
            priority_classroom = self.classroom_priority.get((class_name, section, subject))
            
            if priority_classroom:  # If a priority classroom is specified
                self.model.addConstr(
                    gp.quicksum(
                        self.assignment[class_name, section, subject, teacher_name, day, periods, priority_classroom]
                        for day in self.day_list
                        for periods in self.all_periods_dict[day]
                    ) <= req, name=f"PriorityClassroom_{class_name}_{section}_{subject}_{teacher_name}"
                )
                self.model.addConstr(
                    gp.quicksum(
                        self.assignment[class_name, section, subject, teacher_name, day, periods,classes ]
                        for day in self.day_list
                        for periods in self.all_periods_dict[day]
                        for classes in self.classrooms_list 
                        if classes != priority_classroom
                    ) ==0,name=f"NoOtherClassroom_{class_name}_{section}_{subject}_{teacher_name}"
                )
                
            else:
                # If no priority classroom is specified, add the general constraint
                self.model.addConstr(
                    gp.quicksum(
                        self.assignment[class_name, section, subject, teacher_name, day, periods, classes]
                        for day in self.day_list
                        for periods in self.all_periods_dict[day]
                        for classes in self.classrooms_list
                    ) <= req,f"GeneralClassroomRequirement_{class_name}_{section}_{subject}_{teacher_name}"
               )
            primary_teacher = self.class_subject_dict[class_name][section][subject][0]
            secondary_teachers = self.class_subject_dict[class_name][section][subject][1]
            
            if not pd.isna(secondary_teachers):
                self.model.addConstr(
                            gp.quicksum(
                                self.assignment[class_name, section, subject, primary_teacher, day, period, classes] +
                                self.assignment[class_name, section, subject, secondary_teacher, day, period, classes]
                                for secondary_teacher in secondary_teachers
                                for day in self.day_list
                                for period in self.all_periods_dict[day]
                                for classes in self.classrooms_list
                                if len(secondary_teachers)>0
                            ) <= req,
                            name=f"TotalAssignments_{class_name}_{section}_{subject}_{day}_{period}"
                        )
                
        

       
         # 8. Assign classrooms with capacity >= class strength
        for class_name, section, subject, teacher_name in self.class_subject_teacher_tuples:
            class_capacity = self.class_strength[(class_name, section)]
            for day in self.day_list:
                for period in self.all_periods_dict[day]:
                    for classroom in self.classrooms_list:
                        self.model.addConstr(
                            self.assignment[(class_name, section, subject, teacher_name, day, period, classroom)] <=
                            (self.classroom_capacity_dict[classroom] >= class_capacity)
                        )
       
        

        # 9 Workload constraints
        self.workload = {teacher: self.model.addVar(name=f'workload_{teacher}') for teacher in self.teachers_list}
        for teacher_name in self.teachers_list:
            self.model.addConstr(
                self.workload[teacher_name] == gp.quicksum(
                    self.assignment[class_name,section, subject, teacher, day, period,classes]
                    for (class_name,section, subject,  teacher) in self.class_subject_teacher_tuples
                    if teacher==teacher_name
                    for day in self.day_list
                    for period in self.all_periods_dict[day]
                    for classes in self.classrooms_list
                )
            )
            self.model.addConstr(self.workload[teacher_name] >= self.min_workload[teacher_name],name=f"MinWorkload_{teacher_name}")

            self.model.addConstr(self.workload[teacher_name] <= self.max_workload[teacher_name],name=f"MaxWorkload_{teacher_name}")

        # 10. Assignment Constraint with Penalty
        for class_name, section, subject, teacher_name in self.class_subject_teacher_tuples:
            for day in self.day_list:
                self.model.addConstr(
                    gp.quicksum(
                        self.assignment[class_name, section, subject, teacher_name, day, period, classroom]
                        for period in self.all_periods_dict[day]
                        for classroom in self.classrooms_list
                    ) <= 1 + self.penalty[class_name, section, subject, teacher_name, day],
                    name=f"SingleAssignmentPerDay_{class_name}_{section}_{subject}_{teacher_name}_{day}"
                )
############################################################# Objective function ##############################################################             
    def objective_function(self):
            self.model.setObjective(
            100 * gp.quicksum(
                self.assignment[class_name, section,subject,teach, day, period, classroom]
                for class_name, section,subject, teach in self.class_subject_teacher_tuples
                for day in self.day_list
                for period in self.all_periods_dict[day]
                for classroom in self.classrooms_list
            )
            - gp.quicksum(
                self.penalty[class_name, section,subject,teach, day]
                for class_name, section,subject, teach in self.class_subject_teacher_tuples
                for day in self.day_list
            )
            - gp.quicksum(
                self.assignment[class_name, section,subject,teach, day, period, classroom]
                for class_name, section,subject, teach in self.class_subject_teacher_tuples
                for day in self.day_list
                for period in self.all_periods_dict[day]
                for classroom in self.classrooms_list
                if teach in self.class_subject_dict[class_name][section][subject][1] 
            ),
            sense=GRB.MAXIMIZE
        )



