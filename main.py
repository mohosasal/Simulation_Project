from enum import Enum

import numpy as np
import numpy as np
from enum import Enum
from random import random

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
            return self.list.pop(random.randint(0, len(self.list) - 1))
        else:
            min_index = self.list.index(min(self.list, key=lambda x: x.service_time_))
            return self.list.pop(min_index)



class Q_Manager:

    def __init__(self):
        # define queues

        self.all_queues = dict()

        self.all_queues[Service.CONTRACT_SET] = Self_Q(Policy_Type.SPT, Service.CONTRACT_SET)
        self.all_queues[Service.COMPLAINT_SET] = Self_Q(Policy_Type.FIFO, Service.COMPLAINT_SET)
        self.all_queues[Service.DOCS_APPROVE] = Self_Q(Policy_Type.FIFO, Service.DOCS_APPROVE)
        self.all_queues[Service.BACHELOR_REQUEST] = Self_Q(Policy_Type.SPT, Service.BACHELOR_REQUEST)
        self.all_queues[Service.REVISE_REQUEST] = Self_Q(Policy_Type.SIRO, Service.REVISE_REQUEST)

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
            if len(value.list) >0 : return True
        return False

class Type(Enum):
    A = 5
    B = 7
    C = 10


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
        #self.service_time_list = dict()
        self.queue_manager = queue_manager
        self.queue_manager.employees_in_charge_of_queue[queue_to_serve].append(self)
        Employee.all_employees.append(self)
        self.id = Employee.id
        Employee.id += 1

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

        if self.type == Type.A:
            if self.Queue_to_serve == Service.CONTRACT_SET:
                if rand <= 0.2:
                    self.Queue_to_serve = Service.COMPLAINT_SET
            if self.Queue_to_serve == Service.COMPLAINT_SET:
                if rand < 0.1:
                    self.Queue_to_serve = Service.CONTRACT_SET

        elif self.type == Type.B:
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
        return (last_queue == self.Queue_to_serve)

    # has to be called when some emplyee changes queue to server

    def change_employee_queue(self, last_queue):
        index = self.queue_manager.employees_in_charge_of_queue[last_queue].index(self)
        self.queue_manager.employees_in_charge_of_queue[last_queue].pop(index)
        self.queue_manager.employees_in_charge_of_queue[self.Queue_to_serve].append(self)



class Customer:
    all_customers = []
    id = 0

    # do we need other properties like end service , queue num and ... ?
    def __init__(self, service_type_required):
        self.service_type_required = service_type_required
        self.arrival_time = 0
        self.service_applier()
        self.service_time_ = self.service_time()
        Customer.all_customers.append(self)
        self.id = Customer.id
        Customer.id += 1

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
        for i in range(num // 5):
            x = Customer(Service.REVISE_REQUEST)
        for i in range(num // 5):
            x = Customer(Service.BACHELOR_REQUEST)
        for i in range(num // 5):
            x = Customer(Service.DOCS_APPROVE)
        for i in range(num // 5):
            x = Customer(Service.CONTRACT_SET)
        for i in range(num // 5):
            x = Customer(Service.COMPLAINT_SET)

class Event(Enum):
    ARRIVAL = 1
    CHANGE_EMPLOYEE_SERVICE_TYPE = 2
    DEPARTURE = 3



################################################### initialize objects

# queues
queue_box = Q_Manager()

# Employees ( has to be modified)
Employee(Type.A, Service.COMPLAINT_SET, queue_box)
Employee(Type.B, Service.CONTRACT_SET, queue_box)
Employee(Type.C, Service.DOCS_APPROVE, queue_box)
Employee(Type.A, Service.BACHELOR_REQUEST, queue_box)
Employee(Type.B, Service.REVISE_REQUEST, queue_box)
Employee(Type.C, Service.BACHELOR_REQUEST, queue_box)

# Customers
Customer.generate_customers(10)

################################################### initialize statistical variables

# clock things
clock = 0
max_clock = 1000
# remaining time shits
next_customer_arrival_time = Customer.all_customers[len(Customer.all_customers) - 1].arrival_time
next_employee_queue_change = [0, 0]
next_employee_departure = [0, 0]

min_index = Employee.all_employees.index(min(Employee.all_employees, key=lambda x: x.change_type_remaining_time))
next_employee_queue_change = [min_index, Employee.all_employees[min_index].change_type_remaining_time]
min_index = Employee.all_employees.index(min(Employee.all_employees, key=lambda x: x.service_remaining_time))
next_employee_departure = [min_index, Employee.all_employees[min_index].service_remaining_time]



# event
event = Event.ARRIVAL

#################################################### run the simulation

while (clock < max_clock):

##################### event management

    if event == Event.ARRIVAL:

        # pop the customer and send to queue
        new_customer = Customer.send_next_customer()
        queue_box.all_queues[new_customer.service_type_required].put(new_customer)
        # log
        print(
                f"Arrival event : customer {new_customer.id} goes into queue {new_customer.service_type_required} at {clock}")



    elif event == Event.CHANGE_EMPLOYEE_SERVICE_TYPE:
        # change the employee state and send the customer back
        changed_queue = Employee.all_employees[next_employee_queue_change[0]].Queue_type_specifier()
        if changed_queue:
            if Employee.all_employees[next_employee_queue_change[0]].busy:
                the_customer = Employee.all_employees[next_employee_queue_change[0]].remove_customer
                if Employee.all_employees[next_employee_queue_change[0]].service_remaining_time != 0:
                    # change the customer attribute for ending service
                    queue_box.all_queues[the_customer.service_type_required].put(the_customer)
                    print(
                        f"Chagne employee queue event : employee {Employee.all_employees[next_employee_queue_change[0]].id} goes in"
                        f" the {Employee.all_employees[next_employee_queue_change[0]].Queue_to_serve} queue and the customer {the_customer.id} "
                        f" goes back to the {the_customer.service_type_required} queue at {clock}")



        else:
            print(
                f"Chagne employee queue event : employee {Employee.all_employees[next_employee_queue_change[0]].id} stays in"
                f" the previous queue at {clock}")
            continue



    elif event == Event.DEPARTURE:
        the_employee = Employee.all_employees[next_employee_departure[0]]
        # set the customer attributes based on departure
        the_employee.remove_customer()
        if queue_box.check_queues_are_not_empty():
            #  select from teh derver list of that queue
            # we have to check all the idle servers
            idles= [i for i in Employee.all_employees if i.busy==False]
            ma_man=None
            for i in idles :
                if len(queue_box.all_queues[i.Queue_to_serve].list) > 0:
                    ma_man = i
                    break

            if ma_man != None:
                ma_man.add_customer(queue_box.all_queues[ma_man.Queue_to_serve].pop())
                print(f"the emplyoee {ma_man.id}   "
              f"is starting for customer {ma_man.customer.id} from queue {ma_man.Queue_to_serve} at {clock}")
            #only departure
        else :
            print(f"the emplyoee {the_employee.id} released the  previous customer at {clock}")

    ##################### event specifier

    min_index = Employee.all_employees.index(
        min(Employee.all_employees, key=lambda x: x.change_type_remaining_time))
    next_employee_queue_change = [min_index, Employee.all_employees[min_index].change_type_remaining_time]

    # pure the list of employees  ( dont choose idle servers if q is empty )

    if queue_box.check_queues_are_not_empty():
        min_index = Employee.all_employees.index(min(Employee.all_employees, key=lambda x: x.service_remaining_time))
        next_employee_departure = [min_index, Employee.all_employees[min_index].service_remaining_time]
    else :
        busy_employees = filter(lambda x: x.busy, Employee.all_employees)
        # Find the index of the employee with the minimum service remaining time among the busy employees
        min_index = Employee.all_employees.index(min(busy_employees, key=lambda x: x.service_remaining_time))
        # Create a list with the index and the service remaining time
        next_employee_departure = [min_index, Employee.all_employees[min_index].service_remaining_time]



    #


    # what if list is empty?
    if len(Customer.all_customers) >0 :next_customer_arrival_time = Customer.all_customers[len(Customer.all_customers) - 1].arrival_time
    else : next_customer_arrival_time=float('inf')

    # check for event

    if next_customer_arrival_time <= next_employee_departure[1]:
        if next_customer_arrival_time <= next_employee_queue_change[1]:
            # arrival event
            event = Event.ARRIVAL
            clock = clock + next_customer_arrival_time
            # update clock and objects timings
            Customer.all_customers[len(Customer.all_customers) - 1].arrival_time = 0
            for i in Employee.all_employees:
                # update departure remaining times
                i.change_type_remaining_time -= next_customer_arrival_time
                if i.busy : i.service_remaining_time -= next_customer_arrival_time

    if next_employee_departure[1] <= next_employee_queue_change[1]:
        if next_employee_departure[1] <= next_customer_arrival_time:
            # departure event
            event = Event.DEPARTURE
            clock += Employee.all_employees[next_employee_departure[0]].service_remaining_time
            # update timings
            Customer.all_customers[len(Customer.all_customers) - 1].arrival_time -= Employee.all_employees[
                next_employee_departure[0]].service_remaining_time
            for i in Employee.all_employees:
                # update departure remaining times
                i.change_type_remaining_time -= Employee.all_employees[
                    next_employee_departure[0]].service_remaining_time
                if i.busy: i.service_remaining_time -= Employee.all_employees[next_employee_departure[0]].service_remaining_time

    if next_employee_queue_change[1] <= next_employee_departure[1]:
        if next_employee_queue_change[1] <= next_customer_arrival_time:
            # change queue event
            event = Event.CHANGE_EMPLOYEE_SERVICE_TYPE
            clock += Employee.all_employees[next_employee_queue_change[0]].change_type_remaining_time

            # update timings
            if len(Customer.all_customers) > 0: Customer.all_customers[len(Customer.all_customers) - 1].arrival_time -= Employee.all_employees[next_employee_queue_change[0]].change_type_remaining_time
            for i in Employee.all_employees:
            # update departure remaining times
                i.change_type_remaining_time -= Employee.all_employees[
                next_employee_queue_change[0]].change_type_remaining_time
                if i.busy: i.service_remaining_time -= Employee.all_employees[
                next_employee_queue_change[0]].change_type_remaining_time

################################################### statistical things!

# will implement soon!

################################################### the end
