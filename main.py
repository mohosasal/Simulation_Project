import numpy as np
from enum import Enum
import random


###########################################################################
#  Simulation Project Autumn 2023                                         #
#  MohammadHosein Salimi (99101738)   MohammadReza Shapoori()             #
#  Dr Bardia Safaee                                                       #
###########################################################################


#####################   Define Enums  #####################

class Service(Enum):
    CONTRACT_SET = 1
    COMPLAINT_SET = 2
    DOCS_APPROVE = 3
    BACHELOR_REQUEST = 4
    REVISE_REQUEST = 5


class Policy_Type(Enum):
    SPT = 1
    FIFO = 2
    SIRO = 3


class Employee_Type(Enum):
    A = 5
    B = 7
    C = 10


class Event(Enum):
    ARRIVAL = 1
    CHANGE_EMPLOYEE_SERVICE_TYPE = 2
    DEPARTURE = 3
    Service = 4

    ####################  Define Queue Classes  #################


class Self_Q:

    def __init__(self, policy_type, service_type):
        self.policy_type = policy_type
        self.service_type = service_type
        self.list = []
        self.EmployeeList = []

    # called when arrival time of some customer comes
    def put(self, customer):
        self.list.append(customer)

    # this has to be called when some employee in that queue is idle
    def pop(self):

        if self.policy_type == Policy_Type.FIFO:
            return self.list.pop(0)
        elif self.policy_type == Policy_Type.SIRO:
            return self.list.pop(random.randrange(0, len(self.list)))

        else:
            min_index = self.list.index(min(self.list, key=lambda x: x.service_time_))
            return self.list.pop(min_index)


class Q_Manager:

    def __init__(self):
        # define queues

        self.all_queues = dict()

        self.all_queues[Service.CONTRACT_SET] = Self_Q(Policy_Type.SPT, Service.CONTRACT_SET)

        self.all_queues[Service.COMPLAINT_SET] = Self_Q(Policy_Type.FIFO, Service.COMPLAINT_SET)

        self.all_queues[Service.BACHELOR_REQUEST] = Self_Q(Policy_Type.SPT, Service.BACHELOR_REQUEST)

        self.all_queues[Service.REVISE_REQUEST] = Self_Q(Policy_Type.SIRO, Service.REVISE_REQUEST)

        self.all_queues[Service.DOCS_APPROVE] = Self_Q(Policy_Type.FIFO, Service.DOCS_APPROVE)

        # define employee lists for each queue

        self.employees_in_charge_of_queue = {

            Service.CONTRACT_SET: [],
            Service.COMPLAINT_SET: [],
            Service.DOCS_APPROVE: [],
            Service.BACHELOR_REQUEST: [],
            Service.REVISE_REQUEST: []
        }

    def assign_customer_to_queue(self, customer):
        dest = customer.service_type_required.value()
        self.all_queues[dest].append(customer)

    def check_queues_are_not_empty(self):
        for key, value in self.all_queues.items():
            if len(value.list) > 0: return True
        return False

        ###################### Define Employee and Customer ######################


class Employee:
    all_employees = []
    id = 0

    def __init__(self, type, queue_to_serve, queue_manager):

        self.type = type
        self.Queue_to_serve = queue_to_serve
        self.busy = False
        self.service_remaining_time = 0
        self.customer = None
        self.change_type_remaining_time = type.value
        # self.service_time_list = dict()
        self.queue_manager = queue_manager
        self.queue_manager.employees_in_charge_of_queue[queue_to_serve].append(self)
        Employee.all_employees.append(self)
        self.id = Employee.id
        Employee.id += 1

    def update_service_remaining_time(self, x):
        self.service_remaining_time = self.service_remaining_time + x

    def update_change_type_remaining_time(self, x):
        self.change_type_remaining_time = self.change_type_remaining_time + x

    def add_customer(self, customer):

        self.customer = customer
        self.busy = True
        self.service_remaining_time = customer.service_time_

    def remove_customer(self):

        x = self.customer
        self.customer = None
        self.busy = False
        self.service_remaining_time = 0
        return x

    # based on A B C ... we have to call this to change the service type of employee
    def Queue_type_specifier(self):

        rand = np.random.uniform(0, 1)
        last_queue = self.Queue_to_serve

        if self.type == Employee_Type.A:
            if self.Queue_to_serve == Service.CONTRACT_SET:
                if rand <= 0.2:
                    self.Queue_to_serve = Service.COMPLAINT_SET
            if self.Queue_to_serve == Service.COMPLAINT_SET:
                if rand < 0.1:
                    self.Queue_to_serve = Service.CONTRACT_SET

        elif self.type == Employee_Type.B:
            if self.Queue_to_serve == Service.BACHELOR_REQUEST:
                if rand <= 0.15:
                    self.Queue_to_serve = Service.REVISE_REQUEST
            if self.Queue_to_serve == Service.REVISE_REQUEST:
                if rand < 0.05:
                    self.Queue_to_serve = Service.BACHELOR_REQUEST

        else:
            if self.Queue_to_serve == Service.BACHELOR_REQUEST:
                if rand <= 0.1:
                    self.Queue_to_serve = Service.REVISE_REQUEST
                elif rand <= 0.2:
                    self.Queue_to_serve = Service.DOCS_APPROVE

            if self.Queue_to_serve == Service.REVISE_REQUEST:
                if rand < 0.15:
                    self.Queue_to_serve = Service.BACHELOR_REQUEST
                elif rand < 0.25:
                    self.Queue_to_serve = Service.DOCS_APPROVE

            if self.Queue_to_serve == Service.DOCS_APPROVE:
                if rand < 0.05:
                    self.Queue_to_serve = Service.BACHELOR_REQUEST
                elif rand < 0.1:
                    self.Queue_to_serve = Service.REVISE_REQUEST

        self.change_type_remaining_time = self.type.value
        self.change_employee_queue(last_queue)
        return (last_queue != self.Queue_to_serve)

    # has to be called when some emplyee changes queue to server

    def change_employee_queue(self, last_queue):
        index = self.queue_manager.employees_in_charge_of_queue[last_queue].index(self)
        self.queue_manager.employees_in_charge_of_queue[last_queue].pop(index)
        self.queue_manager.employees_in_charge_of_queue[self.Queue_to_serve].append(self)


class Customer:
    all_customers = []
    finished_customers = []
    id = 0

    # do we need other properties like end service , queue num and ... ?
    def __init__(self, service_type_required):
        self.service_type_required = service_type_required
        self.arrival_time = 0
        self.service_applier()
        self.service_time_ = self.service_time()[0]
        Customer.all_customers.append(self)
        self.id = Customer.id
        Customer.id += 1

        self.system_enter_time = 0
        self.system_exit_time = 0

        self.service_time_spent = 0

    def update_system_time_spent(self, service_time):
        self.service_time_spent += service_time

    def service_applier(self):

        if self.service_type_required == Service.CONTRACT_SET:
            self.arrival_time = np.random.normal(loc=40, scale=6, size=1)

        elif self.service_type_required == Service.COMPLAINT_SET:
            self.arrival_time = np.random.exponential(scale=1 / 0.5, size=1)

        elif self.service_type_required == Service.DOCS_APPROVE:
            self.arrival_time = np.random.gamma(shape=1, scale=1 / 2, size=1)

        elif self.service_type_required == Service.BACHELOR_REQUEST:
            self.arrival_time = np.random.exponential(scale=1 / 0.06, size=1)

        elif self.service_type_required == Service.REVISE_REQUEST:
            self.arrival_time = np.random.normal(loc=15, scale=6, size=1)

    # when the arrival time comes,we have to call this function
    @staticmethod
    def send_next_customer():
        return Customer.all_customers.pop()

    def service_time(self):

        if self.service_type_required == Service.CONTRACT_SET:
            return np.random.exponential(scale=30, size=1)

        elif self.service_type_required == Service.COMPLAINT_SET:
            return np.random.exponential(scale=25, size=1)

        elif self.service_type_required == Service.DOCS_APPROVE:
            return np.random.exponential(scale=10, size=1)

        elif self.service_type_required == Service.BACHELOR_REQUEST:
            return np.random.exponential(scale=5, size=1)

        elif self.service_type_required == Service.REVISE_REQUEST:
            return np.random.exponential(scale=10, size=1)

    # call this at the begging of the simulation
    @staticmethod
    def generate_customers(num):

        for i in range(num):
            random_service = random.choice(list(Service))
            x = Customer(random_service)

            ######################## Statistics Class ###########################


class Statistics:
    inter_arrivals = []
    system_times = []
    service_times = []
    queue_times = []
    customer_in_system_at_t = []
    customer_in_queue_at_t = []
    mean_system_times = 0
    mean_queue_times = 0
    mean_customer_in_system_at_t = 0
    mean_customer_in_queue_at_t = 0
    log = ""

    @staticmethod
    def set_statictical_lists(customers_list):
        for i in customers_list:
            Statistics.inter_arrivals.append(i.arrival_time)
            sys_time = i.system_exit_time - i.system_enter_time
            Statistics.system_times.append(sys_time)
            Statistics.queue_times.append(sys_time - i.service_time_)
            Statistics.service_times.append(i.service_time_)

    @staticmethod
    def set_statistical_means():

        Statistics.mean_system_times = sum(Statistics.system_times) / len(Statistics.system_times)
        Statistics.mean_queue_times = sum(Statistics.queue_times) / len(Statistics.queue_times)


        sys_at_sum = 0
        for i in range(len(Statistics.customer_in_system_at_t) - 1):
            if i > 0: sys_at_sum += Statistics.customer_in_system_at_t[i][1] * (
                        Statistics.customer_in_system_at_t[i][0] - Statistics.customer_in_system_at_t[i - 1][0])
        Statistics.mean_customer_in_system_at_t = sys_at_sum / Statistics.customer_in_system_at_t[
            len(Statistics.customer_in_system_at_t) - 1][0]

        que_at_sum = 0
        for i in range(len(Statistics.customer_in_queue_at_t)-1):
           if i >0 : que_at_sum += Statistics.customer_in_queue_at_t[i][1] *(Statistics.customer_in_queue_at_t[i][0]- Statistics.customer_in_queue_at_t[i-1][0])
        Statistics.mean_customer_in_queue_at_t = que_at_sum / Statistics.customer_in_queue_at_t[
            len(Statistics.customer_in_queue_at_t) - 1][0]

        ######################### Run the Simulation ###############################


########### initial objects

# queues
queue_box = Q_Manager()

# Employees ( has to be modified)

Employee(Employee_Type.A, Service.COMPLAINT_SET, queue_box)
#Employee(Employee_Type.B, Service.COMPLAINT_SET, queue_box)

Employee(Employee_Type.B, Service.CONTRACT_SET, queue_box)
#Employee(Employee_Type.C, Service.CONTRACT_SET, queue_box)

Employee(Employee_Type.C, Service.DOCS_APPROVE, queue_box)
#Employee(Employee_Type.A, Service.DOCS_APPROVE, queue_box)

Employee(Employee_Type.A, Service.BACHELOR_REQUEST, queue_box)
#Employee(Employee_Type.B, Service.BACHELOR_REQUEST, queue_box)

Employee(Employee_Type.B, Service.REVISE_REQUEST, queue_box)
#Employee(Employee_Type.C, Service.REVISE_REQUEST, queue_box)

employee_to_serve = None

# Customers
initial_number_of_customers = 500
Customer.generate_customers(initial_number_of_customers)

################# initialize statistical variables

# clock things
clock = 0
max_clock = 10000
# remaining time shits
next_customer_arrival_time = Customer.all_customers[len(Customer.all_customers) - 1].arrival_time
next_employee_queue_change = [0, 0]
next_employee_departure = [0, 0]
next_employee_service = float('inf')

min_index = Employee.all_employees.index(min(Employee.all_employees, key=lambda x: x.change_type_remaining_time))
next_employee_queue_change = [min_index, Employee.all_employees[min_index].change_type_remaining_time]
min_index = Employee.all_employees.index(min(Employee.all_employees, key=lambda x: x.service_remaining_time))
next_employee_departure = [min_index, Employee.all_employees[min_index].service_remaining_time]

# set the next times


# event
event = Event.ARRIVAL

#################################################### run the simulation

while (clock < max_clock):

    ##################### event management

    if event == Event.ARRIVAL:

        # pop the customer and send to queue
        new_customer = Customer.send_next_customer()
        new_customer.system_enter_time = clock
        queue_box.all_queues[new_customer.service_type_required].put(new_customer)
        # log
        Statistics.log = Statistics.log + f"--> Arrival event <--  customer {new_customer.id} is going into queue {new_customer.service_type_required} at {clock} min \n"



    elif event == Event.CHANGE_EMPLOYEE_SERVICE_TYPE:
        # change the employee state and send the customer back
        changed_queue = Employee.all_employees[next_employee_queue_change[0]].Queue_type_specifier()
        if changed_queue:
            if Employee.all_employees[next_employee_queue_change[0]].busy:

                Employee.all_employees[next_employee_queue_change[0]].customer.update_system_time_spent(
                    (Employee.all_employees[next_employee_queue_change[0]].customer.service_time_ -
                     Employee.all_employees[
                         next_employee_queue_change[
                             0]].service_remaining_time))

                if Employee.all_employees[next_employee_queue_change[0]].service_remaining_time != 0:
                    the_customer = Employee.all_employees[next_employee_queue_change[0]].remove_customer()
                    # change the customer attribute for ending service
                    queue_box.all_queues[the_customer.service_type_required].put(the_customer)
                    Statistics.log = Statistics.log + f"--> Change employee queue event <-- employee {Employee.all_employees[next_employee_queue_change[0]].id} is going into the {Employee.all_employees[next_employee_queue_change[0]].Queue_to_serve} queue and the customer {the_customer.id} is going back to the {the_customer.service_type_required} queue at {clock} min \n"

                else:
                    the_customer.system_exit_time = clock
                    Customer.finished_customers.append(the_customer)

                    Statistics.log = Statistics.log + f"--> Change employee queue event <-- employee {Employee.all_employees[next_employee_queue_change[0]].id} is going into queue {Employee.all_employees[next_employee_queue_change[0]].Queue_to_serve} but released the customer finished at {clock} min \n"

            else:
                Statistics.log = Statistics.log + f"--> Change employee queue event <-- employee {Employee.all_employees[next_employee_queue_change[0]].id} s going into queue {Employee.all_employees[next_employee_queue_change[0]].Queue_to_serve} while idle at {clock} min\n"


        else:

            Statistics.log = Statistics.log + f"--> Change employee queue event <-- employee {Employee.all_employees[next_employee_queue_change[0]].id} stays in the previous queue at {clock} min\n"





    elif event == Event.DEPARTURE:

        the_employee = Employee.all_employees[next_employee_departure[0]]
        # set the customer attributes based on departure
        the_employee.customer.system_exit_time = clock
        the_employee.customer.update_system_time_spent(the_employee.customer.service_time_)
        the_customer = the_employee.remove_customer()
        Customer.finished_customers.append(the_customer)

        Statistics.log = Statistics.log + f"--> Departure event <--the employee {the_employee.id} released the customer {the_customer.id} at {clock} min \n"

    if event == Event.Service:
        employee_to_serve.add_customer(queue_box.all_queues[employee_to_serve.Queue_to_serve].pop())
        Statistics.log = Statistics.log + f"--> Service event <-- the employee {employee_to_serve.id} is starting for customer {employee_to_serve.customer.id} from queue {employee_to_serve.Queue_to_serve} at {clock} min\n"

    ##################### event specifier

    # set the next change queue
    min_index = Employee.all_employees.index(
        min(Employee.all_employees, key=lambda x: x.change_type_remaining_time))
    next_employee_queue_change = [min_index, Employee.all_employees[min_index].change_type_remaining_time]

    # set the next departure
    busy_employees = [i for i in Employee.all_employees if i.busy]
    if len(busy_employees) > 0:
        min_index = Employee.all_employees.index(min(busy_employees, key=lambda x: x.service_remaining_time))
        next_employee_departure = [min_index, Employee.all_employees[min_index].service_remaining_time]
    else:
        next_employee_departure = [0, float('inf')]

    # set the next service
    next_employee_service = float('inf')
    if queue_box.check_queues_are_not_empty():
        idles = [i for i in Employee.all_employees if i.busy == False]
        for i in idles:
            if len(queue_box.all_queues[i.Queue_to_serve].list) > 0:
                next_employee_service = 0
                employee_to_serve = i
                break

    # set the next arrival
    if len(Customer.all_customers) > 0:
        next_customer_arrival_time = Customer.all_customers[len(Customer.all_customers) - 1].arrival_time
    else:
        next_customer_arrival_time = float('inf')

    ######## check for event

    # arrival event

    if next_customer_arrival_time <= next_employee_departure[1] and next_customer_arrival_time <= \
            next_employee_queue_change[1] and next_customer_arrival_time <= next_employee_service:

        event = Event.ARRIVAL
        clock = clock + next_customer_arrival_time
        # update clock and objects timings
        # Customer.all_customers[len(Customer.all_customers) - 1].arrival_time = 0
        for i in range(len(Employee.all_employees) - 1):
            # update departure remaining times
            Employee.all_employees[i].update_change_type_remaining_time(-1 * next_customer_arrival_time)
            if Employee.all_employees[i].busy: Employee.all_employees[i].update_service_remaining_time(
                -1 * next_customer_arrival_time)
    # departure event

    elif next_employee_departure[1] <= next_employee_queue_change[1] and next_employee_departure[
        1] <= next_customer_arrival_time and next_employee_departure[1] <= next_employee_service:

        event = Event.DEPARTURE
        clock += Employee.all_employees[next_employee_departure[0]].service_remaining_time
        # update timings
        if len(Customer.all_customers) > 0:  Customer.all_customers[len(Customer.all_customers) - 1].arrival_time -= \
            Employee.all_employees[
                next_employee_departure[0]].service_remaining_time
        for i in range(len(Employee.all_employees) - 1):
            # update departure remaining times
            Employee.all_employees[i].update_change_type_remaining_time(-1 * next_employee_departure[1])
            if Employee.all_employees[i].busy: Employee.all_employees[i].update_service_remaining_time(
                -1 * next_employee_departure[1])

    # queue change event

    elif next_employee_queue_change[1] <= next_employee_departure[1] and next_employee_queue_change[
        1] <= next_customer_arrival_time and next_employee_queue_change[1] <= next_employee_service:

        # change queue event
        event = Event.CHANGE_EMPLOYEE_SERVICE_TYPE
        clock += Employee.all_employees[next_employee_queue_change[0]].change_type_remaining_time

        # update timings
        if len(Customer.all_customers) > 0: Customer.all_customers[len(Customer.all_customers) - 1].arrival_time -= \
            Employee.all_employees[next_employee_queue_change[0]].change_type_remaining_time
        for i in range(len(Employee.all_employees) - 1):
            # update departure remaining times
            Employee.all_employees[i].update_change_type_remaining_time(-1 * next_employee_queue_change[1])
            if Employee.all_employees[i].busy: Employee.all_employees[i].update_service_remaining_time(
                -1 * next_employee_queue_change[1])

    # service event
    else:
        event = Event.Service
        # the server to serice the customer is defined in the timings!

    at_system = initial_number_of_customers - len(Customer.all_customers) - len(Customer.finished_customers)
    at_clock = 0
    if type(clock) == int:
        at_clock = clock
    elif type(clock) == np.ndarray:
        at_clock = clock.flat[0]

    if len(Statistics.customer_in_system_at_t) > 0:
        if Statistics.customer_in_system_at_t[len(Statistics.customer_in_system_at_t) - 1][0] != at_clock:
            Statistics.customer_in_system_at_t.append([at_clock, at_system])
            Statistics.customer_in_queue_at_t.append([at_clock, at_system - len(busy_employees)])
    else:
        Statistics.customer_in_system_at_t.append([at_clock, at_system])
        Statistics.customer_in_queue_at_t.append([at_clock, at_system - len(busy_employees)])

################################################### statistical things!

# set final statistics

Statistics.set_statictical_lists(Customer.finished_customers)
Statistics.set_statistical_means()

# save the logs in the file
with open("log.txt", "w") as f:
    f.write(Statistics.log)

f.close()

# print the statistical variables and figures

print(f"mean of W : {Statistics.mean_system_times}")
print(f"mean of W_q : {Statistics.mean_queue_times}")
print(f"mean of L_t : {Statistics.mean_customer_in_system_at_t}")
print(f"mean of L_q_t : {Statistics.mean_customer_in_queue_at_t}")

# print the figures based on the lists of the Statistics class


################################################### the end

############ with one employee , we got the resaults below :

# mean of W : 379
# mean of W_q : 363
# mean of L_t : 23.2
# mean of L_q_t : 19.6

############ with two employee of different types for each queue, we got the resaults below :
# mean of W : 28.6
# mean of W_q : 14
# mean of L_t : 2,1
# mean of L_q_t : 0.2
